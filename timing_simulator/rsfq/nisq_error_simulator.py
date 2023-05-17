from qiskit import Aer
import qiskit, os, math, argparse
from qiskit.providers.aer.noise import NoiseModel, pauli_error


def in_range (n, value):
    n_ = float (n.split ("*")[1])
    while n_ > 2.0:
        n_ = n_ - 2.0
    while n_ < -1.75:
        n_ = n_ + 2.0
    return (value-0.25) <= n_ < (value+0.25)


def parse_stabilizer_executable (workload, qubits, bs):
    file_name = "{}_{}_{}".format (workload, qubits, bs)
    digiq_file = "./workloads_digiq_final/{}".format (file_name)
    executable_file = "./workloads_digiq_final/{}_stabilizer".format (file_name)
    if not os.path.isfile (executable_file):
        f = open (digiq_file, "r")
        nf = open (executable_file, "w")
        lines = f.readlines ()
        for inst_ in lines:
            words = inst_.split (' ')
            if "rz" in words[0]:
                angle = words[0].split ("(")[1].split (")")[0]
                if any ((key_ in angle) for key_ in ["0.5", "-1.5"]) \
                        or in_range (angle, 0.5) or in_range (angle, -1.5):
                    nf.write ("s {}\n".format (words[1]))
                elif any ((key_ in angle) for key_ in ["1.0", "-1.0"]) \
                        or in_range (angle, 1.0) or in_range (angle, -1.0):
                    nf.write ("z {}\n".format (words[1]))
                elif any ((key_ in angle) for key_ in ["1.5", "-0.5"]) \
                        or in_range (angle, 1.5) or in_range (angle, -0.5):
                    nf.write ("sdg {}\n".format (words[1]))
                elif any ((key_ in angle) for key_ in ["2.0", "0.0"]) \
                        or in_range (angle, 2.0) or in_range (angle, 0.0):
                    continue
                else:
                    print ("Our model does not support {}.".format (angle))
                    exit (-1)

            elif "ry" in words[0]:
                angle = words[0].split ("(")[1].split (")")[0]
                if any ((key_ in angle) for key_ in ["0.5", "-1.5"]) \
                        or in_range (angle, 0.5) or in_range (angle, -1.5):
                    nf.write ("sx {}\n".format (words[1]))
                    nf.write ("sdg {}\n".format (words[1]))
                    nf.write ("sx {}\n".format (words[1]))
                    nf.write ("z {}\n".format (words[1]))
                elif any ((key_ in angle) for key_ in ["1.0", "-1.0"]) \
                        or in_range (angle, 1.0) or in_range (angle, -1.0):
                    nf.write ("sx {}\n".format (words[1]))
                    nf.write ("sx {}\n".format (words[1]))
                    nf.write ("z {}\n".format (words[1]))
                elif any ((key_ in angle) for key_ in ["1.5", "-0.5"]) \
                        or in_range (angle, 1.5) or in_range (angle, -0.5):
                    nf.write ("sx {}\n".format (words[1]))
                    nf.write ("s {}\n".format (words[1]))
                    nf.write ("sx {}\n".format (words[1]))
                    nf.write ("z {}\n".format (words[1]))
                elif any ((key_ in angle) for key_ in ["2.0", "0.0"]) \
                        or in_range (angle, 2.0) or in_range (angle, 0.0):
                    nf.write ("sx {}\n".format (words[1]))
                    nf.write ("z {}\n".format (words[1]))
                    nf.write ("sx {}\n".format (words[1]))
                    nf.write ("z {}\n".format (words[1]))
                else:
                    print ("Our model does not support {}.".format (angle))
                    exit (-1)

            else:
                nf.write (inst_ + "\n")
        f.close ()
        nf.close ()


def ideal_stabilizer_simulation (workload, qubits, bs, args):
    
    print ("Run {}_{} for {} qubits with ideal simulation.".format (workload, bs, qubits))
    simulator = Aer.get_backend ("aer_simulator_stabilizer")
    num_shots = args.num_shots

    # Create circuit
    file = open ("workloads_digiq_final/{}_{}_{}_stabilizer".format (workload, qubits, bs))
    data = file.read ()
    circ = qiskit.QuantumCircuit.from_qasm_str (data)
    
    # Run and get counts
    result = simulator.run(circ, shots=num_shots).result()
    return result.get_counts (circ)


# timestep to apply the decoherence errors
def parse_executable_with_error (workload, qubits, bs, args):
    timestep = args.timestep
    file_name = "{}_{}_{}".format (workload, qubits, bs)
    digiq_file = "./workloads_digiq_final/{}_stabilizer".format (file_name)
    executable_file = "./workloads_digiq_final/{}_stabilizer_error".format (file_name)
    if not os.path.isfile (executable_file):
        f = open (digiq_file, "r")
        nf = open (executable_file, "w")
        lines = f.readlines ()
        
        error_time = 0
        num_qubits_list = list ()
        qubit_name_list = list ()
        for inst_ in lines:
            words = inst_.split (' ')
            # The marker for timing
            if "qreg" in words[0]:
                num_qubits = int (words[1].split ("[")[1].split ("]")[0])
                qubit_name = words[1].split ("[")[0]
                num_qubits_list.append (num_qubits)
                qubit_name_list.append (qubit_name)
            if "//**" in words[0]:
                curr_time = float (words[1].split ("ns")[0])
                if curr_time > error_time + timestep:
                    for num_qubits, qubit_name in zip (num_qubits_list, qubit_name_list):
                        for qubit_ in range (num_qubits):
                            nf.write ("id {}[{}];\n".format (qubit_name, qubit_))
                    error_time += timestep
            nf.write (inst_)
        f.close ()
        nf.close ()


def error_stabilizer_simulation (workload, qubits, bs, args):
    
    print ("Run {}_{} for {} qubits with noisy simulation.".format (workload, bs, qubits))
    simulator = Aer.get_backend ("aer_simulator_stabilizer")

    # Create circuit
    file = open ("workloads_digiq_final/{}_{}_{}_stabilizer_error".format (workload, qubits, bs))
    data = file.read ()
    circ = qiskit.QuantumCircuit.from_qasm_str (data)

    # Generate the error model
    p_1q_gate = args.single
    p_2q_gate = args.two
    t1_time = args.relax
    t2_time = args.coherence
    timestep = args.timestep
    num_shots = args.num_shots
    p_decoherence_xy = (1 - math.exp (-1*timestep/t1_time))/4
    p_decoherence_z = (1 - math.exp (-1*timestep/t2_time))/2 - p_decoherence_xy

    error_gate1 = pauli_error ([('X',p_1q_gate/3), ('Y',p_1q_gate/3), ('Z',p_1q_gate/3), ('I', 1-p_1q_gate)])
    error_gate2_ = pauli_error ([('X',p_2q_gate/3), ('Y',p_2q_gate/3), ('Z',p_2q_gate/3), ('I', 1-p_2q_gate)])
    error_gate2 = error_gate2_.tensor (error_gate2_)
    error_decoherence = pauli_error ([('X',p_decoherence_xy), ('Y',p_decoherence_xy), \
                        ('Z',p_decoherence_z), ('I', 1-p_decoherence_xy*2 - p_decoherence_z)])
    noise_model = NoiseModel ()
    noise_model.add_all_qubit_quantum_error (error_gate1, "sx") # to apply two errors for the "yz" set
    noise_model.add_all_qubit_quantum_error (error_gate2, "cz")
    noise_model.add_all_qubit_quantum_error (error_decoherence, "id")
    
    # Run and get counts
    result = simulator.run(circ, shots=num_shots, noise_model=noise_model).result()
    return result.get_counts (circ)


def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--single", "-s", help="Single-qubit error rate", type=float, default=2.92e-5)
    parser.add_argument ("--two", "-t", help="Two-qubit error rate", type=float, default=0.00114)
    parser.add_argument ("--relax", "-r", help="Relaxation time (i.e., T1 time) [us]", type=float, default=122000)
    parser.add_argument ("--coherence", "-c", help="Coherence time (i.e., T2 time) [us]", type=float, default=118000)
    parser.add_argument ("--timestep", "-ts", help="Timestep for decoherence error injection", type=int, default=100)
    parser.add_argument ("--num_shots", "-n", help="Number of shots for error simulation", type=int, default=1000)
    args = parser.parse_args ()
    return args


if __name__ == "__main__":

    args = arg_parse ()
    workloads = ['ghz', 'bitcode', 'hamiltonian', 'merminbell', \
            'phase', 'qaoa_fermionic', 'qaoa_vanilla', 'vqe']
    bs_list = [8]
    for workload in workloads:
        for n in range (1, 4):
            qubits = 2**n
            for bs in bs_list:
                parse_stabilizer_executable (workload, qubits, bs)
                result_ideal = ideal_stabilizer_simulation (workload, qubits, bs, args)
                parse_executable_with_error (workload, qubits, bs, args)
                result_error = error_stabilizer_simulation (workload, qubits, bs, args)
                fidelity = qiskit.quantum_info.analysis.hellinger_fidelity (result_ideal, result_error)
                print ("[bs={}] {}_{}:\t{}\n".format (bs, workload, qubits, fidelity))