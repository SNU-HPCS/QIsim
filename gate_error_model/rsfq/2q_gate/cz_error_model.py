#!/usr/bin/python3.8
from Quanlse.QHamiltonian import QHamiltonian as QHam
from Quanlse.QOperator import duff, number
from Quanlse.remoteOptimizer import remoteOptimizeCz
from Quanlse.Utils.Functions import project
import Quanlse
from Quanlse import Define
from Quanlse.QWaveform import QJob
from math import *
import os, argparse


# Get the ideal CZ-pulse waveform from the Baidu cloud.
def get_ideal_cz_pulse (qubit_freq0, qubit_freq1, gate_time, iteration):

    print ("Get the ideal pulse from the Baidu cloud (Quanlse)...", end=" ")
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

    aBound=(-10, 10)  # The bound of the pulse's strength 
    gateJob, infidelity = remoteOptimizeCz(ham, aBound=aBound, tg=tg, maxIter=maxIter, targetInfidelity=0.001)

    result = ham.simulate(job=gateJob)
    process2d = project(result.result[0]["unitary"], qubits, level, 2)
    gatejob_encode = gateJob.dump ()
    nf = open ("ideal_2q_results/{}_{}_{}". format (qubit_freq0, qubit_freq1, tg), "w")
    nf.write (gatejob_encode)
    nf.close ()
    print ("success with {} of the error rate.".format (infidelity))


# Get the CZ fidelity of realistic hardware-generated pulse.
def get_realistic_cz_fidelity (qubit_freq0, qubit_freq1, num_bits, gate_time):

    # Get the ideal CZ pulse and the maximum-amplitude value to calculate the bit precision.
    f = open ("ideal_2q_results/{}_{}_{}". format (qubit_freq0, qubit_freq1, gate_time), "r")
    file_encode = f.read ()
    gatejob_ideal = QJob.load (file_encode)

    # Insert the bit-precision noise to the wave for Qubit 0.
    # + derive the time constaint (tau) for the RL calculation.
    #amp_max = (abs (min (gatejob_ideal['driveZ0'][0].seq)))
    amp_max = max ([abs (val_) for val_ in gatejob_ideal['driveZ0'][0].seq])
    precision = amp_max / (2**num_bits)

    wave0 = gatejob_ideal['driveZ0'][0].seq
    times = [0.2e-9*index_ for index_ in range (len (wave0))]
    new_wave0 = list ()
    for t, data in zip (times, wave0):
        if (abs (data) % precision) > precision/2:
            x = abs (data) - (abs (data) % precision) + precision
        else:
            x = abs (data) - (abs (data) % precision)
        if data >= 0:
            new_wave0.append (x)
        elif data < 0:
            new_wave0.append (-1*x)

    # Insert the bit-precision noise to the wave for Qubit 1.
    # + derive the time constaint (tau) for the RL calculation.
    #amp_max = (abs (min (gatejob_ideal['driveZ1'][0].seq)))
    amp_max = max ([abs (val_) for val_ in gatejob_ideal['driveZ1'][0].seq])
    precision = amp_max / (2**num_bits)

    wave1 = gatejob_ideal['driveZ1'][0].seq
    times = [0.2e-9*index_ for index_ in range (len (wave1))]

    new_wave1 = list ()
    for t, data in zip (times, wave1):
        if (abs (data) % precision) > precision/2:
            x = abs (data) - (abs (data) % precision) + precision
        else:
            x = abs (data) - (abs (data) % precision)
        
        if data >= 0:
            new_wave1.append (x)
        elif data < 0:
            new_wave1.append (-1*x)
    wave0_real = Quanlse.QWaveform.sequence (seq=new_wave0)
    wave1_real = Quanlse.QWaveform.sequence (seq=new_wave1)

    # Sampling period
    dt = 0.2
    # Number of qubits
    qubits = 2
    # System energy levels
    level = 3

    gateJob_new = Quanlse.QWaveform.QJob (subSysNum=qubits, sysLevel=level, dt=dt)
    gateJob_new.addWave (gatejob_ideal.ctrlOperators['driveZ0'], onSubSys=0, waves=wave0_real, name="driveZ0")
    gateJob_new.addWave (gatejob_ideal.ctrlOperators['driveZ1'], onSubSys=1, waves=wave1_real, name="driveZ1")

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

    result_ideal = ham.simulate(job=gatejob_ideal)
    result_real = ham.simulate(job=gateJob_new)
    process2d_ideal = project(result_ideal.result[0]["unitary"], qubits, level, 2)
    process2d_real = project(result_real.result[0]["unitary"], qubits, level, 2)

    ideal_cz = [ \
    [ 1, 0, 0, 0], \
    [ 0, 1, 0, 0], \
    [ 0, 0, 1, 0], \
    [ 0, 0, 0,-1]]

    infidelity_ideal = Quanlse.Utils.Infidelity.unitaryInfidelity (ideal_cz, process2d_ideal, subSysNum=2)
    infidelity_real = Quanlse.Utils.Infidelity.unitaryInfidelity (ideal_cz, process2d_real, subSysNum=2)
    return infidelity_ideal, infidelity_real


def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--freq1", "-f1", help="Resonating frequency of first qubit [GHz]", type=float, default=5.02978)
    parser.add_argument ("--freq2", "-f2", help="Resonating frequency of second qubit [GHz]", type=float, default=4.14238)
    parser.add_argument ("--precision", "-p", help="DC pulse precision [bit]", type=int, default=4)
    parser.add_argument ("--gate_time", "-t", help="2Q-gate duration [ns]", type=int, default=50)
    parser.add_argument ("--iteration", "-i", help="Iterations to find ideal CZ pulse from Baidu servers", type=int, default=30)
    args = parser.parse_args ()
    return args


if __name__ == "__main__":

    args = arg_parse ()
    qubit_freq1 = args.freq1
    qubit_freq2 = args.freq2
    num_bits = args.precision
    gate_time = args.gate_time
    iteration = args.iteration

    # for validation.
    # qubit_freq1 = 4.0
    # qubit_freq2 = 4.16
    # gate_time = 60
    # num_bits = 14

    if not os.path.isfile ("ideal_2q_results/{}_{}_{}".format (qubit_freq1, qubit_freq2, gate_time)):
        get_ideal_cz_pulse (qubit_freq1, qubit_freq2, gate_time, iteration)
    
    print ("Get CZ-gate fidelity of {}GHz, {}GHz of qubit frequency with {} bits for {}ns gate time.".format \
            (qubit_freq1, qubit_freq2, num_bits, gate_time))
    
    fidelity_ideal, fidelity_real = get_realistic_cz_fidelity (qubit_freq1, qubit_freq2, num_bits, gate_time)
    
    print ("  Gate error rate (ideal):\t{}".format (fidelity_ideal))
    print ("  Gate error rate (RSFQ):\t{}".format (fidelity_real))
