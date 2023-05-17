import numpy as np
from qiskit import *
import os, math, random, json, ray
from qiskit.providers.aer.noise import pauli_error
import argparse


# timestep to apply the decoherence errors
timestep = 100
def parse_executable_with_error (workload, qubits, architecture):

    file_name = "{}_{}".format (workload, qubits)
    default_file = "./workloads_final/{}/{}".format (architecture, file_name)
    executable_file = "./workloads_final/{}/{}_error".format (architecture, file_name)
    if True:
    # if not os.path.isfile (executable_file):
        f = open (default_file, "r")
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
                while curr_time > error_time + timestep:
                    for num_qubits, qubit_name in zip (num_qubits_list, qubit_name_list):
                        for qubit_ in range (num_qubits):
                            nf.write ("id {}[{}];\n".format (qubit_name, qubit_))
                    error_time += timestep
            nf.write (inst_)
        f.close ()
        nf.close ()


def error_stabilizer_simulation (workload, qubits, architecture, args):

    # Generate the error model
    p_1q_gate = args.single
    p_2q_gate = args.two
    p_meas = args.measure
    t1_time = args.relax
    t2_time = args.coherence

    p_decoherence_xy = (1 - math.exp (-1*timestep/t1_time))/4
    p_decoherence_z = (1 - math.exp (-1*timestep/t2_time))/2 - p_decoherence_xy

    error_gate1 = pauli_error ([('X',p_1q_gate/3), ('Y',p_1q_gate/3), ('Z',p_1q_gate/3), ('I', 1-p_1q_gate)])
    error_gate2_ = pauli_error ([('X',p_2q_gate/3), ('Y',p_2q_gate/3), ('Z',p_2q_gate/3), ('I', 1-p_2q_gate)])
    error_decoherence = pauli_error ([('X',p_decoherence_xy), ('Y',p_decoherence_xy), \
                        ('Z',p_decoherence_z), ('I', 1-p_decoherence_xy*2 - p_decoherence_z)])
    
    # Read files
    file_name = "{}_{}".format (workload, qubits)
    executable_file = "./workloads_final/{}/{}_error".format (architecture, file_name)
    f = open (executable_file, "r")
    lines = f.readlines ()
    print("./workloads_final/{}/{}_error".format (architecture, file_name))

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

    error_list = dict ()
    for qubit_name, num_qubits in zip (qubit_name_list, num_qubits_list):
        error_list[qubit_name] = ['' for _ in range (num_qubits)]

    for inst_ in lines:
        words = inst_.split (' ')
        # For the case of single-qubit gate
        if any ([key_ in words[0] for key_ in ['rx', 'ry']]):
            qubit = int (words[1].split ("[")[1].split ("]")[0])
            q_name = words[1].split ("[")[0]
            rand = random.random ()
            if 0 <= rand < p_1q_gate/3:
                error_list[q_name][qubit] += "x"
            elif p_1q_gate/3 <= rand < p_1q_gate*2/3:
                error_list[q_name][qubit] += "y"
            elif p_1q_gate*2/3 <= rand < p_1q_gate:
                error_list[q_name][qubit] += "z"

        # For the case of two-qubit gate
        elif any ([key_ in words[0] for key_ in ['cz']]):
            cq = int (words[1].split (",")[0].split ("[")[1].split ("]")[0])
            tq = int (words[1].split (",")[1].split ("[")[1].split ("]")[0])
            q1_name = words[1].split (",")[0].split ("[")[0]
            q2_name = words[1].split (",")[1].split ("[")[0]

            rand = random.random ()
            if 0 <= rand < p_2q_gate/3:
                error_list[q1_name][cq] += "x"
            elif p_2q_gate/3 <= rand < p_2q_gate*2/3:
                error_list[q1_name][cq] += "y"
            elif p_2q_gate*2/3 <= rand < p_2q_gate:
                error_list[q1_name][cq] += "z"

            rand = random.random ()
            if 0 <= rand < p_2q_gate/3:
                error_list[q2_name][tq] += "x"
            elif p_2q_gate/3 <= rand < p_2q_gate*2/3:
                error_list[q2_name][tq] += "y"
            elif p_2q_gate*2/3 <= rand < p_2q_gate:
                error_list[q2_name][tq] += "z"
            
        # For the case of decoherence error
        if any ([key_ in words[0] for key_ in ['id']]):
            qubit = int (words[1].split ("[")[1].split ("]")[0])
            q_name = words[1].split ("[")[0]
            rand = random.random ()
            if 0 <= rand < p_decoherence_xy:
                error_list[q_name][qubit] += "x"
            elif p_decoherence_xy <= rand < 2*p_decoherence_xy:
                error_list[q_name][qubit] += "y"
            elif 2*p_decoherence_xy <= rand < 2*p_decoherence_xy+p_decoherence_z:
                error_list[q_name][qubit] += "z"
                
        # For the case of measurement error
        if any ([key_ in words[0] for key_ in ['measure']]):
            qubit = int (words[1].split ("[")[1].split ("]")[0])
            q_name = words[1].split ("[")[0]
            rand = random.random ()
            if 0 <= rand < p_meas:
                error_list[q_name][qubit] += "x"
                
    return error_list

@ray.remote
def error_stabilizer_simulation_ray (workload, qubits, architecture, args):
    return error_stabilizer_simulation (workload, qubits, architecture, args)


def simulation_ray (workload, qubits, architecture, num_shots, args):
    if not ray.is_initialized():
        ray.init()
    
    sims = [error_stabilizer_simulation_ray.remote (workload, qubits, architecture, args) for _ in range (num_shots)]
    results_error = ray.get(sims)
    
    return results_error


def load_esm_errors (filename):
    with open(filename, "r") as esm_error_file:
        esm_error = json.load(esm_error_file)
        
    data_qubit_result = [esm["data"] for esm in esm_error]
    ancilla_qubit_result = [esm["ancilla"] for esm in esm_error]
    num_shots = len(data_qubit_result)
    
    return data_qubit_result, ancilla_qubit_result, num_shots


def process_data_qubit (data_qubit_result, distance):
    count = [{'x': 0, 'y': 0, 'z': 0} for _ in range(len(data_qubit_result[0]))]
    for shot in data_qubit_result:
        for idx, (c, s) in enumerate(zip(count, shot)):
            for cs in s:
                try:
                    c[cs] = c[cs] +1
                except:
                    pass
    return count


def process_ancilla_qubit (ancilla_qubit_result):
    count = [{'x': 0, 'y': 0, 'z': 0} for _ in range(len(ancilla_qubit_result[0]))]
    for shot in ancilla_qubit_result:
        for c, s in zip(count, shot):
            for cs in s:
                try:
                    c[cs] = c[cs] +1
                except:
                    pass

    return count


def get_physical_error_rate (data_qubit_count, ancilla_qubit_count, num_shots, num_qb, esm_rounds_per_workloads):
    num_bf_dq = 0
    for dq, aq in zip(data_qubit_count, ancilla_qubit_count):
        num_bf_dq += dq['x'] + dq['y']
    p_bf = num_bf_dq / esm_rounds_per_workloads / num_shots / num_qb
    
    num_bf_aq = 0
    for dq, aq in zip(data_qubit_count, ancilla_qubit_count):
        num_bf_aq += aq['x'] + aq['y']
    q_bf = num_bf_aq / esm_rounds_per_workloads / num_shots / num_qb

    return p_bf, q_bf


def get_logical_error_rate (physical_error_rate, d):
    p_bf, q_bf = physical_error_rate
    
    logical_error_rate = 2 * (d + (d-1)*(3*d+5)*(d-1)/2.0/(d+3) + d*((d*d-1)/(d+3)*q_bf/p_bf + (d-1)/2)) * \
                        (math.factorial(d) / math.factorial((d+1)//2) / math.factorial((d-1)//2)) * \
                        (p_bf ** ((d+1)//2))
    
    return logical_error_rate


def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--single", "-s", help="Single-qubit error rate", type=float, default=1.12e-6)
    parser.add_argument ("--two", "-t", help="Two-qubit error rate", type=float, default=0.001)
    parser.add_argument ("--measure", "-m", help="Measurement error rate", type=float, default=0.001)
    parser.add_argument ("--relax", "-r", help="Relaxation time (i.e., T1 time) [us]", type=float, default=122000)
    parser.add_argument ("--coherence", "-c", help="Coherence time (i.e., T2 time) [us]", type=float, default=118000)
    args = parser.parse_args ()
    return args


if __name__ == "__main__":

    args = arg_parse ()
    workloads = ["esm"]
    architectures = ["300k_cmos", "horseridge"]
    qubit_lists = [2*(n_+1)**2 for n_ in range (3,25,2)]
    multithreading = True
    num_shots = 100
    
    print ("Calculates how many errors are occured for data and ancilla qubits, respectively.")
    for architecture in architectures:
        print("--------------- {} ---------------".format(architecture))
        for workload in workloads:
            for qubits in qubit_lists:
                parse_executable_with_error (workload, qubits, architecture)
                if multithreading:
                    results_error = simulation_ray (workload, qubits, architecture, num_shots, args)
                else:
                    results_error = list ()
                    for trials in range (num_shots):
                        result_error = error_stabilizer_simulation (workload, qubits, architecture, args)
                        results_error.append (result_error)
                
                nf = open ("esm_errors/{}/{}_{}.json".format (architecture, workload, qubits), "w")
                json.dump (results_error, nf)
                nf.close ()

    print ("Calculates the logical-qubit error rate.")
    for architecture in architectures:
        print("\n")
        print("--------------- {} ---------------".format(architecture))
        esm_rounds_per_workloads = 10
        
        for distance in range(3,25,2):
            try:
                num_qb = 2 * ((distance +1) ** 2)
                path = "{}/esm_{}.json".format(architecture, num_qb)
                filename = os.getcwd() + "/esm_errors/{}/esm_{}.json".format(architecture, num_qb)
                data_qubit_result, ancilla_qubit_result, num_shots = load_esm_errors(filename)
                print("Read file {} ...".format(path))
            except:
                break
            
            
            num_dq = num_qb // 2
            data_qubit_count = process_data_qubit(data_qubit_result, distance)
            ancilla_qubit_count = process_ancilla_qubit(ancilla_qubit_result)
            physical_error_rate = get_physical_error_rate(data_qubit_count, ancilla_qubit_count, num_shots, num_dq, esm_rounds_per_workloads)
            logical_error_rate = get_logical_error_rate(physical_error_rate, distance)
            
            print("Code distance: {}".format(distance))
            print("Num shots: {}".format(num_shots))
            print("physical_error_rate: {}".format(physical_error_rate))
            print("logical_error_rate: {}".format(logical_error_rate))
            print("")
