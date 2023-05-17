#!/usr/bin/python3.8
from Quanlse.QHamiltonian import QHamiltonian as QHam
from Quanlse.QOperator import duff, number
from Quanlse.remoteOptimizer import remoteOptimizeCz
from Quanlse.Utils.Functions import project
import Quanlse
from Quanlse import Define
from Quanlse.QWaveform import QJob
from math import *
import numpy as np
import os, argparse


# Get the ideal CZ pulse from the Baidu cloud.
def get_ideal_cz_pulse (qubit_freq0, qubit_freq1, gate_time, iteration):

    print ("Get ideal pulse by running Quanlse in Baidu cloud...", end=" ")
    # To use remoteOptimizerCz() on cloud, paste your token (a string) here
    Define.hubToken = ''
    if Define.hubToken == '':
        print ("\n[ERROR] Please insert appropriate token.")
        exit ()
    # Sampling period
    dt = 0.2
    # Number of qubits
    qubits = 2
    # System energy levels
    level = 3
    # Initilize the Hamiltonian
    ham = QHam(subSysNum=qubits, sysLevel=level, dt=dt)

    qubitArgs = {
        "coupling": 0.0277 * (2 * pi),  # Coupling of Q0 and Q1
        "qubit_freq0": qubit_freq0 * (2 * pi),  # Frequency of Q0
        "qubit_freq1": qubit_freq1 * (2 * pi),  # Frequency of Q1
        "drive_freq0": qubit_freq1 * (2 * pi),  # Drive frequency on Q0 (rotating frame)
        "drive_freq1": qubit_freq1 * (2 * pi),  # Drive frequency on Q1 (rotating frame)
        "qubit_anharm0": -0.250 * (2 * pi),  # Anharmonicity of Q0
        "qubit_anharm1": -0.250 * (2 * pi)  # Anharmonicity of Q1
    }

    # Add drift term(s)
    for qu in range(2):
        # Add detuning term(s)
        ham.addDrift(number, qu, (qubitArgs[f"qubit_freq{qu}"] - qubitArgs[f"drive_freq{qu}"]))
        # Add anharmonicity term(s)
        ham.addDrift(duff, qu, qubitArgs[f"qubit_anharm{qu}"] / 2)

    # Add coupling term
    ham.addCoupling([0, 1], qubitArgs["coupling"] / 2)

    tg = gate_time
    maxIter = iteration

    aBound=(-20, 20)  # The bound of the pulse's strength 
    gateJob, infidelity = remoteOptimizeCz(ham, aBound=aBound, tg=tg, maxIter=maxIter, targetInfidelity=0.001)

    result = ham.simulate(job=gateJob)
    process2d = project(result.result[0]["unitary"], qubits, level, 2)
    gatejob_encode = gateJob.dump ()
    nf = open ("ideal_2q_results/{}_{}_{}". format (qubit_freq0, qubit_freq1, tg), "w")
    nf.write (gatejob_encode)
    nf.close ()
    print ("success with {} of the error rate.".format (infidelity))


# Get the CZ fidelity of realistic hardware-generated pulse.
def get_realistic_cz_fidelity (max_freq, min_freq, qubit_freq0, qubit_freq1, num_bits, gate_time):

    # Get maximum amplitude value to calculate bit precision.
    f = open ("ideal_2q_results/{}_{}_{}". format (max_freq, min_freq, gate_time), "r")
    file_encode = f.read ()
    gatejob_max = QJob.load (file_encode)
    amp_max = (abs (min (gatejob_max['driveZ0'][0].seq)))
    precision = amp_max / (2**num_bits)

    # Get the ideal CZ pulse.
    f = open ("ideal_2q_results/{}_{}_{}". format (qubit_freq0, qubit_freq1, gate_time), "r")
    file_encode = f.read ()
    gatejob_ideal = QJob.load (file_encode)

    # Insert the bit-precision noise to the wave for Qubit 0.
    # + derive the time constaint (tau) for the RL calculation.
    wave0 = gatejob_ideal['driveZ0'][0].seq
    times = [0.2e-9*index_ for index_ in range (len (wave0))]
    y_min = max ([abs (val_) for val_ in wave0])
    t_start = None
    t_end = None
    for t, data in zip (times,wave0):
        if (abs (data) > 1e-5) and (t_start == None):
            t_start = t
        if (abs(data) > abs(y_min)*0.632) and (t_end == None):
            t_end = t
    tau0 = t_end - t_start
    if (abs (y_min) % precision) > precision/2:
        x = abs (y_min) - (abs (y_min) % precision) + precision
    else:
        x = abs (y_min) - (abs (y_min) % precision)
    amp_diff = x/abs (y_min)
    wave0_pre = [wave0[index_]*amp_diff for index_ in range (len (wave0))]

    # Insert the bit-precision noise to the wave for Qubit 1.
    # + derive the time constaint (tau) for the RL calculation.
    wave1 = gatejob_ideal['driveZ1'][0].seq
    times = [0.2e-9*index_ for index_ in range (len (wave1))]
    y_min = max ([abs (val_) for val_ in wave1])
    t_start = None
    t_end = None
    for t, data in zip (times,wave1):
        if (abs (data) > 1e-5) and (t_start == None):
            t_start = t
        if (abs(data) > abs(y_min)*0.632) and (t_end == None):
            t_end = t
    tau1 = t_end - t_start
    if (abs (y_min) % precision) > precision/2:
        x = abs (y_min) - (abs (y_min) % precision) + precision
    else:
        x = abs (y_min) - (abs (y_min) % precision)
    amp_diff = x/abs (y_min)
    wave1_pre = [wave1[index_]*amp_diff for index_ in range (len (wave1))]

    # Insert Gaussian noise due to the imprecise analog circuit.
    # deviation = amp_max * (200-122.07)*1e-6 * sqrt (2/pi) * voltage_reduction
    deviation = amp_max * (200)*1e-6 * sqrt (2/pi)
    noise0 = np.random.normal (0, deviation, 250)
    noise1 = np.random.normal (0, deviation, 250)
    wave0_real = wave0_pre + noise0
    wave1_real = wave1_pre + noise1
    wave0 = Quanlse.QWaveform.sequence (seq=wave0_real)
    wave1 = Quanlse.QWaveform.sequence (seq=wave1_real)

    # Sampling period
    dt = 0.2
    # Number of qubits
    qubits = 2
    # System energy levels
    level = 3

    gateJob_new = Quanlse.QWaveform.QJob (subSysNum=qubits, sysLevel=level, dt=dt)
    gateJob_new.addWave (gatejob_ideal.ctrlOperators['driveZ0'], onSubSys=0, waves=wave0, name="driveZ0")
    gateJob_new.addWave (gatejob_ideal.ctrlOperators['driveZ1'], onSubSys=1, waves=wave1, name="driveZ1")
    # gateJob_new.plot()

    # Initilize the Hamiltonian
    ham = QHam(subSysNum=qubits, sysLevel=level, dt=dt)

    qubitArgs = {
        "coupling": 0.0277 * (2 * pi),  # Coupling of Q0 and Q1
        "qubit_freq0": qubit_freq0 * (2 * pi),  # Frequency of Q0
        "qubit_freq1": qubit_freq1 * (2 * pi),  # Frequency of Q1
        "drive_freq0": qubit_freq1 * (2 * pi),  # Drive frequency on Q0 (rotating frame)
        "drive_freq1": qubit_freq1 * (2 * pi),  # Drive frequency on Q1 (rotating frame)
        "qubit_anharm0": -0.250 * (2 * pi),  # Anharmonicity of Q0
        "qubit_anharm1": -0.250 * (2 * pi)  # Anharmonicity of Q1
    }

    # Add drift term(s)
    for qu in range(2):
        # Add detuning term(s)
        ham.addDrift(number, qu, (qubitArgs[f"qubit_freq{qu}"] - qubitArgs[f"drive_freq{qu}"]))
        # Add anharmonicity term(s)
        ham.addDrift(duff, qu, qubitArgs[f"qubit_anharm{qu}"] / 2)

    # Add coupling term
    ham.addCoupling([0, 1], qubitArgs["coupling"] / 2)

    result = ham.simulate(job=gateJob_new)
    # result = ham.simulate(job=gatejob_ideal)
    process2d = project(result.result[0]["unitary"], qubits, level, 2)

    ideal_cz = [ \
        [ 1, 0, 0, 0], \
        [ 0, 1, 0, 0], \
        [ 0, 0, 1, 0], \
        [ 0, 0, 0,-1]]

    infidelity = Quanlse.Utils.Infidelity.unitaryInfidelity (ideal_cz, process2d, subSysNum=2)
    return infidelity, amp_max, precision


def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--max_freq", "-max", help="Max. qubit frequency that QCI supports [GHz]", type=float, default=6.0)
    parser.add_argument ("--min_freq", "-min", help="Min. qubit frequency that QCI supports [GHz]", type=float, default=4.0)
    parser.add_argument ("--freq1", "-f1", help="Resonating frequency of first qubit [GHz]", type=float, default=5.064)
    parser.add_argument ("--freq2", "-f2", help="Resonating frequency of second qubit [GHz]", type=float, default=5.0)
    parser.add_argument ("--precision", "-p", help="DC pulse precision [bit]", type=int, default=12)
    parser.add_argument ("--gate_time", "-t", help="2Q-gate duration [ns]", type=int, default=50)
    parser.add_argument ("--iteration", "-i", help="Iterations to find ideal CZ pulse from Baidu servers", type=int, default=40)
    args = parser.parse_args ()
    return args


if __name__ == "__main__":

    args = arg_parse ()
    max_freq = args.max_freq
    min_freq = args.min_freq
    qubit_freq0 = args.freq1
    qubit_freq1 = args.freq2
    num_bits = args.precision
    gate_time = args.gate_time
    iteration = args.iteration
    
    if not os.path.isfile ("ideal_2q_results/{}_{}_{}".format (max_freq, min_freq, gate_time)):
        get_ideal_cz_pulse (max_freq, min_freq, gate_time, iteration)
    if not os.path.isfile ("ideal_2q_results/{}_{}_{}".format (qubit_freq0, qubit_freq1, gate_time)):
        get_ideal_cz_pulse (qubit_freq0, qubit_freq1, gate_time, iteration)
    
    print ("Get CZ-gate fidelity of {}GHz, {}GHz of qubit frequency with {} bits for {}ns gate time.".format \
            (qubit_freq0, qubit_freq1, num_bits, gate_time))
    print ("(The maximum amplitude of the pulse circuit targets the CZ gate of {}GHz-{}GHz qubits)".format \
            (max_freq, min_freq))
    
    fidelity, amp_max, precision = get_realistic_cz_fidelity (max_freq, min_freq, qubit_freq0, qubit_freq1, \
                                                                num_bits, gate_time)
    
    print ("  Maximum amplitude:\t{}".format (amp_max))
    print ("  Bit precision:\t{}".format (precision))
    print ("  Gate error rate:\t{}".format (fidelity))
