import numpy as np
from qutip import *
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from qiskit.pulse.library import Waveform, Constant
from math import frexp 
import json, ray, os, scipy, argparse
from scipy.optimize import curve_fit
from skspatial.objects import Line
from qutip import *
from scipy.signal import cheby1, freqs
from scipy import interpolate

ray.init(
            _system_config={
                "local_fs_capacity_threshold": 0.99,
                "object_spilling_config": json.dumps(
                    {
                        "type": "filesystem",
                        "params": {
                            "directory_path": "/tmp/spill",
                        },
                        },
                )
            },
        )


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


# Generate the output pulse of TX circuits
# (which will be used as an input for Hamiltonian simulation).
def generate_input_pulse (gate_time, filter_params, params):
    gate_tlist = np.linspace(0, gate_time, int(gate_time/params['dt']), endpoint=False)
    A_I = Constant(duration= len(gate_tlist), amp= params['V0']).get_waveform().samples
    I = A_I * np.sin(2 * np.pi * params['w_d'] * gate_tlist)
    Q = A_I * np.cos(2 * np.pi * params['w_d'] * gate_tlist)
    IQ = [complex(r, i) for r, i in zip(I, Q)]
    # IQ_NCO = single_error_model.emulate_drive_circuit_filter(filter_params, Waveform(IQ), params['dt'], params['V0']).samples
    IQ_NCO = emulate_drive_circuit_filter(filter_params, Waveform(IQ), params['dt'], params['V0']).samples
    E = np.real(IQ_NCO) * np.cos(2 * np.pi * params['w_LO'] * gate_tlist) + np.imag(IQ_NCO) * np.sin(2 * np.pi * params['w_LO'] * gate_tlist)
    return E


# Get the reflect signal (i.e., IQ value) of the qubit plane 
# (by running Hamiltonian simulation with qubit-resonator coupled systems and input TX pulse).
@ray.remote
def SMEsolver(sme_args, params, filter_params, input_pulse_duration):
    times = np.linspace(0.0, sme_args['simul_time'], sme_args['num_steps']) # ns
    psi0 = tensor(basis(2,0), fock(sme_args['max_photon_num'],0))
    psi1 = tensor(basis(2,1), fock(sme_args['max_photon_num'],0))
    a = destroy(sme_args['max_photon_num'])
    input_pulse = generate_input_pulse(sme_args['simul_time'], filter_params, params)

    def HD_coeff(t, args):
        if t < input_pulse_duration:
            return input_pulse[int(t / params['dt'])]
        else:
            return 0

    H_JC_disp = tensor(params['w_r'] * qeye(2) + params['chi'] * sigmaz(), a.dag() * a) + tensor((params['w_q'] + params['chi']) * sigmaz(), qeye(sme_args['max_photon_num'])) / 2
    H1 = tensor(qeye(2), a.dag())
    H2 = tensor(qeye(2), a)
    HD = H1 + H2
    H0 = 2 * np.pi * H_JC_disp

    H = [H0, [HD, HD_coeff]]

    c_ops = []
    sc_ops = []
    dephase_rate = 1 / params['T1'] - 1 / (2 * params['T2'])
    dephase_rate = dephase_rate if dephase_rate > 0 else 0

    if dephase_rate > 0:
        c_ops = [np.sqrt(2 * np.pi * dephase_rate) * tensor(sigmaz(), qeye(sme_args['max_photon_num']))]
    sc_ops = [np.sqrt(2 * np.pi * params['kappa']) * tensor(qeye(2), a), np.sqrt(2 * np.pi / params['T1']) * tensor(destroy(2), qeye(sme_args['max_photon_num']))]

    stoc_solution0 = smesolve(H, psi0, times, 
        c_ops=c_ops,
        sc_ops=sc_ops,
        e_ops=[tensor(qeye(2), a + a.dag()) / 2, tensor(qeye(2), -1.j * a + 1.j * a.dag()) / 2],
        ntraj=sme_args['ntraj'],
        nsubsteps=sme_args['nsubsteps'],
        method='homodyne')

    stoc_solution1 = smesolve(H, psi1, times, 
        c_ops=c_ops,
        sc_ops=sc_ops,
        e_ops=[tensor(qeye(2), a + a.dag()) / 2, tensor(qeye(2), -1.j * a + 1.j * a.dag()) / 2],
        ntraj=sme_args['ntraj'],
        nsubsteps=sme_args['nsubsteps'],
        method='homodyne')

    return [stoc_solution0.expect[0], stoc_solution0.expect[1], stoc_solution1.expect[0], stoc_solution1.expect[1]]


# Applying the noise of microwave componants (TWPA, HEMT, LNA) into the reflected signal
def add_noise (output_pulse_t, dt, add_twpa_noise = True, add_hemt_noise = True, add_lna_noise = False):
    num_samples = len(output_pulse_t)
    k = np.power(10, -22.85991672) # W/K/Hz
    h_bar = 1.0545718e-34 # Js
    # Add 10mK TWPA noise
    TWPA_noise_temp = 0.4 # K (0.6)
    TWPA_gain = 15 # dB (20)
    TWPA_bw = 5 # GHz
    TWPA_noise = k * TWPA_noise_temp * TWPA_bw * 1e9 # W
    TWPA_noise_ghz = TWPA_noise * dt / h_bar / 1e9 / 1e9 # GHz
    if add_twpa_noise:
        output_pulse_t = output_pulse_t + np.random.normal(0, np.sqrt(TWPA_noise_ghz), num_samples)
        output_pulse_t = output_pulse_t * (np.power(10, TWPA_gain / 10))
    # Add 4K HEMT noise
    HEMT_noise_temp = 3.2 # K
    HEMT_gain = 40 # dB
    HEMT_bw = 4 # GHz
    HEMT_noise = k * HEMT_noise_temp * HEMT_bw * 1e9 # W
    HEMT_noise_ghz = HEMT_noise * dt / h_bar / 1e9 / 1e9 # GHz
    if add_hemt_noise:
        output_pulse_t = output_pulse_t + np.random.normal(0, np.sqrt(HEMT_noise_ghz), num_samples)
        output_pulse_t = output_pulse_t * (np.power(10, HEMT_gain / 10))
    # Add 300K LNA noise
    LNA_noise_temp = 54.5 # K
    LNA_gain = 40 # dB
    LNA_bw = 4 # GHz
    LNA_noise = k * LNA_noise_temp * LNA_bw * 1e9 # W
    LNA_noise_ghz = LNA_noise * dt / h_bar / 1e9 / 1e9 # GHz
    if add_lna_noise:
        output_pulse_t = output_pulse_t + np.random.normal(0, np.sqrt(LNA_noise_ghz), num_samples)
        output_pulse_t = output_pulse_t * (np.power(10, LNA_gain / 10))
    
    output_pulse_t = output_pulse_t * np.power(10, - (add_twpa_noise * TWPA_gain + add_hemt_noise * HEMT_gain + add_lna_noise * LNA_gain) / 10)
    
    return output_pulse_t


# Get the state-discrimination line
def get_line_from_iq (
    I_0: list, Q_0: list, I_1: list, Q_1: list
) -> Line:
    # Find a center of each state
    state_0_center = (np.average(I_0), np.average(Q_0))
    state_1_center = (np.average(I_1), np.average(Q_1))

    ## A line that connects two centers
    slope = (state_1_center[1] - state_0_center[1]) / (state_1_center[0] - state_0_center[0])
    center_point = ((state_0_center[0] + state_1_center[0]) / 2, (state_0_center[1] + state_1_center[1]) / 2)
    y_intercept = (-1)*slope*center_point[0] + center_point[1]

    xx = np.arange(min(state_0_center[0], state_1_center[0]), max(state_0_center[0], state_1_center[0]), 0.000001)
    yy = [x*slope + y_intercept for x in xx]

    ## A line that is normal to the center-connecting line 
    slope_normal = -1/slope
    y_intercept_normal = (-1)*slope_normal*center_point[0] + center_point[1]
    xx_normal = np.arange(min(min(I_0),min(I_1)), max(max(I_0),max(I_1)), 0.00001)
    yy_normal = [x*slope_normal + y_intercept_normal for x in xx_normal]
    line = Line(point=center_point, direction=(1,slope_normal))

    return line, state_0_center, state_1_center


# Get the fidelity of the bin-counting method (Intel Horseridge-II).
def bin_counting_get_fidelity (
    I_0: list, Q_0: list, I_1: list, Q_1: list, line: Line, IQ_binning_end_idx: int, params: dict, options: dict
) -> tuple:
    ## Project IQ results into distances from the predefined line
    result_0_state_1dim = [line.distance_point(point) for point in zip(I_0, Q_0)]
    result_1_state_1dim = [line.distance_point(point) for point in zip(I_1, Q_1)]

    slope_normal = line.direction[1]
    y_intercept_normal = line.intersect_line(Line([0,0],[0,1]))[1]

    result_0_state_1dim = [-val if x*slope_normal+y_intercept_normal < y else val for (val, x, y) in zip(result_0_state_1dim, I_0, Q_0)]
    result_1_state_1dim = [-val if x*slope_normal+y_intercept_normal < y else val for (val, x, y) in zip(result_1_state_1dim, I_1, Q_1)]

    # Fit each histogram into the gaussian function
    def func(x, a, x0, sigma):
        return a*np.exp(-(x-x0)**2/(2*sigma**2))

    # Get histogram results
    num = params['hist_bins']
    state_hist_0 = plt.hist(result_0_state_1dim, bins = num, label='0_state')
    state_hist_1 = plt.hist(result_1_state_1dim, bins = num, label='1_state')

    ## Execute curve_fit
    hist_0_x = [(state_hist_0[1][i-1] + state_hist_0[1][i]) / 2 for i in range(1, len(state_hist_0[1]), 1)]
    hist_0_y = (state_hist_0[0])
    hist_1_x = [(state_hist_1[1][i-1] + state_hist_1[1][i]) / 2 for i in range(1, len(state_hist_1[1]), 1)]
    hist_1_y = (state_hist_1[0])

    ## initial guess
    init_0_amp = max(hist_0_y)
    init_1_amp = max(hist_1_y)

    init_0_mean = sum(hist_0_x*hist_0_y)/sum(hist_0_y)
    init_1_mean = sum(hist_1_x*hist_1_y)/sum(hist_1_y)

    init_0_sigma = np.sqrt(abs(sum((hist_0_x-init_0_mean)**2*hist_0_y)/sum(hist_0_y)))
    init_1_sigma = np.sqrt(abs(sum((hist_1_x-init_1_mean)**2*hist_1_y)/sum(hist_1_y)))

    popt_0, pcov_0 = curve_fit(func, hist_0_x, hist_0_y, p0 = [init_0_amp, init_0_mean, init_0_sigma], maxfev=50000)
    popt_1, pcov_1 = curve_fit(func, hist_1_x, hist_1_y, p0 = [init_1_amp, init_1_mean, init_1_sigma], maxfev=50000)

    # Determine readout error rate
    amp_0, mean_0, sigma_0 = popt_0
    amp_1, mean_1, sigma_1 = popt_1
    sigma_0 = abs(sigma_0)
    sigma_1 = abs(sigma_1)

    rv_0 = scipy.stats.norm(mean_0, sigma_0)
    rv_1 = scipy.stats.norm(mean_1, sigma_1)

    prob_0_roi = 1-rv_0.cdf(0)
    prob_1_roi = 1-rv_1.cdf(0)

    num_samples = IQ_binning_end_idx

    error_rate_0 = 0
    for k in range(num_samples//2, num_samples+1, 1):
        error_0_k = scipy.stats.binom(num_samples, prob_0_roi).pmf(k)
        error_rate_0 += error_0_k
        
    error_rate_1 = 0
    for k in range(0, num_samples//2, 1):
        error_1_k = scipy.stats.binom(num_samples, prob_1_roi).pmf(k)
        error_rate_1 += error_1_k
        
    readout_error = 0.5*error_rate_0 + 0.5*error_rate_1
    
    verbose = options['verbose']
    if verbose:
        print("amp_0: {}, mean_0: {}, sigma_0: {}".format(amp_0, mean_0, sigma_0))
        print("amp_1: {}, mean_1: {}, sigma_1: {}".format(amp_1, mean_1, sigma_1))

        print("prob_0_roi: {}".format(prob_0_roi))
        print("prob_1_roi: {}".format(prob_1_roi))

        print("error_rate_0: {}".format(error_rate_0))
        print("error_rate_1: {}".format(error_rate_1))
        print("readout_error: {}".format(readout_error))
        
    return (error_rate_0, error_rate_1, readout_error)


# Calculate the fidelity of the bin-counting method (multiprocessed)
@ray.remote
def bin_counting_get_fidelity_ray (
    I_0: list, Q_0: list, I_1: list, Q_1: list, line: Line, IQ_binning_end_idx: int, params: dict, options: dict
):
    ## Project IQ results into distances from the predefined line
    result_0_state_1dim = [line.distance_point(point) for point in zip(I_0, Q_0)]
    result_1_state_1dim = [line.distance_point(point) for point in zip(I_1, Q_1)]

    slope_normal = line.direction[1]
    y_intercept_normal = line.intersect_line(Line([0,0],[0,1]))[1]

    result_0_state_1dim = [-val if x*slope_normal+y_intercept_normal < y else val for (val, x, y) in zip(result_0_state_1dim, I_0, Q_0)]
    result_1_state_1dim = [-val if x*slope_normal+y_intercept_normal < y else val for (val, x, y) in zip(result_1_state_1dim, I_1, Q_1)]

    # Fit each histogram into the gaussian function
    def func(x, a, x0, sigma):
        return a*np.exp(-(x-x0)**2/(2*sigma**2))

    # Get histogram results
    num = params['hist_bins']
    state_hist_0 = plt.hist(result_0_state_1dim, bins = num, label='0_state')
    state_hist_1 = plt.hist(result_1_state_1dim, bins = num, label='1_state')

    ## Execute curve_fit
    hist_0_x = [(state_hist_0[1][i-1] + state_hist_0[1][i]) / 2 for i in range(1, len(state_hist_0[1]), 1)]
    hist_0_y = (state_hist_0[0])
    hist_1_x = [(state_hist_1[1][i-1] + state_hist_1[1][i]) / 2 for i in range(1, len(state_hist_1[1]), 1)]
    hist_1_y = (state_hist_1[0])

    ## initial guess
    init_0_amp = max(hist_0_y)
    init_1_amp = max(hist_1_y)

    init_0_mean = sum(hist_0_x*hist_0_y)/sum(hist_0_y)
    init_1_mean = sum(hist_1_x*hist_1_y)/sum(hist_1_y)

    init_0_sigma = np.sqrt(abs(sum((hist_0_x-init_0_mean)**2*hist_0_y)/sum(hist_0_y)))
    init_1_sigma = np.sqrt(abs(sum((hist_1_x-init_1_mean)**2*hist_1_y)/sum(hist_1_y)))

    popt_0, pcov_0 = curve_fit(func, hist_0_x, hist_0_y, p0 = [init_0_amp, init_0_mean, init_0_sigma], maxfev=50000)
    popt_1, pcov_1 = curve_fit(func, hist_1_x, hist_1_y, p0 = [init_1_amp, init_1_mean, init_1_sigma], maxfev=50000)

    # Determine readout error rate
    amp_0, mean_0, sigma_0 = popt_0
    amp_1, mean_1, sigma_1 = popt_1
    sigma_0 = abs(sigma_0)
    sigma_1 = abs(sigma_1)

    rv_0 = scipy.stats.norm(mean_0, sigma_0)
    rv_1 = scipy.stats.norm(mean_1, sigma_1)

    prob_0_roi = 1-rv_0.cdf(0)
    prob_1_roi = 1-rv_1.cdf(0)

    num_samples = IQ_binning_end_idx

    error_rate_0 = 0
    for k in range(num_samples//2, num_samples+1, 1):
        error_0_k = scipy.stats.binom(num_samples, prob_0_roi).pmf(k)
        error_rate_0 += error_0_k
        
    error_rate_1 = 0
    for k in range(0, num_samples//2, 1):
        error_1_k = scipy.stats.binom(num_samples, prob_1_roi).pmf(k)
        error_rate_1 += error_1_k
        
    readout_error = 0.5*error_rate_0 + 0.5*error_rate_1
    
    verbose = options['verbose']
    if verbose:
        print("amp_0: {}, mean_0: {}, sigma_0: {}".format(amp_0, mean_0, sigma_0))
        print("amp_1: {}, mean_1: {}, sigma_1: {}".format(amp_1, mean_1, sigma_1))

        print("prob_0_roi: {}".format(prob_0_roi))
        print("prob_1_roi: {}".format(prob_1_roi))

        print("error_rate_0: {}".format(error_rate_0))
        print("error_rate_1: {}".format(error_rate_1))
        print("readout_error: {}".format(readout_error))
        
    return readout_error


# Fit each histogram into the gaussian function
def gauss(x,mu,sigma,A):
    return A*np.exp(-(x-mu)**2/2/sigma**2)


# Get the fidelity of the single-point method (Google Sycamore).
def single_point_get_fidelity (
    I_0: list, Q_0: list, I_1: list, Q_1: list, line: Line, IQ_binning_end_idx: int, params: dict, options: dict
) -> tuple:
    # Project IQ results into distances from the predefined line
    result_0_state_1dim = [line.distance_point(point) for point in zip(I_0, Q_0)]
    result_1_state_1dim = [line.distance_point(point) for point in zip(I_1, Q_1)]

    slope_normal = line.direction[1]
    y_intercept_normal = line.intersect_line(Line([0,0],[0,1]))[1]

    result_0_state_1dim = [-val if x*slope_normal+y_intercept_normal < y else val for (val, x, y) in zip(result_0_state_1dim, I_0, Q_0)]
    result_1_state_1dim = [-val if x*slope_normal+y_intercept_normal < y else val for (val, x, y) in zip(result_1_state_1dim, I_1, Q_1)]

    # Get histogram results
    num = params['hist_bins']
    plt.figure()
    state_hist_0 = plt.hist(result_0_state_1dim, bins = num, label='0_state')
    state_hist_1 = plt.hist(result_1_state_1dim, bins = num, label='1_state')
    plt.legend()
    plt.show()

    ## Execute curve_fit    
    hist_0_x = np.array([(state_hist_0[1][i-1] + state_hist_0[1][i]) / 2 for i in range(1, len(state_hist_0[1]), 1)])
    hist_0_y = (state_hist_0[0])
    hist_1_x = np.array([(state_hist_1[1][i-1] + state_hist_1[1][i]) / 2 for i in range(1, len(state_hist_1[1]), 1)])
    hist_1_y = (state_hist_1[0])

    plt.figure()
    plt.scatter(hist_0_x, hist_0_y, label='0 state', s=10)
    plt.scatter(hist_1_x, hist_1_y, label='1 state', s=10)
    plt.legend()
    plt.show()

    popt_0, pcov_0 = curve_fit(gauss, hist_0_x, hist_0_y, maxfev=50000)
    popt_1, pcov_1 = curve_fit(gauss, hist_1_x, hist_1_y, maxfev=50000)

    rv_0 = scipy.stats.norm(popt_0[0], abs(popt_0[1]))
    rv_1 = scipy.stats.norm(popt_1[0], abs(popt_1[1]))

    prob_0_roi = 1-rv_0.cdf(0)
    prob_1_roi = rv_1.cdf(0)

    e_g_error_idx = (hist_0_x > 0.0)
    g_e_error_idx = (hist_1_x < 0.0)
    e_g_error = np.sum(hist_0_y[e_g_error_idx]) / np.sum(hist_0_y)
    g_e_error = np.sum(hist_1_y[g_e_error_idx]) / np.sum(hist_1_y)

    return popt_0, popt_1, prob_0_roi, prob_1_roi, e_g_error, g_e_error


# Apply the analog/digital noise of RX circuits
# (The output I & Q are for IQ value of the bin-counting method)
# (The output I_NCO & Q_NCO are for IQ value of the single-point method)
def extract_iq (IQ, gate_tlist, params, avg_window):

    # LO down mix
    I_LO = IQ * np.cos(2 * np.pi * params['w_LO'] * gate_tlist)
    Q_LO = - IQ * np.sin(2 * np.pi * params['w_LO'] * gate_tlist)
    
    num_samples = len(I_LO)
    cutoff_frequency = 1.25e9

    # LPF
    ideal_area_real = np.trapz(np.abs(I_LO))
    ideal_area_imag = np.trapz(np.abs(Q_LO))
    s_real = I_LO
    s_imag = Q_LO
    f_real = np.fft.rfft(s_real)
    f_imag = np.fft.rfft(s_imag)
    digital_output_sample_frequency = np.fft.rfftfreq(num_samples, params['dt'] * 1e-9)
    f_real_filtered = np.array([amp if np.abs(freq) <= cutoff_frequency else 0 for amp, freq in zip(f_real, digital_output_sample_frequency)])
    f_imag_filtered = np.array([amp if np.abs(freq) <= cutoff_frequency else 0 for amp, freq in zip(f_imag, digital_output_sample_frequency)])
    
    s_real_filtered = np.array([r for r in np.fft.irfft(f_real_filtered)])
    s_imag_filtered = np.array([i for i in np.fft.irfft(f_imag_filtered)])
    s_area_filtered_real = np.trapz(np.abs(s_real_filtered))
    s_area_filtered_imag = np.trapz(np.abs(s_imag_filtered))

    IQ_LO_filtered = np.array([complex(r/s_area_filtered_real*ideal_area_real, i/s_area_filtered_imag*ideal_area_imag) for r, i in zip(s_real_filtered, s_imag_filtered)])

    # ADC의 bit/frequency precision 적용
    output_precision_ADC = 7
    IQ_LO_ADC = IQ_LO_filtered[::int(1/ 2.5e9 / (params['dt'] * 1e-9))]
    new_gate_tlist = np.linspace(0, gate_tlist[-1], len(IQ_LO_ADC), endpoint=False)
    IQ_LO_ADC = np.array([complex(int(v.real* (2**(output_precision_ADC-frexp(v.real)[1]))) * (2**(frexp(v.real)[1]-output_precision_ADC)),
                                      int(v.imag* (2**(output_precision_ADC-frexp(v.imag)[1]))) * (2**(frexp(v.imag)[1]-output_precision_ADC))) for v in IQ_LO_ADC.copy()])
    I_LO_ADC = np.real(IQ_LO_ADC)
    Q_LO_ADC = np.imag(IQ_LO_ADC)

    # NCO down mix
    output_precision_NCO = 10
    cos_NCO = np.cos(2 * np.pi * params['w_d'] * new_gate_tlist) 
    sin_NCO = np.sin(2 * np.pi * params['w_d'] * new_gate_tlist)
    cosine_NCO_ideal = np.array([complex(r,i) for r,i in zip(cos_NCO, sin_NCO)])
    cosine_NCO = np.array([complex(int(v.real* (2**(output_precision_NCO-frexp(v.real)[1]))) * (2**(frexp(v.real)[1]-output_precision_NCO)),
                                      int(v.imag* (2**(output_precision_NCO-frexp(v.imag)[1]))) * (2**(frexp(v.imag)[1]-output_precision_NCO))) for v in cosine_NCO_ideal])
    I_NCO = I_LO_ADC * np.real(cosine_NCO) + Q_LO_ADC * np.imag(cosine_NCO)
    Q_NCO = - I_LO_ADC * np.imag(cosine_NCO) + Q_LO_ADC * np.real(cosine_NCO)
    
    # Moving average & IQ binning
    I = list()
    Q = list()

    I_sum = 0
    Q_sum = 0
    for idx in range(len(I_NCO)):
        I_sum += I_NCO[idx]
        Q_sum += Q_NCO[idx]
        if idx >= avg_window:
            I_sum -= I_NCO[idx - avg_window]
            Q_sum -= Q_NCO[idx - avg_window]
            I.append(I_sum)
            Q.append(Q_sum)
    I = np.array(I) / avg_window
    Q = np.array(Q) / avg_window
    
    return I, Q, IQ_LO_filtered, I_LO_ADC, Q_LO_ADC, I_LO, Q_LO, I_NCO, Q_NCO, new_gate_tlist


# Multiprocessed IQ value extraction.
@ray.remote
def extract_iq_ray (IQ, gate_tlist, params, avg_window):
    # LO down mix
    I_LO = IQ * np.cos(2 * np.pi * params['w_LO'] * gate_tlist)
    Q_LO = - IQ * np.sin(2 * np.pi * params['w_LO'] * gate_tlist)
    
    num_samples = len(I_LO)
    cutoff_frequency = 1.25e9
    # LPF
    ideal_area_real = np.trapz(np.abs(I_LO))
    ideal_area_imag = np.trapz(np.abs(Q_LO))
    s_real = I_LO
    s_imag = Q_LO
    f_real = np.fft.rfft(s_real)
    f_imag = np.fft.rfft(s_imag)
    digital_output_sample_frequency = np.fft.rfftfreq(num_samples, params['dt'] * 1e-9)
    f_real_filtered = np.array([amp if np.abs(freq) <= cutoff_frequency else 0 for amp, freq in zip(f_real, digital_output_sample_frequency)])
    f_imag_filtered = np.array([amp if np.abs(freq) <= cutoff_frequency else 0 for amp, freq in zip(f_imag, digital_output_sample_frequency)])
    
    s_real_filtered = np.array([r for r in np.fft.irfft(f_real_filtered)])
    s_imag_filtered = np.array([i for i in np.fft.irfft(f_imag_filtered)])
    s_area_filtered_real = np.trapz(np.abs(s_real_filtered))
    s_area_filtered_imag = np.trapz(np.abs(s_imag_filtered))

    IQ_LO_filtered = np.array([complex(r/s_area_filtered_real*ideal_area_real, i/s_area_filtered_imag*ideal_area_imag) for r, i in zip(s_real_filtered, s_imag_filtered)])

    # ADC의 bit/frequency precision 적용
    output_precision_ADC = 7
    IQ_LO_ADC = IQ_LO_filtered[::int(1/ 2.5e9 / (params['dt'] * 1e-9))]
    new_gate_tlist = np.linspace(0, gate_tlist[-1], len(IQ_LO_ADC), endpoint=False)
    IQ_LO_ADC = np.array([complex(int(v.real* (2**(output_precision_ADC-frexp(v.real)[1]))) * (2**(frexp(v.real)[1]-output_precision_ADC)),
                                      int(v.imag* (2**(output_precision_ADC-frexp(v.imag)[1]))) * (2**(frexp(v.imag)[1]-output_precision_ADC))) for v in IQ_LO_ADC.copy()])
    I_LO_ADC = np.real(IQ_LO_ADC)
    Q_LO_ADC = np.imag(IQ_LO_ADC)

    # NCO down mix
    output_precision_NCO = 22
    cos_NCO = np.cos(2 * np.pi * params['w_d'] * new_gate_tlist) 
    sin_NCO = np.sin(2 * np.pi * params['w_d'] * new_gate_tlist)
    cosine_NCO_ideal = np.array([complex(r,i) for r,i in zip(cos_NCO, sin_NCO)])
    cosine_NCO = np.array([complex(int(v.real* (2**(output_precision_NCO-frexp(v.real)[1]))) * (2**(frexp(v.real)[1]-output_precision_NCO)),
                                      int(v.imag* (2**(output_precision_NCO-frexp(v.imag)[1]))) * (2**(frexp(v.imag)[1]-output_precision_NCO))) for v in cosine_NCO_ideal])
    I_NCO = I_LO_ADC * np.real(cosine_NCO) + Q_LO_ADC * np.imag(cosine_NCO)
    Q_NCO = - I_LO_ADC * np.imag(cosine_NCO) + Q_LO_ADC * np.real(cosine_NCO)
    
    # Moving average & IQ binning
    I = list()
    Q = list()

    I_sum = 0
    Q_sum = 0
    for idx in range(len(I_NCO)):
        I_sum += I_NCO[idx]
        Q_sum += Q_NCO[idx]
        if idx >= avg_window:
            I_sum -= I_NCO[idx - avg_window]
            Q_sum -= Q_NCO[idx - avg_window]
            I.append(I_sum)
            Q.append(Q_sum)
    I = np.array(I) / avg_window
    Q = np.array(Q) / avg_window
    
    return I, Q, I_NCO, Q_NCO, new_gate_tlist


# Calculate the fidelity of bin-counting and single-point methods.
def calculate_fidelity(result_I0, result_Q0, result_I1, result_Q1, simul_time, num_steps, params, readout_duration, steady_state_start_time):
    times = np.linspace(0.0, simul_time, num_steps) # ns
    nan_idx = list()
    for idx, result in enumerate(result_I0.copy()):
        if np.isnan(result).sum() > 0:
            nan_idx.append(idx)
    result_I0 = np.delete(result_I0, nan_idx, 0)
    nan_idx = list()
    for idx, result in enumerate(result_Q0.copy()):
        if np.isnan(result).sum() > 0:
            nan_idx.append(idx)
    result_Q0 = np.delete(result_Q0, nan_idx, 0)
    nan_idx = list()
    for idx, result in enumerate(result_I1.copy()):
        if np.isnan(result).sum() > 0:
            nan_idx.append(idx)
    result_I1 = np.delete(result_I1, nan_idx, 0)
    nan_idx = list()
    for idx, result in enumerate(result_Q1.copy()):
        if np.isnan(result).sum() > 0:
            nan_idx.append(idx)
    result_Q1 = np.delete(result_Q1, nan_idx, 0)

    I0_list = list()
    Q0_list = list()
    I1_list = list()
    Q1_list = list()
    I0_avg_list = list()
    Q0_avg_list = list()
    I1_avg_list = list()
    Q1_avg_list = list()
    new_gate_tlist = 0

    simuls0 = [extract_iq_ray.remote(add_noise(I_0 + Q_0, simul_time/num_steps), times, params, avg_window=8) for I_0, Q_0 in zip(result_I0, result_Q0)]
    simuls1 = [extract_iq_ray.remote(add_noise(I_1 + Q_1, simul_time/num_steps), times, params, avg_window=8) for I_1, Q_1 in zip(result_I1, result_Q1)]
    results0 = np.array(ray.get(simuls0))
    results1 = np.array(ray.get(simuls1))
    new_gate_tlist = results0[0,4]
    I0_list = results0[:,2]
    Q0_list = results0[:,3]
    I1_list = results1[:,2]
    Q1_list = results1[:,3]
    I0_avg_list = results0[:,0]
    Q0_avg_list = results0[:,1]
    I1_avg_list = results1[:,0]
    Q1_avg_list = results1[:,1]

    I0_integrated = list()
    Q0_integrated = list()
    I1_integrated = list()
    Q1_integrated = list()

    new_num_steps = len(new_gate_tlist)
    new_time_interval = (new_gate_tlist[1]-new_gate_tlist[0])
    interval_step = int(2 / new_time_interval)

    for I_0, Q_0 in zip(I0_list, Q0_list):
        I0_temp = list()
        Q0_temp = list()

        for k in range(int(new_num_steps / interval_step)):
            I0_temp.append(I_0[ : (k + 1) * interval_step].mean())
            Q0_temp.append(Q_0[ : (k + 1) * interval_step].mean())
        I0_integrated.append(I0_temp)
        Q0_integrated.append(Q0_temp)

    for I_1, Q_1 in zip(I1_list, Q1_list):
        I1_temp = list()
        Q1_temp = list()

        for k in range(int(new_num_steps / interval_step)):
            I1_temp.append(I_1[ : (k + 1) * interval_step].mean())
            Q1_temp.append(Q_1[ : (k + 1) * interval_step].mean())
        I1_integrated.append(I1_temp)
        Q1_integrated.append(Q1_temp)

    I0_integrated = np.array(I0_integrated)
    Q0_integrated = np.array(Q0_integrated)
    I1_integrated = np.array(I1_integrated)
    Q1_integrated = np.array(Q1_integrated)
    I0_integrated_std = I0_integrated.std(axis=0)
    Q0_integrated_std = Q0_integrated.std(axis=0)
    I1_integrated_std = I1_integrated.std(axis=0)
    Q1_integrated_std = Q1_integrated.std(axis=0)

    # Single point method readout error rate
    integrated_times = np.linspace(2, simul_time, len(I0_integrated_std), endpoint=True)
    readout_duration_idx = int(readout_duration / (integrated_times[1] - integrated_times[0])) - 1

    line, _, _ = get_line_from_iq(I0_integrated[:, readout_duration_idx], Q0_integrated[:, readout_duration_idx], I1_integrated[:, readout_duration_idx], Q1_integrated[:, readout_duration_idx])
    params0, params1, prob_0_roi, prob_1_roi, e_g_error, g_e_error = single_point_get_fidelity(I0_integrated[:, readout_duration_idx], Q0_integrated[:, readout_duration_idx], I1_integrated[:, readout_duration_idx], Q1_integrated[:, readout_duration_idx], 
                        line, len(I0_integrated), params = {'hist_bins': 50}, options = {'verbose': True})
    print("Total error = {:.3f}%, e|g error = {:.3f}%, g|e error = {:.3f}%".format((e_g_error + g_e_error)/2 * 100, e_g_error * 100, g_e_error * 100))

    # Bin-counting method readout error rate
    bin_counting_readout_duration_idx = int(readout_duration / (new_gate_tlist[1] - new_gate_tlist[0])) - 1
    steady_state_start_idx = int(steady_state_start_time / (new_gate_tlist[1] - new_gate_tlist[0])) - 1

    bin_counting_line, state_0_center, state_1_center = get_line_from_iq (
                I0_avg_list.mean(axis=0),
                Q0_avg_list.mean(axis=0),
                I1_avg_list.mean(axis=0),
                Q1_avg_list.mean(axis=0)
            )
    total_error = 0
    num_shot = 0
    if len(I0_avg_list) > len(I1_avg_list):
        num_shot = len(I1_avg_list)
    else:
        num_shot = len(I0_avg_list)

    bin_counting_simuls = [
        bin_counting_get_fidelity_ray.remote (
                    I_0[steady_state_start_idx:bin_counting_readout_duration_idx],
                    Q_0[steady_state_start_idx:bin_counting_readout_duration_idx],
                    I_1[steady_state_start_idx:bin_counting_readout_duration_idx],
                    Q_1[steady_state_start_idx:bin_counting_readout_duration_idx],
                    bin_counting_line,
                    len(I_0),
                    params = {'hist_bins': 50},
                    options = {'verbose': False}
                )
        for I_0, Q_0, I_1, Q_1 in zip(I0_avg_list[:num_shot], Q0_avg_list[:num_shot], I1_avg_list[:num_shot], Q1_avg_list[:num_shot])
    ]

    bin_counting_results = np.array(ray.get(bin_counting_simuls))
    total_error = np.sum(bin_counting_results)
    print("Bin-counting method error = {:.3f}%".format(total_error / num_shot * 100))


# max_photon_num: 8~10 is appropriate following [1,2].
# w_r: We use the obtained IBMQ value following [3].
# pulse_power: -131~-121dBm is appropriate following [2]

# [1] Hoffer, Cole R. Superconducting qubit readout pulse optimization using deep reinforcement learning. Diss. MIT, 2021.
# [2] Sank, Daniel Thomas. Fast, Accurate State Measurement in Superconducting Qubits. Diss. UCSB, 2014.
# [3] https://qiskit.org/textbook/ch-quantum-hardware/Jaynes-Cummings-model.html

def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--simulation_time", "-s", help="Simulation time [ns]", type=int, default=517)
    parser.add_argument ("--ringup_time", "-r", help="Ring-up time of the resonator [ns]", type=int, default=117)
    parser.add_argument ("--max_photon_num", "-p", help="Number of photons in the resonator", type=int, default=10)
    parser.add_argument ("--freq_qubit", "-fq", help="Qubit frequency [GHz]", type=float, default=5)
    parser.add_argument ("--freq_resonator", "-fr", help="Resonator frequency [GHz]", type=float, default=6)
    parser.add_argument ("--freq_lo", "-fl", help="Local oscillator frequency [GHz]", type=float, default=6)
    parser.add_argument ("--chi", "-fc", help="Chi of qubit-resonator coupled systems [GHz]", type=float, default=0.0015)
    parser.add_argument ("--kappa", "-fk", help="Kappa of qubit-resonator coupled systems [GHz]", type=float, default=0.006525)
    parser.add_argument ("--relax", "-t1", help="Relaxation time (i.e., T1 time) [ns]", type=int, default=122000)
    parser.add_argument ("--coherence", "-t2", help="Coherence time (i.e., T2 time) [ns]", type=int, default=118000)
    parser.add_argument ("--pulse_power", "-pp", help="Pulse power of TX circuit [dBm]", type=int, default=-122)
    parser.add_argument ("--num_shot", "-n", help="Number of independent measurements for simulation", type=int, default=1024)
    args = parser.parse_args ()
    return args


if __name__ == "__main__":
    args = arg_parse ()
    simul_time = args.simulation_time # ns
    input_pulse_duration = simul_time # ns
    steady_state_start_time = args.ringup_time # ns
    readout_duration = simul_time # ns
    num_steps = simul_time*100
    max_photon_num = args.max_photon_num

    chi = args.chi # GHz
    w_r = args.freq_resonator # GHz
    w_q = args.freq_qubit # GHz
    w_LO = args.freq_lo # GHz
    w_d = w_r # GHz
    kappa = args.kappa # GHz
    T1 = args.relax # ns
    T2 = args.coherence # ns
    pulse_power_dbm = args.pulse_power # dBm
    num_shot = args.num_shot

    h_bar = 1.0545718e-34 # Js; Planck constant
    amp = np.power(10, pulse_power_dbm / 10 - 3) * (simul_time / num_steps) / h_bar / 1e9 / 1e9 # GHz

    ntraj = 1
    nsubsteps = 50
    
    # Readout error
    print("Start readout error simulation")
    # Params for TX circuit (../1q_gate/single_error_model.py)
    filter_params = {"device_frequency": 2.5e9, "output_precision": 10, "filter_type": "ideal_low_pass_filter", "cutoff_frequency": 1.25e9, "amplifier_type": "abs_area_ratio"}
    params = {'dt': simul_time/num_steps, 'pulse power': pulse_power_dbm, 'V0': amp, 'w_d': (w_d - w_LO), 'w_LO': w_LO, 'w_q': w_q, 'w_r': w_r, 'kappa': kappa, 
            'T1': T1, 'T2': T2, 'chi': chi}
    sme_args = {'simul_time': simul_time, 'num_steps': num_steps, 'max_photon_num': max_photon_num, 'ntraj': ntraj, 'nsubsteps': nsubsteps}
    print(params)
    print(sme_args)

    print("Num shot = {}".format(num_shot))

    if (not os.path.isfile ("IQ_results/new_model_I0_{:.3f}_{}_{}_{}shot".format(amp, T1, T2, num_shot))) or \
        (not os.path.isfile ("IQ_results/new_model_I0_{:.3f}_{}_{}_{}shot".format(amp, T1, T2, num_shot))) or \
        (not os.path.isfile ("IQ_results/new_model_I0_{:.3f}_{}_{}_{}shot".format(amp, T1, T2, num_shot))) or \
        (not os.path.isfile ("IQ_results/new_model_I0_{:.3f}_{}_{}_{}shot".format(amp, T1, T2, num_shot))):
        simuls = [SMEsolver.remote(sme_args, params, filter_params, input_pulse_duration) for _ in range(num_shot)]
        print ("get IQ_results...")
        results = np.array(ray.get(simuls))
        ray.shutdown()

        result_I0 = results[:,0,:]
        result_Q0 = results[:,1,:]
        result_I1 = results[:,2,:]
        result_Q1 = results[:,3,:]

        np.savetxt("IQ_results/new_model_I0_{:.3f}_{}_{}_{}shot".format(amp, T1, T2, num_shot), result_I0)
        np.savetxt("IQ_results/new_model_Q0_{:.3f}_{}_{}_{}shot".format(amp, T1, T2, num_shot), result_Q0)
        np.savetxt("IQ_results/new_model_I1_{:.3f}_{}_{}_{}shot".format(amp, T1, T2, num_shot), result_I1)
        np.savetxt("IQ_results/new_model_Q1_{:.3f}_{}_{}_{}shot".format(amp, T1, T2, num_shot), result_Q1)
        
    result_I0 = np.loadtxt("IQ_results/new_model_I0_{:.3f}_{}_{}_{}shot".format(amp, T1, T2, num_shot), dtype=float)
    result_Q0 = np.loadtxt("IQ_results/new_model_Q0_{:.3f}_{}_{}_{}shot".format(amp, T1, T2, num_shot), dtype=float)
    result_I1 = np.loadtxt("IQ_results/new_model_I1_{:.3f}_{}_{}_{}shot".format(amp, T1, T2, num_shot), dtype=float)
    result_Q1 = np.loadtxt("IQ_results/new_model_Q1_{:.3f}_{}_{}_{}shot".format(amp, T1, T2, num_shot), dtype=float)
    
    calculate_fidelity(result_I0, result_Q0, result_I1, result_Q1, simul_time, num_steps, params, readout_duration, steady_state_start_time)
