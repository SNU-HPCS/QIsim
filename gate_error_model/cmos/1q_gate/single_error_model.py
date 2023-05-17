import numpy as np
from math import frexp
from qiskit.pulse.library import Waveform, Constant
from qutip import *
from scipy.signal import cheby1, freqs
from scipy import interpolate
import ray, json, csv, warnings, argparse
warnings.filterwarnings(action='ignore')


# Applying bit-precision error
def round_pow2 (val, prec, V0):
    V_step = 2 * V0 / (2**prec - 1)
    trun = val + V0
    if (trun % V_step) < V_step / 2:
        trun = int(trun / V_step) * V_step
    else:
        trun = (int(trun / V_step) + 1) * V_step
    trun = trun - V0
    return trun


# Emulating analog part until LO up-mixer
def emulate_drive_circuit_filter (
    device_parameters: dict, ideal_wave: Waveform, dt_ns: float, V0: float
) -> Waveform:
    # Digital circuit parameters
    device_frequency = device_parameters["device_frequency"]
    output_precision = int(device_parameters["output_precision"])
    
    # Analog circuit parameters
    filter_type = device_parameters["filter_type"] # average_filter, ideal_low_pass_filter
    if filter_type == "ideal_low_pass_filter" or filter_type == "chebyshev_LPF":
        cutoff_frequency = device_parameters["cutoff_frequency"]
    else:
        cutoff_frequency = 0
    if filter_type == "average_filter":
        filter_num_dt = device_parameters["filter_num_dt"]
    else:
        filter_num_dt = 0
      
    amplifier_type = device_parameters["amplifier_type"] # area_ratio, abs_area_ratio, no_amp
    
    ideal_wave_samples = ideal_wave.samples
    ideal_wave_samples_real = [v.real for v in ideal_wave_samples]
    ideal_wave_samples_imag = [v.imag for v in ideal_wave_samples]
    num_samples = len(ideal_wave_samples)
    
    # device_frequency
    device_period = float(1/device_frequency)
    device_period_ns = device_period * (1e9)
    num_samples_in_device_period = float(device_period_ns / dt_ns)
    
    # Calculate area of ideal sample
    if amplifier_type == "area_ratio":
        ideal_area_real = np.trapz(ideal_wave_samples_real)
        ideal_area_imag = np.trapz(ideal_wave_samples_imag)
    elif amplifier_type == "abs_area_ratio" or amplifier_type == "vga":
        ideal_area_real = np.trapz(np.abs(ideal_wave_samples_real))
        ideal_area_imag = np.trapz(np.abs(ideal_wave_samples_imag))
    else:
        ideal_area_real = 1
        ideal_area_imag = 1

    # Apply device_frequency
    if num_samples_in_device_period.is_integer():
        num_samples_in_device_period = int(num_samples_in_device_period)
        total_iteration = float(num_samples / num_samples_in_device_period)
        if total_iteration.is_integer():
            total_iteration = int(total_iteration)
        else:
            remainder = num_samples % num_samples_in_device_period
            ideal_wave_samples = np.concatenate((ideal_wave_samples, np.array([0] * (num_samples_in_device_period-remainder))))
            total_iteration = int(total_iteration) +1
        
        output_sample = [[complex(np.mean([v.real for v in ideal_wave_samples[i:i+num_samples_in_device_period]]),
                                  np.mean([v.imag for v in ideal_wave_samples[i:i+num_samples_in_device_period]])
                                  )]*num_samples_in_device_period for i in range(0,num_samples,num_samples_in_device_period)]
        output_sample = np.array(output_sample).flatten()[:num_samples]
    else:
        s_re = 0
        s_im = 0
        idx = 0
        count = 0
        output_sample = []
        for v in ideal_wave_samples:
            if idx >= num_samples_in_device_period:
                avg_re = s_re / count
                avg_im = s_im / count
                output_sample = output_sample + [complex(avg_re, avg_im)] * count
                count = 0
                s_re = 0
                s_im = 0
                idx -= num_samples_in_device_period
            else:
                pass
            
            s_re += v.real
            s_im += v.imag
            idx += 1
            count += 1
            
        avg_re = s_re / count
        avg_im = s_im / count
        output_sample = output_sample + [complex(avg_re, avg_im)] * count
        count = 0
        s_re = 0
        s_im = 0
        idx -= num_samples_in_device_period
        
        output_sample = np.array(output_sample)
                
    # Apply output precision
    digital_output_sample = np.array([complex(
        round_pow2(v.real, output_precision, V0),
        round_pow2(v.imag, output_precision, V0)) for v in output_sample])
        
    # Apply filter
    if filter_type == "average_filter":
        # Filter
        half_filter_num_dt = filter_num_dt // 2
        s_real_filtered = np.array([np.mean([v.real for v in digital_output_sample[max(0, i-half_filter_num_dt):min(num_samples-1, i-half_filter_num_dt+filter_num_dt)]]) for i in range(num_samples)])
        s_imag_filtered = np.array([np.mean([v.imag for v in digital_output_sample[max(0, i-half_filter_num_dt):min(num_samples-1, i-half_filter_num_dt+filter_num_dt)]]) for i in range(num_samples)])
        
        # Amplifier
        if amplifier_type == "area_ratio":
            s_area_filtered_real = np.trapz(s_real_filtered)
            s_area_filtered_imag = np.trapz(s_imag_filtered)
        elif amplifier_type == "abs_area_ratio" or amplifier_type == "vga":
            s_area_filtered_real = np.trapz(np.abs(s_real_filtered))
            s_area_filtered_imag = np.trapz(np.abs(s_imag_filtered))
        else:
            s_area_filtered_real = ideal_area_real
            s_area_filtered_imag = ideal_area_imag
        
        # Result
        if amplifier_type == "vga":
            analog_output_sample = np.array([complex(r*device_parameters["gain"], i*device_parameters["gain"]) for r, i in zip(s_real_filtered, s_imag_filtered)])
        else:
            analog_output_sample = np.array([complex(r/s_area_filtered_real*ideal_area_real, i/s_area_filtered_imag*ideal_area_imag) for r, i in zip(s_real_filtered, s_imag_filtered)])

    elif filter_type == "ideal_low_pass_filter":
        # Filter
        s_real = np.array([v.real for v in digital_output_sample])
        s_imag = np.array([v.imag for v in digital_output_sample])
        # s_area = np.sum(s_real) + np.sum(s_imag)
        f_real = np.fft.rfft(s_real)
        f_imag = np.fft.rfft(s_imag)
        dt = dt_ns * (1e-9)
        digital_output_sample_frequency = np.fft.rfftfreq(num_samples, dt)
        f_real_filtered = np.array([amp if np.abs(freq) <= cutoff_frequency else 0 for amp, freq in zip(f_real, digital_output_sample_frequency)])
        f_imag_filtered = np.array([amp if np.abs(freq) <= cutoff_frequency else 0 for amp, freq in zip(f_imag, digital_output_sample_frequency)])
        
        s_real_filtered = np.array([r for r in np.fft.irfft(f_real_filtered)])
        s_imag_filtered = np.array([i for i in np.fft.irfft(f_imag_filtered)])
        
        # Amplifier
        if amplifier_type == "area_ratio":
            s_area_filtered_real = np.trapz(s_real_filtered)
            s_area_filtered_imag = np.trapz(s_imag_filtered)
        elif amplifier_type == "abs_area_ratio" or amplifier_type == "vga":
            s_area_filtered_real = np.trapz(np.abs(s_real_filtered))
            s_area_filtered_imag = np.trapz(np.abs(s_imag_filtered))
        else:
            s_area_filtered_real = ideal_area_real
            s_area_filtered_imag = ideal_area_imag

        #print("Ideal low pass filtered real area : {}".format(np.trapz(np.abs(s_real_filtered))))
        #print("Ideal low pass filtered imag area : {}".format(np.trapz(np.abs(s_imag_filtered))))
            
        # Result
        if amplifier_type == "vga":
            analog_output_sample = np.array([complex(r*device_parameters["gain"], i*device_parameters["gain"]) for r, i in zip(s_real_filtered, s_imag_filtered)])
        else:
            analog_output_sample = np.array([complex(r/s_area_filtered_real*ideal_area_real, i/s_area_filtered_imag*ideal_area_imag) for r, i in zip(s_real_filtered, s_imag_filtered)])
    elif filter_type == "chebyshev_LPF":
        # Filter
        s_real = np.array([v.real for v in digital_output_sample])
        s_imag = np.array([v.imag for v in digital_output_sample])
        # s_area = np.sum(s_real) + np.sum(s_imag)
        f_real = np.fft.rfft(s_real)
        f_imag = np.fft.rfft(s_imag)
        dt = dt_ns * (1e-9)
        digital_output_sample_frequency = np.fft.rfftfreq(num_samples, dt)
        rp = 2
        b, a = cheby1(N=2, rp=rp, Wn=cutoff_frequency, btype='lowpass', analog=True, output='ba')
        w, h = freqs(b, a)
        interpolated_filter = interpolate.interp1d(np.concatenate(([digital_output_sample_frequency[0]],w,[digital_output_sample_frequency[-1]])), abs(np.concatenate(([h[0]],h,[0]))), kind="nearest")
        chebyshev_filter = interpolated_filter(digital_output_sample_frequency) * np.power(10, rp / 20)
        f_real_filtered = f_real * chebyshev_filter
        f_imag_filtered = f_imag * chebyshev_filter
        s_real_filtered = np.array([r for r in np.fft.irfft(f_real_filtered)])
        s_imag_filtered = np.array([i for i in np.fft.irfft(f_imag_filtered)])
        
        # Amplifier
        if amplifier_type == "area_ratio":
            s_area_filtered_real = np.trapz(s_real_filtered)
            s_area_filtered_imag = np.trapz(s_imag_filtered)
        elif amplifier_type == "abs_area_ratio" or amplifier_type == "vga":
            s_area_filtered_real = np.trapz(np.abs(s_real_filtered))
            s_area_filtered_imag = np.trapz(np.abs(s_imag_filtered))
        else:
            s_area_filtered_real = ideal_area_real
            s_area_filtered_imag = ideal_area_imag
            
        # Result
        if amplifier_type == "vga":
            analog_output_sample = np.array([complex(r*device_parameters["gain"], i*device_parameters["gain"]) for r, i in zip(s_real_filtered, s_imag_filtered)])
        else:
            analog_output_sample = np.array([complex(r/s_area_filtered_real*ideal_area_real, i/s_area_filtered_imag*ideal_area_imag) for r, i in zip(s_real_filtered, s_imag_filtered)])
    else:
        # Filter
        s_real_filtered = digital_output_sample.real
        s_imag_filtered = digital_output_sample.imag
        
        # Amplifier
        if amplifier_type == "area_ratio":
            s_area_filtered_real = np.trapz(s_real_filtered)
            s_area_filtered_imag = np.trapz(s_imag_filtered)
        elif amplifier_type == "abs_area_ratio" or amplifier_type == "vga":
            s_area_filtered_real = np.trapz(np.abs(s_real_filtered))
            s_area_filtered_imag = np.trapz(np.abs(s_imag_filtered))
        else:
            s_area_filtered_real = ideal_area_real
            s_area_filtered_imag = ideal_area_imag

        if amplifier_type == "vga":
            analog_output_sample = np.array([complex(r*device_parameters["gain"], i*device_parameters["gain"]) for r, i in zip(s_real_filtered, s_imag_filtered)])
        else:
            analog_output_sample = np.array([complex(r/s_area_filtered_real*ideal_area_real, i/s_area_filtered_imag*ideal_area_imag) for r, i in zip(s_real_filtered, s_imag_filtered)])
    
    output_waveform = Waveform(analog_output_sample) 
    return output_waveform


# Hamiltonian without rotating frame.
# w_q = qubit freq, w_d = NCO freq, w_LO = LO freq
def hamiltonian_3dim_LO_modulation(t, E_t, args):
    w1 = args['w_q'] * 2 * np.pi
    w2 = 2 * w1 + args['anharmonicity'] * 2 * np.pi
    wD = (args['w_d'] + args['w_LO']) * 2 * np.pi
    lambda1 = 1
    lambda2 = np.sqrt(2)
    return Qobj((w1 - wD)* np.array([[0.,0.,0.],[0.,1.,0.],[0.,0.,0.]])
                + (w2 - 2 * wD)* np.array([[0.,0.,0.],[0.,0.,0.],[0.,0.,1.]])
                + E_t * np.array([[0.,lambda1 * np.exp(-1.j*wD*t),0.],[lambda1* np.exp(1.j*wD*t),0.,lambda2* np.exp(-1.j*wD*t)],[0.,lambda2* np.exp(1.j*wD*t),0.]]))


# Derive unitary with hamiltonian simulation
def hamiltonian_simulation(H, time_list, E, args):
    U = qeye(3)
    for t in time_list:
        U = (-1.j * H(t, E[int(t/args['dt'])], args) * args['dt']).expm() * U 
    return U


# DRAG pulse generation
def drag_generate(duration, amp, beta, sigma):
    center = duration / 2
    t = np.arange(0, duration)
    t_shifted = (t - center)
    gauss = np.exp(-((t_shifted / sigma) ** 2) / 2)
    deriv = - (t - center) / (sigma**2) * gauss
    return amp * gauss, amp * beta * deriv


# Inject SNR noise (following HR-II)
def generate_noise(input_pulse, dt):
    num_samples = len(input_pulse)
    impedance = 50
    pulse_power = np.trapz(input_pulse**2, np.linspace(0, num_samples * dt, num_samples, endpoint=False)) / impedance / (num_samples * dt)
    input_pulse = input_pulse + np.random.normal(0, np.sqrt(pulse_power / np.power(10, 48 / 20)), num_samples)
    return input_pulse


# Emulating the digital part of Drive circuit.
def calculate_drive_pulse(pulse_type, modulation_type, gate_time, filter_params, params, add_noise):
    gate_tlist = np.linspace(0, gate_time, int(gate_time/params['dt']), endpoint=False)

    A_I = np.zeros_like(gate_tlist)
    A_Q = np.zeros_like(gate_tlist)
    if pulse_type == "DRAG":
        A_I, A_Q = drag_generate(duration= len(gate_tlist), amp= params['V0'], beta= params['drag_lambda']/(params['anharmonicity']), sigma= params['sigma'])
    elif pulse_type == "Gaussian":
        A_I, A_Q = drag_generate(duration= len(gate_tlist), amp= params['V0'], beta= params['drag_lambda']/(params['anharmonicity']), sigma= params['sigma'])
        A_Q = A_Q * 0
    elif pulse_type == "Square":
        A_I = Constant(duration= len(gate_tlist), amp= params['V0']).get_waveform().samples
    elif pulse_type == "GaussianSquare":
        A_I, _ = drag_generate(duration= int((gate_time - params['square_width']) / params['dt']), amp= params['V0'], beta= params['drag_lambda']/(params['anharmonicity']), sigma= params['sigma'])
        A_I = np.concatenate((A_I[:int(len(A_I)/2)], params['V0'] * np.ones(len(gate_tlist) - len(A_I)), A_I[int(len(A_I)/2):]))
    else:
        print("Our model does not support {} pulse.".format(pulse_type))

    w_d = int(params['w_d'] * 1e9 * (2**(params['NCO_freq_resolution']-frexp(params['w_d'] * 1e9)[1]))) * (2**(frexp(params['w_d'] * 1e9)[1]-params['NCO_freq_resolution'])) * 1e-9
    if modulation_type == "frequency":
        I = - A_I * np.sin(2 * np.pi * w_d * gate_tlist) - A_Q * np.cos(2 * np.pi * w_d * gate_tlist)
        Q = - A_Q * np.sin(2 * np.pi * w_d * gate_tlist) + A_I * np.cos(2 * np.pi * w_d * gate_tlist)
    elif modulation_type == "polar":
        A = np.sqrt(np.square(A_I) + np.square(A_Q))
        Phi = np.arctan(A_Q/A_I)
        I = - A * np.sin(2 * np.pi * w_d * gate_tlist + Phi) 
        Q = A * np.cos(2 * np.pi * w_d * gate_tlist + Phi) 
    else:
        print("Our model does not support {} modulation.".format(modulation_type))

    digital_signal = [complex(I[idx], Q[idx]) for idx in range(len(I))]

    step_envelope = emulate_drive_circuit_filter(filter_params, Waveform(digital_signal), dt_ns=params['dt'], V0=params['V0']).samples

    E = np.real(step_envelope) * np.sin(2 * np.pi * params['w_LO'] * gate_tlist) + np.imag(step_envelope) * np.cos(2 * np.pi * params['w_LO'] * gate_tlist)

    if add_noise:
        E = generate_noise(E, dt=params['dt'] * 1e-9)

    return E, gate_tlist


# Error rate without decoherence
def calculate_error(sim_U, ideal_U):
    sim_d = sim_U * Qobj([[1., 0., 0.], [0., 0., 0.], [0., 0., 0.]]) * sim_U.dag()
    F = (basis(3,1).trans() * sim_d * basis(3,1)).sqrtm().tr()
    return 1 - abs(F)


# Error rate with decoherence
def calculate_error_decoherence(sim_U, ideal_U, T1, T2, gate_time, params):
    sim_d = sim_U * Qobj([[1., 0., 0.], [0., 0., 0.], [0., 0., 0.]]) * sim_U.dag()
    sim_d_2dim = sim_d.eliminate_states([2])

    w_d = w_d = int(params['w_d'] * 1e9 * (2**(params['NCO_freq_resolution']-frexp(params['w_d'] * 1e9)[1]))) * (2**(frexp(params['w_d'] * 1e9)[1]-params['NCO_freq_resolution'])) * 1e-9
    delta_w = (params['w_q'] - params['w_LO'] - w_d) * 2 * np.pi
    decoherent_d = Qobj([[1 + (sim_d_2dim[0][0][0] - 1) * np.exp(- gate_time / T1), sim_d_2dim[0][0][1] * np.exp(- gate_time / T2) * np.exp(1.j * delta_w * gate_time)], \
                         [sim_d_2dim[1][0][0] * np.exp(- gate_time / T2) * np.exp(-1.j * delta_w * gate_time), sim_d_2dim[1][0][1] * np.exp(- gate_time / T1)]])
    F = (basis(2,1).trans() * decoherent_d * basis(2,1)).sqrtm().tr()
    return 1 - abs(F), decoherent_d


# Drive pulse generation -> Hamiltonian simulation -> error rate calculation
def simulation(pulse_type, modulation_type, gate_time, filter_params, params, add_noise):
    E, gate_tlist = calculate_drive_pulse(pulse_type=pulse_type, modulation_type=modulation_type, gate_time=gate_time, filter_params=filter_params,\
                                    params=params, add_noise=add_noise)
    sim_U = hamiltonian_simulation(hamiltonian_3dim_LO_modulation, gate_tlist, E, params)
    error = calculate_error(sim_U, ideal_U= sigmax())
    return error


@ray.remote
def simulation_ray(pulse_type, modulation_type, gate_time, filter_params, params, add_noise, V0, drag_lambda):
    params['V0'] = V0
    params['drag_lambda'] = drag_lambda
    E, gate_tlist = calculate_drive_pulse(pulse_type=pulse_type, modulation_type=modulation_type, gate_time=gate_time, filter_params=filter_params,\
                                    params=params, add_noise=add_noise)
    sim_U = hamiltonian_simulation(hamiltonian_3dim_LO_modulation, gate_tlist, E, params)
    error = calculate_error(sim_U, ideal_U= sigmax())
    return error, params


# drag_lambda sweep w/o ray
def sweep_drag_lambda(num_trials, step_size, start_val, pulse_type, modulation_type, gate_time, filter_params, params, add_noise):
    min_error_rate = 1
    min_error_rate_param = 0
    for i, cur_val in enumerate(np.arange(start_val, start_val+step_size*num_trials, step_size)):
        print("Trial {}: drag_lambda = {}".format(i, cur_val))
        params['drag_lambda'] = cur_val
        print("params")
        print(params)

        error = simulation(pulse_type, modulation_type, gate_time, filter_params, params, add_noise)

        print("# Error rate: {}".format(error))
        min_error_rate = min(min_error_rate, error)
        if (min_error_rate == error):
            # min_error_rate_theta = theta / (num/2) * np.pi
            min_error_rate_param = cur_val
            
    print("Minimum error rate with drag_lambda = {} : {} ".format(min_error_rate_param, min_error_rate))


# V0 sweep w/o ray
def sweep_V0(num_trials, step_size, start_val, pulse_type, modulation_type, gate_time, filter_params, params, add_noise):
    min_error_rate = 1
    min_error_rate_param = 0
    for i, cur_val in enumerate(np.arange(start_val, start_val+step_size*num_trials, step_size)):
        print("Trial {}: V0 = {}".format(i, cur_val))
        params['V0'] = cur_val
        print("params")
        print(params)

        error = simulation(pulse_type, modulation_type, gate_time, filter_params, params, add_noise)

        print("# Error rate: {}".format(error))
        min_error_rate = min(min_error_rate, error)
        if (min_error_rate == error):
            # min_error_rate_theta = theta / (num/2) * np.pi
            min_error_rate_param = cur_val

    print("Minimum error rate with V0 = {} : {} ".format(min_error_rate_param, min_error_rate))


# drag_lambda sweep
def sweep_drag_lambda_ray(num_trials, step_size, start_val, pulse_type, modulation_type, gate_time, filter_params, params, add_noise):
    # ray.init(
    #     _system_config={
    #         # Allow spilling until the local disk is 99% utilized.
    #         # This only affects spilling to the local file system.
    #         "local_fs_capacity_threshold": 0.99,
    #         "object_spilling_config": json.dumps(
    #             {
    #             "type": "filesystem",
    #             "params": {
    #                 "directory_path": "/tmp/spill",
    #             },
    #             },
    #         )
    #     },
    # )
    ray.init ()
    simuls = [simulation_ray.remote(pulse_type, modulation_type, gate_time, filter_params, params, add_noise, params['V0'], drag_lambda) for drag_lambda in np.linspace(start_val, start_val + (num_trials - 1) * step_size, num_trials)]
    results = ray.get(simuls)
    min_error_rate = 1
    min_error_rate_param = dict()
    for result in results:
        if min_error_rate > result[0]:
            min_error_rate = result[0]
            min_error_rate_param = result[1]
    print("## Minimum error rate with {}".format(min_error_rate_param))
    print("Min error = {}".format(min_error_rate))
    ray.shutdown()
    return min_error_rate_param


# V0 sweep
def sweep_V0_ray(num_trials, step_size, start_val, pulse_type, modulation_type, gate_time, filter_params, params, add_noise):
    # ray.init(
    #     _system_config={
    #         # Allow spilling until the local disk is 99% utilized.
    #         # This only affects spilling to the local file system.
    #         "local_fs_capacity_threshold": 0.99,
    #         "object_spilling_config": json.dumps(
    #             {
    #             "type": "filesystem",
    #             "params": {
    #                 "directory_path": "/tmp/spill",
    #             },
    #             },
    #         )
    #     },
    # )
    ray.init ()
    simuls = [simulation_ray.remote(pulse_type, modulation_type, gate_time, filter_params, params, add_noise, V0, params['drag_lambda']) for V0 in np.linspace(start_val, start_val + (num_trials - 1) * step_size, num_trials)]
    results = ray.get(simuls)
    min_error_rate = 1
    min_error_rate_param = dict()
    for result in results:
        if min_error_rate > result[0]:
            min_error_rate = result[0]
            min_error_rate_param = result[1]
    print("## Minimum error rate with {}".format(min_error_rate_param))
    print("Min error = {}".format(min_error_rate))
    ray.shutdown()
    return min_error_rate_param


# Error simulation for given gate time (while sweeping V0 and drag_lambda)
def gatetime_error_simulation(standard_setup, gate_time_list, num_trials, V0_step_size, lambda_step_size, pulse_type, modulation_type, filter_params, params, T1, T2):
    standard_gate_time = standard_setup['gate_time']
    standard_V0 = standard_setup['V0']
    standard_sigma = standard_setup['sigma']
    standard_lambda = standard_setup['drag_lambda']
    params['drag_lambda'] = standard_lambda

    f = open('1q_results/gate_time_error_results_DAC{}bit.csv'.format(filter_params['output_precision']), 'w', newline='')
    wr = csv.writer(f)
    wr.writerow(["gate time", "V0", "sigma", "drag lambda", "error (w/o deco)", "error (w deco)", "LOG scale error (w/o deco)", "LOG scale error (w deco)"])
    
    for gate_time in gate_time_list:
        print("##### Gate time = {} ns".format(gate_time))
        sigma = standard_sigma * gate_time / standard_gate_time
        params['sigma'] = sigma

        V0_step_size = (standard_V0 * standard_gate_time / gate_time) / (5 * num_trials)
        start_V0 = standard_V0 * standard_gate_time / gate_time - num_trials * V0_step_size / 2
        
        V0_min_error_rate_param = sweep_V0_ray(num_trials, V0_step_size, start_V0, pulse_type, modulation_type, gate_time, filter_params, params, add_noise=False)

        start_lambda = standard_lambda - num_trials * lambda_step_size / 2
        min_error_rate_param = sweep_drag_lambda_ray(num_trials, lambda_step_size, start_lambda, pulse_type, modulation_type, gate_time, filter_params, V0_min_error_rate_param, add_noise=False)

        E, gate_tlist = calculate_drive_pulse(pulse_type=pulse_type, modulation_type=modulation_type, gate_time=gate_time, filter_params=filter_params,\
                                        params=min_error_rate_param, add_noise=True)
        sim_U = hamiltonian_simulation(hamiltonian_3dim_LO_modulation, gate_tlist, E, params)

        error = calculate_error(sim_U, ideal_U= sigmax())
        print("Error rate = {}".format(error))

        decoherent_error, decoherent_d = calculate_error_decoherence(sim_U, ideal_U= sigmax(), T1=T1, T2=T2, gate_time=gate_time, params=params)
        print("With decoherence error rate = {}".format(decoherent_error))
        print("=========================")
        wr.writerow([gate_time, V0_min_error_rate_param['V0'], sigma, min_error_rate_param['drag_lambda'], error, decoherent_error, np.log10(error),  np.log10(decoherent_error)])
    f.close()


def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--relax", "-r", help="Relaxation time (i.e., T1 time) [us]", type=float, default=122000)
    parser.add_argument ("--coherence", "-c", help="Coherence time (i.e., T2 time) [us]", type=float, default=118000)
    parser.add_argument ("--gate_time", "-t", help="Target 1Q-gate time [ns]", type=int, default=25)
    parser.add_argument ("--freq_qubit", "-q", help="Qubit frequency [GHz]", type=float, default=5)
    parser.add_argument ("--freq_lo", "-l", help="Local oscillator frequency [GHz]", type=float, default=4)
    parser.add_argument ("--nco_precision", "-n", help="NCO bit precision [bit]", type=int, default=22)
    parser.add_argument ("--dac_precision", "-d", help="DAC bit precision [bit]", type=int, default=9)
    parser.add_argument ("--pulse_type", "-p", help="Pulse type (i.e., DRAG, Gaussian, Square, GaussianSquare)", type=str, default="DRAG")
    parser.add_argument ("--modulation_type", "-mo", help="Modulation type (i.e., polar, frequency)", type=str, default="polar")
    parser.add_argument ("--filter_type", "-f", help="Filter type (i.e., chebyshev_LPF, average_filter)", type=str, default="chebyshev_LPF")
    args = parser.parse_args ()
    return args


if __name__ == "__main__":

    args = arg_parse ()

    standard_setup = {"gate_time": 25, "V0": 0.035112, "sigma": 3471.875, "drag_lambda": 110}
    gate_time = args.gate_time
    num_trials = 500
    V0_step_size = 0.0001
    lambda_step_size = 0.1
    T1 = args.relax
    T2 = args.coherence
    w_q = args.freq_qubit
    w_LO = args.freq_lo
    nco_resolution = args.nco_precision
    dac_resolution = args.dac_precision
    pulse_type = args.pulse_type
    modulation_type = args.modulation_type
    filter_type = args.filter_type

    params = {'dt': 0.001, 'NCO_freq_resolution': nco_resolution, 'w_d': w_q - w_LO, 'w_LO': w_LO, 'w_q': w_q, 'anharmonicity': -0.25}
    filter_params = {"device_frequency": 2.5e9, "output_precision": dac_resolution, "filter_type": filter_type, "cutoff_frequency": 1.8e9, "amplifier_type": "vga", "gain": 15}
    gatetime_error_simulation(standard_setup, [gate_time], num_trials, V0_step_size, lambda_step_size, pulse_type, modulation_type, filter_params, params, T1, T2)
