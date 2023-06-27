import numpy as np
from qutip import *
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from JC import *
import argparse


# Calculate sfq-pulse amplitude with the ratio of cmos power and sfq power
def _convert_dBm_power_to_peak_voltage (power, impedance=50):
    rms_voltage = np.sqrt(impedance/1000.0) * (10**(power/20.0))
    peak_voltage = np.sqrt(2) * rms_voltage # Assumed sinusoidal wave
    return (peak_voltage * 1e3)


# Convert CMOS-pulse amplitude from GHz to mV
def calc_amplitude (input_type, amp_cmos_ghz, power_cmos_dbm, amp_sfq_mv, impedance):
    if input_type == "cmos":
        amp = amp_cmos_ghz
        num_pulse_train = 1
    elif input_type == "sfq":
        # Single SFQ pulse: 1mV amplitude, 2ps pulse duration
        amp_cmos_mv = _convert_dBm_power_to_peak_voltage (power_cmos_dbm, impedance) # [mV]
        voltage_ratio = (amp_sfq_mv / amp_cmos_mv)
        amp_sfq = amp_cmos_ghz * voltage_ratio # GHz
        
        amp = amp_sfq
        num_pulse_train = int(np.trunc(50 / voltage_ratio))
    else:
        raise Exception ("Invalid input_type: {}. Set input_type as 'cmos' or 'sfq'".format(input_type))

    return (amp, num_pulse_train)


# Hamiltonian simulation for the resonator-driving stage.
def drive_stage (input_type, sim_time, num_steps, fq, fr, fj, gq, gj, amp, max_photon_num, dip_num, device_freq, num_pulse_train=1):
    chi_q = (gq**2 / (fr - fq)) # dispersive shift of resonator due to qubit-resonator coupling.
    chi_j = (gj**2 / (fr - fj)) # dispersive shift of resonator due to JPM-resonator coupling.
    fd = fr - chi_q + chi_j # resonator drive frequency (= fr_tilda1)
    fr_tilda0 = fr + chi_q + chi_j # dispersive-shifted resonator frequency when the qubit is |0> state
    fr_tilda1 = fr - chi_q + chi_j # dispersive-shifted resonator frequency when the qubit is |1> state
    td = 1 / (2 * chi_q) # [ns] the time difference between the dips
    num_steps += 1
    times = np.linspace(0.0, sim_time, num_steps) # ns
    psi0 = fock(max_photon_num, 0) # resonator initial state
    a = destroy(max_photon_num) # annihilation operator

    H_0state = 2 * np.pi * fr_tilda0 * a.dag() * a # resonator's Hamiltonian when the initial qubit state is |0> 
    H_1state = 2 * np.pi * fr_tilda1 * a.dag() * a # resonator's Hamiltonian when the initial qubit state is |1> 
    Hd = a + a.dag() # resonator drive pulse Hamiltonian before multiplying the pulse coefficient
    
    # For SFQ pulse train design
    td_fs = int(1/fd * 1e6) # fs
    device_dt_fs = int(1 / device_freq * 1e6) # fs
    dt = times[1] - times[0] # ns
    dt_fs = int(dt * 1e6) # fs

    def Hd_coeff_cmos (t, args):
        return 2 * np.pi * amp * np.cos(2 * np.pi * fd * t)

    # num_pulse_train: indicates how many SFQ pulses within the half-resonator period.
    # Hd_coeff_sfq: generate the corresponding SFQ-pulse train following num_pulse_train.
    def Hd_coeff_sfq (t, args):
        cond = any([((i * device_dt_fs) <= (int(t*1e6) % (td_fs)) < (i * device_dt_fs + dt_fs)) for i in range(num_pulse_train)])
        return 2 * np.pi * amp * (1 if cond else 0)
    
    # input Hamiltonians for sesolve Simulation (to match the format).
    if input_type == "cmos":
        H0 = [H_0state, [Hd, Hd_coeff_cmos]]
        H1 = [H_1state, [Hd, Hd_coeff_cmos]]
    elif input_type == "sfq":
        H0 = [H_0state, [Hd, Hd_coeff_sfq]] 
        H1 = [H_1state, [Hd, Hd_coeff_sfq]]
    
    print("---- Setup ----")
    print("Input type : {}, device freq : {}, qubit freq : {}, resonator freq : {}, JPM freq : {}, qubit-resonator coupling : {}, JPM-resonator coupling : {}, \
    Input pulse amplitude : {}, max photon number : {}, dip number : {}, num_pulse_train: {}".format \
        (input_type, device_freq, fq, fr, fj, gq, gj, amp, max_photon_num, dip_num, num_pulse_train))
    print("---------------")
    result0 = sesolve(H0, psi0, times, [a]) 
    result1 = sesolve(H1, psi0, times, [a])

    alpha_norm_list0 = np.abs(result0.expect[0]) ** 2 # #of photons when the initial qubit state is |0>
    alpha_norm_list1 = np.abs(result1.expect[0]) ** 2 # #of photons when the initial qubit state is |1>

    dip_idx = np.argmin(alpha_norm_list0[int((dip_num * td - td / 2) * num_steps / sim_time):int((dip_num * td + td / 2) * num_steps / sim_time)]) \
            + int((dip_num * td - td / 2) * num_steps / sim_time)
    alpha_norm0 = alpha_norm_list0[dip_idx]
    alpha_norm1 = alpha_norm_list1[dip_idx]
    print("0 state |alpha|^2 at {} dip : {}".format(dip_num, alpha_norm0))
    print("1 state |alpha|^2 at {} dip : {}".format(dip_num, alpha_norm1))
    print("Resonator drive stage duration = {}ns\n".format(times[dip_idx]))

    plt.figure()
    plt.plot(times[1:], np.log10(alpha_norm_list0[1:]), label='0 state')
    plt.plot(times[1:], np.log10(alpha_norm_list1[1:]), label='1 state')
    plt.annotate("{:.1f} ns".format(times[dip_idx]), xy = (times[dip_idx] + 10, np.log10(alpha_norm0) - 0.5))
    plt.axvline(times[dip_idx], color="r", linestyle="--")
    plt.axhline(np.log10(alpha_norm0), color="r", linestyle="--")
    plt.axhline(np.log10(alpha_norm1), color="r", linestyle="--")
    plt.title("0 state : {:.3E}, 1 state : {:.3E}".format(alpha_norm0, alpha_norm1))
    plt.legend()
    plt.xlabel("time (ns)")
    plt.ylabel("|alpha|^2")
    plt.savefig("JPM_preparation_results/alpha/{}GHz_{}_{}train_{:.3f}_{:.3f}_{:.3f}_{:.3f}_{:.3f}_{:.5f}_{}_{}.png".format \
                (device_freq, input_type, num_pulse_train, fq, fr, fj, gq, gj, amp, max_photon_num, dip_num))

    # Get final cavity state alpha.
    state_result0 = sesolve(H0, psi0, times, [])
    state_result1 = sesolve(H1, psi0, times, [])

    alpha0 = state_result0.states[dip_idx] # initial resonator state for the tunneling stage when initial qubit state was |0>
    alpha1 = state_result1.states[dip_idx] # initial resonator state for the tunneling stage when initial qubit state was |1>

    return alpha_norm0, alpha_norm1, alpha0, alpha1, device_freq


# Hamiltonian simulation for the JPM-tunneling stage.
def JPM_tunneling_stage(device_freq, num_pulse_train, alpha0, alpha1, sim_time, num_steps, T1, T2, gamma_e, gamma_g, fq, fr, fj, gq, gj, amp, max_photon_num, dip_num):
    times = np.linspace(0.0, sim_time, num_steps) # ns
    a = destroy(max_photon_num)
    H = 2 * np.pi * gj * (tensor(a.dag(), Qobj([[0., 1., 0.], [0., 0., 0.], [0., 0., 0.]])) + tensor(a, Qobj([[0., 0., 0.], [1., 0., 0.], [0., 0., 0.]]))) # resonator-JPM coupled system Hamiltonian

    # Lindblad operations for Lindblad master equation
    C0 = np.sqrt(2 * np.pi * gamma_g) * tensor(qeye(max_photon_num), Qobj([[0., 0., 0.], [0., 0., 0.], [1., 0., 0.]])) # JPM |g> state tunneling operator
    C1 = np.sqrt(2 * np.pi * gamma_e) * tensor(qeye(max_photon_num), Qobj([[0., 0., 0.], [0., 0., 0.], [0., 1., 0.]])) # JPM |e> state tunneling operator
    C2 = np.sqrt(2 * np.pi / T2) * tensor(qeye(max_photon_num), Qobj([[0., 0., 0.], [0., 1., 0.], [0., 0., 0.]])) # JPM pure dephasing
    C3 = np.sqrt(2 * np.pi / T1) * tensor(qeye(max_photon_num), Qobj([[0., 1., 0.], [0., 0., 0.], [0., 0., 0.]])) # JPM energy relaxation

    psi0 = tensor(alpha0, basis(3, 0)) # resonator state after resonator drive stage when initial qubit state was |0>
    psi1 = tensor(alpha1, basis(3, 0)) # resonator state after resonator drive stage when initial qubit state was |1>
    c_ops = []
    # as the T2 time merely affects the final result, we set the T2 time to 1000ns to reduce the simulation time.
    if T2 >= 1000:
        c_ops = [C0, C1, C3]
    else:
        c_ops = [C0, C1, C2, C3]

    readout_result0 = mesolve(H, psi0, times, c_ops, [])
    readout_result1 = mesolve(H, psi1, times, c_ops, [])

    states0 = readout_result0.states
    states1 = readout_result1.states
    detection_prob_list0 = [] # JPM detection probability after JPM tunneling when initial qubit state is |0>
    detection_prob_list1 = [] # JPM detection probability after JPM tunneling when initial qubit state is |1>

    # Extract the JPM state only from the state vector of resonator-JPM coupled system.
    m_list = np.arange(0, max_photon_num, 1, dtype=int) * 3 + 2 
    for s0, s1 in zip(states0, states1):
        detection_prob_list0.append(s0.extract_states(m_list).norm())
        detection_prob_list1.append(s1.extract_states(m_list).norm())

    detection_prob_list0 = np.array(detection_prob_list0) ** 2
    detection_prob_list1 = np.array(detection_prob_list1) ** 2

    contrast = detection_prob_list1 - detection_prob_list0 # = readout fidelity
    opt_fidelity = np.max(contrast) # Optimal fidelity
    opt_fidelity_idx = np.argmax(contrast) 
    opt_measure_duration = times[opt_fidelity_idx] # tunneling-stage duration for the optimal fidelity

    plt.figure()
    plt.plot(times, detection_prob_list0, label='0 state')
    plt.plot(times, detection_prob_list1, label='1 state')
    plt.axvline(opt_measure_duration, color="r", linestyle="--")
    plt.annotate("{:.4f}".format(detection_prob_list0[opt_fidelity_idx]), xy = (opt_measure_duration + 5, detection_prob_list0[opt_fidelity_idx] + 0.005))
    plt.annotate("{:.4f}".format(detection_prob_list1[opt_fidelity_idx]), xy = (opt_measure_duration + 5, detection_prob_list1[opt_fidelity_idx] + 0.005))
    plt.title("Fidelity = {:.4f} %, Duration = {:.1f}".format(opt_fidelity * 100, opt_measure_duration))
    plt.legend()
    plt.xlabel("time (ns)")
    plt.ylabel("Detection probability")
    plt.savefig("JPM_preparation_results/detection_prob/{}GHz_{}_{}train_{:.3f}_{:.3f}_{:.3f}_{:.3f}_{:.3f}_{:.5f}_{}_{}_{}_{}_{:.3f}_{:.5f}.png".format(device_freq, input_type, num_pulse_train, fq, fr, fj, gq, gj, amp, max_photon_num, dip_num, T1, T2, gamma_e, gamma_g))

    print ("Fidelity = {:.4f}%, JPM-tunneling stage duration = {:.1f}ns".format(opt_fidelity * 100, opt_measure_duration))
    return detection_prob_list0, detection_prob_list1, times, opt_fidelity, opt_measure_duration


# JPM full state-preparation stage (driving + tunneling)
def full_stage(input_type, sim_time, num_steps, fq, fr, fj, gq, gj, amp, max_photon_num, dip_num, device_freq, T1, T2, gamma_e, gamma_g, num_pulse_train):
    print("Start the resonator-driving stage")
    _, _, alpha0, alpha1, _ = drive_stage(input_type, sim_time, num_steps, fq, fr, fj, gq, gj, amp, max_photon_num, dip_num, device_freq, num_pulse_train)
    print("Start the JPM-tunneling stage")
    JPM_tunneling_stage(device_freq, num_pulse_train, alpha0, alpha1, 50, 25000, T1, T2, gamma_e, gamma_g, fq, fr, fj, gq, gj, amp, max_photon_num, dip_num)


def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--simulation_time", "-s", help="Simulation time [ns]", type=int, default=750)
    parser.add_argument ("--freq_qubit", "-fq", help="Qubit frequency [GHz]", type=float, default=4.14238)
    parser.add_argument ("--freq_resonator", "-fr", help="Resonator frequency [GHz]", type=float, default=6.008188)
    parser.add_argument ("--freq_jpm", "-fj", help="JPM frequency [GHz]", type=float, default=7.008188)
    parser.add_argument ("--coupling_qr", "-cqr", help="Qubit-resonator coupling strength [GHz]", type=float, default=0.09)
    parser.add_argument ("--coupling_rj", "-crj", help="Resonator-JPM coupling strength [GHz]", type=float, default=0.062)
    parser.add_argument ("--input_type", "-t", help="The type of resonator-driving pulses (i.e., cmos, sfq)", type=str, default="sfq")
    parser.add_argument ("--relax", "-t1", help="JPM relaxation time [ns]", type=int, default=5)
    args = parser.parse_args ()
    return args


if __name__ == "__main__":

    args = arg_parse ()
    fq = args.freq_qubit # [GHz] qubit freq
    fr = args.freq_resonator # [GHz] resonator freq
    fj = args.freq_jpm # [GHz] JPM freq
    gq = args.coupling_qr # [GHz] coupling strength of qubit-resonator
    gj = args.coupling_rj # [GHz] coupling strength of JPM-resonator

    input_type = args.input_type
    device_freq = 24 # [GHz] SFQ hardware frequency
    sim_time = args.simulation_time # ns
    num_steps = sim_time*500
    dip_num = 5 # the dip with minimum error rate.
    max_photon_num = 100

    T1 = args.relax # [ns] JPM T1 time of [Opremcak'21]
    T2 = 1000   # [ns] JPM T2 time which does not significantly change the final result
                # (Opremcak did not show the JPM T2 time.)
    gamma_e = 0.2 # [GHz] tunneling rate of JPM excited state
    gamma_g = 0.001 # [GHz] tunneling rate of JPM ground state

    amp_cmos_ghz = 0.0158 # CMOS pulse power in GHz
    power_cmos_dbm = -67 # CMOS drive power following [Opremcak'14,21]
    amp_sfq_mv = 1.035 # SFQ pulse amplitude
    impedance = 50
    amp, _ = calc_amplitude (input_type, amp_cmos_ghz, power_cmos_dbm, amp_sfq_mv, impedance)

    # Single simulation
    num_pulse_train = 1
    print("amp: {}, num_pulse_train: {}".format(amp, num_pulse_train))
    full_stage(input_type, sim_time, num_steps, fq, fr, fj, gq, gj, amp, max_photon_num, dip_num, device_freq, T1, T2, gamma_e, gamma_g, num_pulse_train)
