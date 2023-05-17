from sfqlib import *
from math import pi, ceil
import numpy as np
from multiprocessing import Pool
import os, json, argparse
from qiskit.quantum_info.operators import Operator
from qiskit.quantum_info import process_fidelity

# 1. RY(pi/2) GATES.

# Pulse with [1,0,0,0,0] sequence; naive case (qubit.resonance).
# One Z rotation -> One SFQ pulse.
def get_fidelity_without_opt (d_theta, freq_clock=24, freq_qubit=4):
    qubit = Sfq3LevelQubit(d_theta=d_theta, w_clock=2*pi*freq_clock*1e9, \
                w_qubit=(2*pi*freq_qubit*1e9, 2*pi*9.75e9), theta=pi/2)
    qubit.resonance ()
    fidelity = qubit.measure_fidelity ()
    return fidelity


def get_fidelity (pulse, d_theta, freq_clock=24, freq_qubit=4):
    qubit = Sfq3LevelQubit(d_theta=d_theta, w_clock=2*pi*freq_clock*1e9, \
                w_qubit=(2*pi*freq_qubit*1e9, 2*pi*9.75e9), theta=pi/2)
    qubit.pulse_pattern (pulse)
    #qubit.resonance ()
    fidelity = qubit.measure_fidelity ()
    return fidelity


# Initial palindrome pulse (unoptimized).
def get_initial_pulse (cyc_pulse, freq_clock=24, freq_qubit=4):
    cyc_qubit = int (freq_qubit * cyc_pulse / freq_clock)
    pulse = []
    for cyc_ in range (cyc_pulse):
        val_ = (float (cyc_qubit) * float (cyc_) / float (cyc_pulse))%1
        if val_ <= 0.25 or val_ >= 0.75:
            pulse.append (1)
        else:
            pulse.append (0)
    pulse.reverse ()
    return pulse


# Find appropriate theta to maximize fidelity.
def find_theta (pulse, freq_clock, freq_qubit):
    d_thetas = list (np.linspace (0, pi/100, 100))
    fidelities = []
    for d_theta in d_thetas:
        fidelity = get_fidelity (pulse.copy (), d_theta, freq_clock, freq_qubit)
        fidelities.append (fidelity)
    max_fid = max (fidelities)
    for d_theta_, fidelity_ in zip (d_thetas, fidelities):
        if fidelity_ == max_fid:
            return d_theta_, fidelity_


# SCALLOPS algorithm with BFS.
def optimizer_thread (cyc_pulse, freq_clock, freq_qubit, arr, max_fidelity, global_results, thread_num):
    max_pulse = None
    max_theta = None
    for (m_, loc_, max_pulse_past_) in arr:
        pulse_ = max_pulse_past_.copy ()
        pulse_[loc_] = (pulse_[loc_]+1)%2
        pulse_[int (m_*freq_clock/freq_qubit*2-loc_)] = (pulse_[loc_]+1)%2
        theta, fidelity = find_theta (pulse_, freq_clock, freq_qubit)
        if fidelity > max_fidelity:
            max_fidelity = fidelity
            max_pulse = pulse_
            max_theta = theta
    if max_pulse == None:
        return (None, None, None)
    return (max_fidelity, max_pulse, max_theta)


# Multi-threaded SCALLOPS algorithm.
def optimizer (cyc_pulse, freq_clock, freq_qubit, depth):
    
    max_pulses_past = [get_initial_pulse (cyc_pulse, freq_clock, freq_qubit)]
    max_pulses_curr = []
    max_fidelity_past = find_theta (max_pulses_past[0], freq_clock, freq_qubit)[1]
    max_fidelity_curr = None
    good_results = []
    num_cpu = os.cpu_count ()

    #print ("\nOptimizer starts.")
    for depth_ in range (depth):
        #print ("[Depth {}]".format (depth_+1))
        cyc_qubit = int (freq_qubit * cyc_pulse / freq_clock)
        todo = []
        for max_pulse_past in max_pulses_past:
            for m_ in range (cyc_qubit):
                for loc_ in range (cyc_pulse):
                    if m_*freq_clock/freq_qubit <= loc_:
                        break
                    if m_*freq_clock/freq_qubit*2 - loc_ >= cyc_pulse:
                        continue
                    todo.append ((m_, loc_, max_pulse_past))
        #print ("{} jobs for {} pulses.".format (len (todo), len (max_pulses_past)))
        
        len_per_thread = ceil(len (todo)/num_cpu)
        ps = []
        global_results = [None] * num_cpu
        pool = Pool (num_cpu)
        for thread in range (num_cpu):
            if (thread+1)*len_per_thread < len (todo):
                arr = todo[thread*len_per_thread:(thread+1)*len_per_thread].copy ()
            else:
                arr = todo[thread*len_per_thread:-1].copy ()
            ps.append (pool.apply_async (optimizer_thread, \
                (cyc_pulse, freq_clock, freq_qubit, arr, max_fidelity_past, global_results, thread)))
        
        global_results = [global_result.get () for global_result in ps]

        fidelities = []
        for fidelity_, pulse_, theta_ in global_results:
            if pulse_ == None:
                continue
            if fidelity_ > 0.9999:
                good_results.append ([fidelity_, pulse_, theta_])
            max_pulses_curr.append (pulse_)
            fidelities.append (fidelity_)
        if len (max_pulses_curr) == 0 or len (fidelities) == 0:
            break
        max_fidelity_curr = max (fidelities)

        #print ("Fidelity: {}\n".format (max_fidelity_curr))
        if max_fidelity_past >= max_fidelity_curr:
            break
        max_pulses_past = max_pulses_curr.copy ()
        max_pulses_curr = []
        max_fidelity_past = max_fidelity_curr

    #print ("Optimizer ends.")
    f = open ("1q_results/{}_{}_{}_{}".format (cyc_pulse, freq_clock, freq_qubit, depth), "w")
    json.dump (good_results, f)
    f.close ()
    return max_fidelity_past


# 2. RZ gate.

# Get the worst-case RZ gate fidelity for a given condition.
def rz_fidelity (freq_clock, freq_qubit, length):
    precision = freq_qubit/freq_clock*(2*pi)
    angles = list ()
    for n in range (length+1):
        angles.append ((precision*n)%(2*pi))
    angles = list (set (angles))
    angles.sort ()

    min_fidelity = 1
    max_fidelity = 0
    for index in range (len (angles)):
        if index == len (angles)-1:
            break
        angle_1 = angles[index]
        angle_2 = angles[index+1]
        angle_ref = (angle_1 + angle_2)/2
        rz_gate_1 = Operator (np.array ([[np.exp(-1.0j/2*angle_1), 0], [0, np.exp(1.0j/2*angle_1)]], dtype=np.complex128))
        rz_gate_2 = Operator (np.array ([[np.exp(-1.0j/2*angle_2), 0], [0, np.exp(1.0j/2*angle_2)]], dtype=np.complex128))
        rz_gate_ref = Operator (np.array ([[np.exp(-1.0j/2*angle_ref), 0], [0, np.exp(1.0j/2*angle_ref)]], dtype=np.complex128))

        fidelity_1 = process_fidelity (rz_gate_1, rz_gate_ref)
        fidelity_2 = process_fidelity (rz_gate_2, rz_gate_ref)
        min_fidelity = min (min_fidelity, fidelity_1, fidelity_2)
        max_fidelity = max (max_fidelity, fidelity_1, fidelity_2)
    return min_fidelity, max_fidelity


def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--freq_clock", "-c", help="Hardware clock frequency [GHz]", type=float, default=24)
    parser.add_argument ("--freq_qubit", "-q", help="Qubit resonating frequency [GHz]", type=float, default=4.14238)
    parser.add_argument ("--max_y_length", "-y", help="Maximum target length of Y(pi/2) bitstream", type=int, default=300)
    parser.add_argument ("--z_length", "-z", help="Target length of RZ (i.e., RZ-gate precision)", type=int, default=256)
    parser.add_argument ("--depth", "-d", help="Depth of design space exploration", type=int, default=3)
    args = parser.parse_args ()
    return args


if __name__ == "__main__":

    args = arg_parse ()
    freq_clock = args.freq_clock
    freq_qubit = args.freq_qubit
    max_y_length = args.max_y_length
    z_length = args.z_length
    search_depth = args.depth

    # Initial pulse-length setting.
    ## find the error-minimizing pulse length using palindrome method.
    prev_max = 0
    y_length = 0
    for length_ in range (max_y_length):
        pulse = get_initial_pulse (length_, freq_clock, freq_qubit)
        _, fidelity = find_theta (pulse, freq_clock, freq_qubit)
        if fidelity > prev_max:
            prev_max = fidelity
            y_length = length_
    print ("\nOptimal RY-pulse length (1~{}):\t{}\n".format (max_y_length, y_length))
    
    # RZ gate fidelity.
    print ("1. RZ gate fidelity")
    min_fidelity, max_fidelity = rz_fidelity (freq_clock, freq_qubit, z_length)
    print ("\tWorst case:\t\t{}".format (min_fidelity))
    print ("\tBest case:\t\t{}\n".format (max_fidelity))

    # RY(pi/2) gate fidelity.
    print ("2. RY(pi/2) gate fidelity")
    print ("\tResonance:\t\t{}".format (get_fidelity_without_opt (pi/2/50, freq_clock, freq_qubit)))
    pulse = get_initial_pulse (y_length, freq_clock, freq_qubit)
    print ("\tInitial palindrome:\t{}".format (find_theta (pulse, freq_clock, freq_qubit)[1]))
    print ("\tSCALLOPS:\t\t{}".format (optimizer (y_length, freq_clock, freq_qubit, search_depth)))
