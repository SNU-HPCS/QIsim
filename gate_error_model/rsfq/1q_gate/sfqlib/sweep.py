"""This code is not longer valid given current version of sfqEvolution
Do not use this code.
TODO UPDATE THE SWEEP"""
from sfqQubit import Sfq3LevelQubit, Sfq2LevelQubit
import numpy as np
import time
import matplotlib.pyplot as plt


def sweep_d_theta():
    """Resonance sequence. Sweep d_theta"""
    start = time.time()
    n = np.linspace(10, 500, 491)
    fidelities = list()
    for num_steps in n:
        qubit = Sfq3LevelQubit((np.pi/2.0/num_steps))
        qubit.resonance()
        fidelities.append(qubit.measure_fidelity())
    end = time.time()
    print "Time elapsed " + str(end - start)
    plt.plot([1.0-f for f in fidelities], 'b-')


def sweep_d_theta_with_pattern():
    """Resonance sequence. Sweep d_theta,
    using explicitly constructed pulse sequence"""
    n = np.linspace(10, 500, 491)
    start = time.time()
    fidelities = list()
    for j, num_steps in enumerate(n):
        pattern = list()
        pattern = make_resonance_pattern(num_steps)
        qubit = Sfq3LevelQubit((np.pi/2.0/num_steps))
        qubit.pulse_pattern(pattern)
        fidelities.append(qubit.measure_fidelity())
    end = time.time()
    print "Time elapsed " + str(end - start)
    plt.plot([1.0-f for f in fidelities], 'b-')
    plt.xlabel('number of puleses')
    plt.ylabel('Infidelity')
    plt.savefig('resonance.pdf')


def sweep_qubit_frequency_3_level(d_theta, marker):
    """Quantify error due to off resonance"""
    start = time.time()
    fidelities = list()
    w_qubit_space = np.linspace(2*np.pi*4.99e9, 2*np.pi*5.01e9, 500)
    for w01 in w_qubit_space:
        qubit = Sfq3LevelQubit(d_theta=d_theta,
                               w_qubit=(w01, w01-2*np.pi*0.2e9))
        qubit.resonance()
        fidelities.append(qubit.measure_fidelity(ignore_leakage=True))
    end = time.time()
    print "Time elapsed " + str(end - start)
    plt.semilogy([w/2.0/np.pi for w in w_qubit_space],
                 [1.0-f for f in fidelities], marker)


def sweep_d_theta_qubit_frequency_3_level():
    plt.figure()
    sweep_qubit_frequency_3_level(np.pi/2.0/50, 'b')
    sweep_qubit_frequency_3_level(np.pi/2.0/100, 'y')
    sweep_qubit_frequency_3_level(np.pi/2.0/300, 'r')
    sweep_qubit_frequency_3_level(np.pi/2.0/500, 'c')
    plt.legend(['50', '100', '300', '500'])
    plt.xlabel('Qubit Frequency (Hz)')
    plt.ylabel('Infidelity')
    plt.savefig('report1/figures/off_resonance_3_level.jpeg')


def sweep_qubit_frequency_2_level(d_theta, marker):
    """Quantify error due to off resonance"""
    start = time.time()
    fidelities = list()
    w_qubit_space = np.linspace(2*np.pi*4.99e9, 2*np.pi*5.01e9, 500)
    for w01 in w_qubit_space:
        qubit = Sfq2LevelQubit(d_theta=d_theta,
                               w_qubit=(w01, 2 * w01-2*np.pi*0.2e9))
        qubit.resonance()
        fidelities.append(qubit.measure_fidelity())
    end = time.time()
    print "Time elapsed " + str(end - start)
    plt.semilogy([w/2.0/np.pi for w in w_qubit_space],
                 [1.0-f for f in fidelities], marker)


def sweep_d_theta_qubit_frequency_2_level():
    plt.figure()
    sweep_qubit_frequency_2_level(np.pi/2.0/50, 'b')
    sweep_qubit_frequency_2_level(np.pi/2.0/100, 'y')
    sweep_qubit_frequency_2_level(np.pi/2.0/300, 'r')
    sweep_qubit_frequency_2_level(np.pi/2.0/500, 'c')
    plt.legend(['50', '100', '300', '500'])
    plt.xlabel('Qubit Frequency (Hz)')
    plt.ylabel('Infidelity')
    plt.savefig('report1/figures/off_resonance_2_level.jpeg')


def make_drag_pattern(resonance_num, drag_num):
    "res - drag - drag - res"
    pattern = list()
    resonance_only = int(1.0/2.0 * (resonance_num - drag_num))
    for i in range(resonance_only):
        pattern = pattern + [1, 0, 0, 0]
    for i in range(drag_num):
        pattern = pattern + [1, 1, 0, 0]
    for i in range(drag_num):
        pattern = pattern + [1, 0, 0, 1]
    for i in range(resonance_only):
        pattern = pattern + [1, 0, 0, 0]
    return pattern


def sweep_d_theta_drag(drag_num, marker):
    """
    Sweep DRAG puleses with different pulse number.
    """
    start = time.time()
    fidelities = list()
    resonance_space = np.linspace(200, 500, 100)
    for resonance_num in resonance_space:
        pattern = list()
        pattern = make_drag_pattern(int(resonance_num), drag_num)
        qubit = Sfq3LevelQubit((np.pi/2.0/resonance_num), w_clock=2*np.pi*20e9)
        qubit.pulse_pattern(pattern)
        fidelities.append(qubit.measure_fidelity())
    end = time.time()
    print "Time elapsed " + str(end - start)
    plt.plot(resonance_space, [1.0-f for f in fidelities], marker)


def sweep_derivative_d_theta_drag():
    """
    2d-Sweep DRAG pulses with different drag length and pulse number.
    """
    plt.figure()
    sweep_d_theta_drag(0, 'm')
    sweep_d_theta_drag(10, 'r')
    sweep_d_theta_drag(20, 'g')
    sweep_d_theta_drag(40, 'b')
    sweep_d_theta_drag(80, 'c')
    sweep_d_theta_drag(100, 'y')
    plt.legend(['0', '10', '20', '40', '80', '100'])
    plt.xlabel('number of puleses')
    plt.ylabel('Infidelity')
    plt.savefig('report1/figures/drag.jpeg')


def make_resonance_pattern(num):
    """
    Create a pulse pattern of [1, 1, 0, 1, ...].
    Only for the case when the clock frequency is the qubit frequency.
    """
    return [1 for i in range(int(num))]


sweep_d_theta()
sweep_d_theta_with_pattern()
sweep_d_theta_qubit_frequency_2_level()
sweep_d_theta_qubit_frequency_3_level()
sweep_derivative_d_theta_drag()
