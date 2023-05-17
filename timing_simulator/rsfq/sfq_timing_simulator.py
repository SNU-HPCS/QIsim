import pandas as pd
import numpy as np
from math import *
import decimal
import os
import multiprocessing, argparse

import warnings

warnings.simplefilter (action='ignore', category=RuntimeWarning)
warnings.simplefilter (action='ignore', category=FutureWarning)
warnings.simplefilter (action='ignore', category=DeprecationWarning)

DIGIQ_PATH = "../../device_model/rsfq/"


### WORKLOAD PARSER
### Parsing workloads to DigiQ-executable codes.

# insert u3gate with "RZ*RY*RZ*RY*RZ" form.
# (which is compatible with DigiQ)
def insert_u3gate (t3, t2, t1, qubit, q_name, file, z_angles):
    #print ("U3 ({}, {}, {}) to {}[{}]".format (t3, t2, t1, q_name, qubit))
    file.write ("rz(pi*{}) {}[{}];\n".format ((t1+z_angles[q_name][qubit])/180, q_name, qubit))
    file.write ("ry(pi*{}) {}[{}];\n".format (0.5, q_name, qubit))
    z_angles[q_name][qubit] = 0
    file.write ("rz(pi*{}) {}[{}];\n".format (t2/180, q_name, qubit))
    file.write ("ry(pi*{}) {}[{}];\n".format (0.5, q_name, qubit))
    z_angles[q_name][qubit] = t3
    return

def insert_hadamard (qubit, q_name, file, z_angles):
    file.write ("rz(pi*{}) {}[{}];\n".format ((180+z_angles[q_name][qubit])/180, q_name, qubit))
    file.write ("ry(pi*{}) {}[{}];\n".format (0.5, q_name, qubit))
    z_angles[q_name][qubit] = 0
    return

# insert CNOT (CX) using CZ gates.
def insert_cx (cq, tq, q1_name, q2_name, file, z_angles):
    # Hadamard
    insert_hadamard (tq, q2_name, file, z_angles)
    # CZ
    file.write ("cz {}[{}],{}[{}];\n".format (q1_name, cq, q2_name, tq))
    # Hadamard
    insert_hadamard (tq, q2_name, file, z_angles)
    return


def flush_z (z_angles, file):
    q_names = z_angles.keys ()
    for q_name in q_names:
        for qubit in range (len (z_angles[q_name])):
            file.write ("rz(pi*{}) {}[{}];\n".format ((z_angles[q_name][qubit])/180, q_name, qubit))
    return


def parse_circuit (workload, nq):
    digiq_file = "./workloads_digiq/{}_{}".format (workload, nq)
       
    #if not os.path.isfile (digiq_file):
    if True:
        
        z_angles = dict ()

        file = "./workloads/{}_{}".format (workload, nq)
        nf = open (digiq_file, "w")
        f = open (file, "r")
        lines = f.readlines ()
        line = ""
        prev_line = ""

        for n, line in enumerate (lines):
            words = line.split (' ')

            # Build the z-angle objects
            if words[0] == "qreg":
                qubits = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                z_angles[q_name] = [0 for _ in range (qubits)]

            # Insert barrier between start of measure and reset for timing optimization
            if (words[0] == "measure" and prev_line.split (' ')[0] != "measure") or \
                (words[0] != "measure" and prev_line.split (' ')[0] == "measure") or \
                (words[0] == "reset" and prev_line.split (' ')[0] != "reset") or \
                (words[0] != "reset" and prev_line.split (' ')[0] == "reset"):
                inst_ = "barrier "
                for n_, qubit_ in enumerate (z_angles.keys ()):
                    if n_ == 0:
                        inst_ = inst_ + qubit_
                    else:
                        inst_ = inst_ + "," + qubit_
                inst_ = inst_ + ";\n"
                nf.write (inst_)

            # Puali gates (X,Y,Z).
            if words[0] == "x" or words[0] == "X":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                #t3, t2, t1 = 90, 0, 0
                t3, t2, t1 = 180, 0, 0
                insert_u3gate (t3, t2, t1, qubit, q_name, nf, z_angles)
            elif words[0] == "y" or words[0] == "Y":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                t3, t2, t1 = 0, 0, 0
                insert_u3gate (t3, t2, t1, qubit, q_name, nf, z_angles)
            elif words[0] == "z" or words[0] == "Z":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                z_angles[q_name][qubit] += 180

            # H, SDG, S gates.
            elif words[0] == "h":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                insert_hadamard (qubit, q_name, nf, z_angles)
            elif words[0] == "sdg":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                z_angles[q_name][qubit] += (-90)
            elif words[0] == "s":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                z_angles[q_name][qubit] += 90
            elif words[0] == "t":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                z_angles[q_name][qubit] += 45
            elif words[0] == "tdg":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                z_angles[q_name][qubit] += (-45)

            # RX, RY, RZ gates.
            elif words[0].split ("(")[0] == "rx":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                angle = None
                if "pi" in words[0]:
                    angle = float (words[0].split ("*")[1].split (")")[0])*180
                else:
                    angle = float (words[0].split ("(")[1].split (")")[0])/pi*180
                t3, t2, t1 = -180, (180-angle), 0
                insert_u3gate (t3, t2, t1, qubit, q_name, nf, z_angles)
            elif words[0].split ("(")[0] == "ry":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                angle = None
                if "pi" in words[0]:
                    angle = float (words[0].split ("*")[1].split (")")[0])*180
                else:
                    angle = float (words[0].split ("(")[1].split (")")[0])/pi*180
                t3, t2, t1 = -90, (180-angle), -90
                insert_u3gate (t3, t2, t1, qubit, q_name, nf, z_angles)
            elif words[0].split ("(")[0] == "rz":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                angle = None
                if "pi" in words[0]:
                    angle = float (words[0].split ("*")[1].split (")")[0])*180
                else:
                    angle = float (words[0].split ("(")[1].split (")")[0])/pi*180
                z_angles[q_name][qubit] += angle

            # Two-qubit gates (CX, SWAP).
            elif words[0] == "cx":
                cq = int (words[1].split (",")[0].split ("[")[1].split ("]")[0])
                tq = int (words[1].split (",")[1].split ("[")[1].split ("]")[0])
                q1_name = words[1].split (",")[0].split ("[")[0]
                q2_name = words[1].split (",")[1].split ("[")[0]
                insert_cx (cq, tq, q1_name, q2_name, nf, z_angles)
            elif words[0] == "swap":
                cq = int (words[1].split (",")[0].split ("[")[1].split ("]")[0])
                tq = int (words[1].split (",")[1].split ("[")[1].split ("]")[0])
                q1_name = words[1].split (",")[0].split ("[")[0]
                q2_name = words[1].split (",")[1].split ("[")[0]
                insert_cx (cq, tq, q1_name, q2_name, nf, z_angles)
                insert_cx (tq, cq, q2_name, q1_name, nf, z_angles)
                insert_cx (cq, tq, q1_name, q2_name, nf, z_angles)

            # Three-qubit gates (Toffoli; CCX)
            elif words[0] == "ccx":
                cq1 = int (words[1].split (",")[0].split ("[")[1].split ("]")[0])
                cq2 = int (words[1].split (",")[1].split ("[")[1].split ("]")[0])
                tq = int (words[1].split (",")[2].split ("[")[1].split ("]")[0])
                q1_name = words[1].split (",")[0].split ("[")[0]
                q2_name = words[1].split (",")[1].split ("[")[0]
                q3_name = words[1].split (",")[2].split ("[")[0]
                # insert H
                insert_hadamard (tq, q3_name, nf, z_angles)
                # insert CX
                insert_cx (cq2, tq, q2_name, q3_name, nf, z_angles)
                # insert TDG
                z_angles[q3_name][tq] += (-45)
                # insert CX
                insert_cx (cq1, tq, q1_name, q3_name, nf, z_angles)
                # insert T
                z_angles[q3_name][tq] += (45)
                # insert CX
                insert_cx (cq2, tq, q2_name, q3_name, nf, z_angles)
                # insert TDG
                z_angles[q3_name][tq] += (-45)
                # insert CX
                insert_cx (cq1, tq, q1_name, q3_name, nf, z_angles)
                # insert T
                z_angles[q2_name][cq2] += (45)
                # insert T
                z_angles[q3_name][tq] += (45)
                # insert CX
                insert_cx (cq1, cq2, q1_name, q2_name, nf, z_angles)
                # insert H
                insert_hadamard (tq, q3_name, nf, z_angles)
                # insert T
                z_angles[q1_name][cq1] += (45)
                # insert TDG
                z_angles[q2_name][cq2] += (-45)
                # insert CX
                insert_cx (cq1, cq2, q1_name, q2_name, nf, z_angles)

            else:
                nf.write (line)
            if (words[0] != "//") or (not line.isspace ()):
                prev_line = line
        return


def parse_workloads ():
    
    file_list = os.listdir ("./workloads")
    file_list.remove (".gitkeep")
    for file in file_list:
        words = file.split ("_")
        qubit = int (words[-1])
        workload = None
        if len (words) == 2:
            workload = words[0]
        else:
            workload = "{}_{}".format (words[0], words[1])
        print ("{} / {}".format (workload, qubit))
        parse_circuit (workload, qubit)
    return


### TIMING SIMULATION.
### Derive timing and the total number of executed instructions.

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def float_scale(x):
    max_digits = 14
    int_part = int(abs(x))
    magnitude = 1 if int_part == 0 else int(log10(int_part)) + 1
    if magnitude >= max_digits:
        return 0
    frac_part = abs(x) - int_part
    multiplier = 10 ** (max_digits - magnitude)
    frac_digits = multiplier + int(multiplier * frac_part + 0.5)
    while frac_digits % 10 == 0:
        frac_digits /= 10
    return int(log10(frac_digits))


def float_gcd(a, b):
    sc = float_scale(a)
    sc_b = float_scale(b)
    sc = sc_b if sc_b > sc else sc
    fac = pow(10, sc)

    a = int(round(a*fac))
    b = int(round(b*fac))

    return round(gcd(a, b)/fac, sc)


def timing_adjustment (workload, qubits, sl, tl, ml, rl, groups, bs):

    text_file = open ("workloads_digiq/{}_{}".format (workload, qubits), "r")
    new_file = open ("workloads_digiq_final/{}_{}_{}".format (workload, qubits, bs), "w")
    data = text_file.read ()
    data_list = data.split ("\n")
    gate_sequence_per_qubit = dict() # remaining gate sequence for each qubits
    cur_gate_per_qubit = dict() # currently executing gate or waiting CZ gates
    valid_gate_per_qubit = dict() # validity (wait time decreases only if the qubit is valid)
    wait_time_per_qubit = dict() # remaining cycle for completing operation

    num_group_1q = 0
    num_inst_per_total_2q = 0
    num_group_meas = 0
    num_group_reset = 0

    num_qubit_1q = 0
    num_qubit_2q = 0
    num_qubit_meas = 0
    num_qubit_reset = 0

    qubit_count = 0
    # Initializing dicts 
    sg_operating = dict() # {(qubit name, qubit #): 0 or 1}
    sg_operating_gr = dict() # {group #: number of operating 1q }
    sg_operate_cycle_gr = dict() # {group # : operate cycle #}
    tg_operating = 0  # number of operating 2q 
    meas_operating = dict() # {group # : number of operating measure }
    meas_operate_cycle = dict() # {group # : operate cycle #}
    for n, inst_ in enumerate(data_list.copy()):
        words = inst_.split(" ")
        if any ((key_ in words[0]) for key_ in ["//", "OPENQASM", "include", "qreg", "creg", "ry(pi*0.5)"]):
            if words[0] == "qreg":
                qubits_ = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]

                gate_sequence_per_qubit[q_name] = [list() for _ in range (qubits_)]
                cur_gate_per_qubit[q_name] = [" " for _ in range (qubits_)]
                valid_gate_per_qubit[q_name] = [1 for _ in range (qubits_)]
                wait_time_per_qubit[q_name] = [0 for _ in range (qubits_)]
                sg_operating[q_name] = [0 for _ in range (qubits_)]
                qubit_count += qubits_
            if words[0] == "//" or words[0] == "ry(pi*0.5)" or words[0] == "barrier":
                data_list.remove(inst_)
            else:
                new_file.write(inst_ + "\n")
                data_list.remove(inst_)

        if any ((key_ in words[0]) for key_ in ["cz"]):
            num_qubit_2q += 2
        elif any ((key_ in words[0]) for key_ in ["measure"]):
            num_qubit_meas += 1
        elif any ((key_ in words[0]) for key_ in ["reset"]):
            num_qubit_reset += 1
        elif any ((key_ in words[0]) for key_ in ["rz", "z", "Z", "s", "sdg"]):
            num_qubit_1q += 1


    # Initializing gate_sequence_per_qubit & num_gate
    num_gate = 0 # Total nubmer of gates(or operations).  
    cz_label = 0 # for labeling CZ gates
    #barrier_label = 0 # for labeling barriers

    inst_types = set ([inst_.split (" ")[0] for inst_ in data_list])
    inst_types = list(inst_types)
    if "barrier" in inst_types:
        inst_types.remove("barrier")
    if "cz" in inst_types:
        inst_types.remove("cz")
    if "measure" in inst_types:
        inst_types.remove("measure")
    if "reset" in inst_types:
        inst_types.remove("reset")
    if "" in inst_types:
        inst_types.remove("")
    if " " in inst_types:
        inst_types.remove(" ")

    cur_s_gate_type = dict()
    for inst_type_ in inst_types:
        cur_s_gate_type[inst_type_] = 0
    
    qubit_per_group = (qubit_count - 1) // groups + 1
    qubit_group_info = dict() # {(qubit name, qubit #) : group #}

    cnt = 0
    for q_name in cur_gate_per_qubit.keys():
        for qubit in range(len(cur_gate_per_qubit[q_name])):
            qubit_group_info[(q_name, qubit)] = cnt // qubit_per_group
            cnt += 1

    for gr_num_ in range(groups):
        sg_operating_gr[gr_num_] = 0
        sg_operate_cycle_gr[gr_num_] = 0
        meas_operating[gr_num_] = 0
        meas_operate_cycle[gr_num_] = 0


    for n, inst_ in enumerate(data_list.copy()):
        words = inst_.split(' ')
        op = words[0].split("(")[0]
        
        if op == "rz" or words[0] == "measure" or words[0] == "reset":
            qubit = int(words[1].split("[")[1].split("]")[0])
            q_name = words[1].split("[")[0]
            gate_sequence_per_qubit[q_name][qubit].append(inst_)
            num_gate += 1

        if words[0] == "cz":
            cz_label += 1
            cq = int (words[1].split (",")[0].split ("[")[1].split ("]")[0])
            tq = int (words[1].split (",")[1].split ("[")[1].split ("]")[0])
            q1_name = words[1].split (",")[0].split ("[")[0]
            q2_name = words[1].split (",")[1].split ("[")[0]
            gate_sequence_per_qubit[q1_name][cq].append(inst_ + " {}".format(cz_label))
            gate_sequence_per_qubit[q2_name][tq].append(inst_ + " {}".format(cz_label))
            num_gate += 2

        '''
        if words[0] == "barrier":
            barrier_label += 1
            for q_name in gate_sequence_per_qubit.keys():
                for qubit in range(len(gate_sequence_per_qubit[q_name])):
                    gate_sequence_per_qubit[q_name][qubit].append(inst_ + " {}".format(barrier_label))
                    num_gate += 1
        '''
    
    cycle_time = float_gcd(float_gcd(float_gcd(sl, tl), ml), rl)
    sl, tl, ml, rl = int(decimal.Decimal("{}".format(sl)) // decimal.Decimal("{}".format(cycle_time))),\
                    int(decimal.Decimal("{}".format(tl)) // decimal.Decimal("{}".format(cycle_time))), \
                    int(decimal.Decimal("{}".format(ml)) // decimal.Decimal("{}".format(cycle_time))), \
                    int(decimal.Decimal("{}".format(rl)) // decimal.Decimal("{}".format(cycle_time)))
    global_clock = 0

    # For CZ gate's validity check
    cz_num_list = list() # [CZ gate #, ...]
    cz_target_list = list() # [(qubit name, qubit #)]
    #barrier_list = dict() # {barrier # : barrier count}

    while 1:
        is_reset_counted = 0
        # new gate fetch only if there are completed gates
        if min([min(wait_time_per_qubit[key_]) for key_ in wait_time_per_qubit.keys()]) == 0:
            timing_point_generated = 0
            for q_name in wait_time_per_qubit.keys():
                for qubit in range(len(wait_time_per_qubit[q_name])):
                    if wait_time_per_qubit[q_name][qubit] == 0:
                        if len(gate_sequence_per_qubit[q_name][qubit]) != 0:

                            inst_ = gate_sequence_per_qubit[q_name][qubit].pop(0)
                            words = inst_.split(" ")
                            op = words[0].split("(")[0]

                            if cur_gate_per_qubit[q_name][qubit].split("(")[0] == "rz":
                                sg_operating[q_name][qubit] = 0 
                                sg_operating_gr[qubit_group_info[(q_name, qubit)]] -= 1
                            elif cur_gate_per_qubit[q_name][qubit].split(" ")[0] == "measure":
                                meas_operating[qubit_group_info[(q_name, qubit)]] -= 1
                            elif cur_gate_per_qubit[q_name][qubit].split(" ")[0] == "cz":
                                tg_operating -= 1

                            # Timing point generate
                            if timing_point_generated == 0 :
                                new_file.write("//** {}ns\n".format (float(global_clock * decimal.Decimal("{}".format(cycle_time)))))  
                                timing_point_generated += 1

                            # Get new gate        
                            # Single qubit gates                        
                            if op == "rz":
                                # Fetch new gate
                                cur_s_gate_type[words[0]] += 1
                                cur_gate_per_qubit[q_name][qubit] = words[0]
                                wait_time_per_qubit[q_name][qubit] = sl
                                valid_gate_per_qubit[q_name][qubit] = 0

                            # Two qubit gate
                            elif op == "cz":
                                cur_gate_per_qubit[q_name][qubit] = inst_
                                wait_time_per_qubit[q_name][qubit] = tl
                                valid_gate_per_qubit[q_name][qubit] = 0

                            # Measure
                            elif op == "measure":
                                # Fetch new gate
                                cur_gate_per_qubit[q_name][qubit] = inst_    
                                wait_time_per_qubit[q_name][qubit] = ml
                                valid_gate_per_qubit[q_name][qubit] = 0

                            # Reset    
                            elif op == "reset":
                                # Fetch new gate
                                cur_gate_per_qubit[q_name][qubit] = "reset"     
                                new_file.write(inst_ + "\n")
                                num_gate -= 1
                                wait_time_per_qubit[q_name][qubit] = rl
                                if is_reset_counted == 0:
                                    num_group_reset += 1
                                    is_reset_counted += 1

                            # etc
                            else:
                                print("Our model does not support {} operation\n".format(op))
                                exit
                        else :
                            if cur_gate_per_qubit[q_name][qubit].split("(")[0] == "rz":
                                sg_operating_gr[qubit_group_info[(q_name, qubit)]] -= 1
                            elif cur_gate_per_qubit[q_name][qubit].split(" ")[0] == "measure":
                                meas_operating[qubit_group_info[(q_name, qubit)]] -= 1
                            elif cur_gate_per_qubit[q_name][qubit].split(" ")[0] == "cz":
                                tg_operating -= 1
                            # Update wait time, currengt gate info, and valid info of operation done qubits
                            cur_gate_per_qubit[q_name][qubit] = " "
                            valid_gate_per_qubit[q_name][qubit] = 0
                            wait_time_per_qubit[q_name][qubit] = 0.1 
                            sg_operating[q_name][qubit] = 0

        # Execute 2q gate only if tg_operating == 0
        tg_operating_temp = 0
        for q_name in cur_gate_per_qubit.keys():
            for qubit, cur_gate_ in enumerate(cur_gate_per_qubit[q_name]):
                if valid_gate_per_qubit[q_name][qubit] == 0:
                    if cur_gate_.split(" ")[0] == "cz":
                        cz_label_ = cur_gate_.split(" ")[-1]
                        if cz_label_ in cz_num_list:
                            # Fetch new CZgate only if every target qubits of the CZ gate is ready
                            if tg_operating == 0:
                                (tq_name, tq) = cz_target_list[cz_num_list.index(cz_label_)]
                                if q_name != tq_name or qubit != tq:
                                    valid_gate_per_qubit[q_name][qubit] = 1
                                    valid_gate_per_qubit[tq_name][tq] = 1
                                    cz_num_list.remove(cz_label_)
                                    cz_target_list.remove((tq_name, tq))
                                    new_file.write(remove_suffix(cur_gate_, " {}".format(cz_label_)) + "\n")
                                    num_gate -= 2
                                    tg_operating_temp += 2
                        else:
                            cz_num_list.append(cz_label_)
                            cz_target_list.append((q_name, qubit))
                            valid_gate_per_qubit[q_name][qubit] = 0
        tg_operating += tg_operating_temp

        # If no single qubit gate is running, execute the most numerous single qubit gate.
        if max([max(sg_operating[key_]) for key_ in sg_operating.keys()]) == 0:
            for n in range(bs):
                max_s_gate_num = 0
                max_s_gate = ""
                for key_, value_ in cur_s_gate_type.items():
                    if value_ > max_s_gate_num:
                        max_s_gate = key_
                        max_s_gate_num = value_
                if max_s_gate_num > 0:                    
                    for q_name in cur_gate_per_qubit.keys():
                        for qubit in range(len(cur_gate_per_qubit[q_name])):
                            cur_inst_ = cur_gate_per_qubit[q_name][qubit]
                            if cur_inst_.split("(")[0] == "rz":
                                if cur_inst_ == max_s_gate:
                                    valid_gate_per_qubit[q_name][qubit] = 1
                                    new_file.write("{} {}[{}];\n".format(cur_inst_, q_name, qubit))
                                    new_file.write("{} {}[{}];\n".format("ry(pi*0.5)", q_name, qubit))
                                    num_gate -= 1
                                    cur_s_gate_type[cur_inst_] -= 1
                                    sg_operating[q_name][qubit] = 1
                                    sg_operating_gr[qubit_group_info[(q_name, qubit)]] += 1

        # Execute measure only if meas_operating == 0 for each group
        for gr_num_ in range(groups):
            if max(meas_operating.values()) == 0:
                for q_name in cur_gate_per_qubit.keys():
                    for qubit, cur_gate_ in enumerate(cur_gate_per_qubit[q_name]):
                        if qubit_group_info[(q_name, qubit)] == gr_num_:
                            if valid_gate_per_qubit[q_name][qubit] == 0:
                                if cur_gate_.split(" ")[0] == "measure":
                                    new_file.write(cur_gate_ + "\n")
                                    num_gate -= 1
                                    meas_operating[qubit_group_info[(q_name, qubit)]] += 1
                                    valid_gate_per_qubit[q_name][qubit] = 1

        for gr_num_ in range(groups):
            if sg_operating_gr[gr_num_] >= 1:
                sg_operate_cycle_gr[gr_num_] += 1
            if meas_operating[gr_num_] > 0:
                meas_operate_cycle[gr_num_] += 1
        
        if tg_operating > 0:
            num_inst_per_total_2q += 2

        # Reduce wait time by 1 only valid qubits
        for q_name in valid_gate_per_qubit.keys():
                for qubit in range(len(valid_gate_per_qubit[q_name])):
                    if valid_gate_per_qubit[q_name][qubit] == 1:
                        wait_time_per_qubit[q_name][qubit] -= 1
        global_clock += 1

        '''
        # Check if barriers have been fetched for all qubits, and if all are gathered, proceed with the next operation
        for barrier_label_ in barrier_list.copy().keys():
            if barrier_list[barrier_label_] == qubit_count:
                for q_name in wait_time_per_qubit.keys():
                    for qubit in range(len(wait_time_per_qubit[q_name])):
                        wait_time_per_qubit[q_name][qubit] = 0
                        valid_gate_per_qubit[q_name][qubit] = 1
                        num_gate -= 1
                barrier_list.pop(barrier_label_)
                global_clock -= 1
        '''

        # If there is no gate to execute, generate the last timing point by adding max waiting time
        if num_gate == 0:
            # Check the current operation of all qubits, and add the max remaining time (wait time) for each operation to the inst per group value
            max_1q = np.zeros(groups, int)
            max_2q = 0
            max_meas = np.zeros(groups, int)
            for qname_ in cur_gate_per_qubit.keys():
                for qnum_, cur_gate_ in enumerate(cur_gate_per_qubit[qname_]):
                    if cur_gate_.split("(")[0] == "rz" and max_1q[qubit_group_info[(qname_, qnum_)]] < wait_time_per_qubit[qname_][qnum_]:
                        max_1q[qubit_group_info[(qname_, qnum_)]] = wait_time_per_qubit[qname_][qnum_]
                    elif cur_gate_.split(" ")[0] == "cz" and max_2q < wait_time_per_qubit[qname_][qnum_]:
                        max_2q = wait_time_per_qubit[qname_][qnum_]
                    elif cur_gate_ == "measure" and max_meas[qubit_group_info[(qname_, qnum_)]] < wait_time_per_qubit[qname_][qnum_]:
                        max_meas[qubit_group_info[(qname_, qnum_)]] = wait_time_per_qubit[qname_][qnum_]
            for gnum_, max_wait_1q_per_group in enumerate(max_1q):
                if max_wait_1q_per_group >= 1:
                    sg_operate_cycle_gr[gnum_] += max_wait_1q_per_group
            if max_2q >= 1: num_inst_per_total_2q += 2 * max_2q
            for m_gnum_, max_wait_meas_per_group in enumerate(max_meas):
                if max_wait_meas_per_group >= 1:
                    meas_operate_cycle[m_gnum_] += max_wait_meas_per_group

            max_wait_time = int(max(max([wait_time_per_qubit[key_] for key_ in wait_time_per_qubit.keys()])))
            global_clock += max_wait_time
            if max_wait_time != 0:
                new_file.write("//** {}ns\n".format (float(global_clock * decimal.Decimal("{}".format(cycle_time)))))         
            break     

    num_group_1q = sum(sg_operate_cycle_gr.values()) / sl
    num_inst_per_total_2q = num_inst_per_total_2q / tl
    num_group_meas = sum(meas_operate_cycle.values()) / ml

    stat = {'1q': int(num_qubit_1q), '1q_per_group': (num_group_1q), \
            '2q': int(num_qubit_2q), '2q overlap': num_inst_per_total_2q, \
            'measure': int(num_qubit_meas),'measure_per_group': (num_group_meas),\
            'reset': int (num_qubit_reset), \
            'latency': float(global_clock * decimal.Decimal("{}".format(cycle_time)))}
    stat_df = pd.DataFrame.from_dict (stat, orient='index')
    stat_df.to_csv ("results/stats/{}_{}_{}.csv".format (workload, qubits, bs))

def rm_time_point(workload, qubits, bs):
    if os.path.isfile ("workloads_digiq_final/{}_{}_{}".format (workload, qubits, bs)):
        pass
    data_list = list()
    with open ("workloads_digiq_final/{}_{}_{}".format (workload, qubits, bs), "r") as f:
        data = f.read ()
        data_list = data.split ("\n")
    with open ("workloads_digiq_final/{}_{}_{}".format (workload, qubits, bs), "w") as nf:
        time_point_list = list()
        remove_list = list()
        for n, line in enumerate(data_list.copy()):
            if n == len(data_list) - 1 and line.split(" ")[0] == "//**":
                time_point_list.append(n)
                if len(time_point_list) >= 2:
                    for idx in range(len(time_point_list) - 1):
                        remove_list.append(time_point_list[idx])
                time_point_list = list()
            else:
                if line.split(" ")[0] == "//**":
                    time_point_list.append(n)
                else:
                    if len(time_point_list) >= 2:
                        for idx in range(len(time_point_list) - 1):
                            remove_list.append(time_point_list[idx])
                    time_point_list = list()
        for rm in sorted(remove_list, reverse= True):
            del data_list[rm]
        for line in data_list:
            nf.write("{}\n".format(line))

    data_list = list()
    with open ("workloads_digiq_final/{}_{}_{}".format (workload, qubits, bs), "r") as f:
        data = f.read ()
        data_list = data.split ("\n")
    with open ("workloads_digiq_final/{}_{}_{}".format (workload, qubits, bs), "w") as nf:
        cur_time_point_list = (0, "")
        prev_time_point_list = (0, "")
        remove_list = list()
        for n, line in enumerate(data_list.copy()):
            if line.split(" ")[0] == "//**" :
                prev_time_point_list = cur_time_point_list
                cur_time_point_list = (n, line.split(" ")[1].split("ns")[0])
                if prev_time_point_list[1] == cur_time_point_list[1]:
                    remove_list.append(cur_time_point_list[0])

        for rm in sorted(remove_list, reverse= True):
            del data_list[rm]
        for line in data_list:
            nf.write("{}\n".format(line))

def timing_adjustment_threading (workload, qubit_range, sl, tl, ml, rl, groups, bs):
    for qubits in qubit_range:
        for bs_ in bs:
            print ("Current file: {}_{}_{}".format (workload, qubits, bs_))
            timing_adjustment (workload, qubits, sl, tl, ml, rl, groups, bs_)
            rm_time_point(workload, qubits, bs_)


def power_calculation (workload, qubits, sl, tl, ml, rl, groups, bs, y_length, z_length, tq_width, tech_type):
    # Read digiq hardware results.
    freq = 24 # We use the fixed frequency; 24GHz
    digiq_file = DIGIQ_PATH + "digiq_results/{}_{}_{}_{}_{}_{}_{}_{}_{}.csv".format \
                (bs, groups, qubits, y_length, z_length, tl*freq, tq_width, 32, False)
    if not os.path.isfile (digiq_file):
        current_dir_ = os.getcwd ()
        os.chdir (DIGIQ_PATH)
        os.system ("python sfq_device_model.py -q {} -b {} -y {} -t {}".format (qubits, bs, y_length, tq_width))
        os.chdir (current_dir_)
    digiq_df = pd.read_csv (digiq_file, index_col=0)
    # Read digiq simulation-stat results.
    stat_file = "results/stats/{}_{}_{}.csv".format (workload, qubits, bs)
    stat_df = pd.read_csv (stat_file, index_col=0)
    
    ratio_1q = stat_df.loc["1q_per_group"].item() * sl / stat_df.loc["latency"].item()/2
    ratio_2q = stat_df.loc["2q overlap"].item() * tl / stat_df.loc["latency"].item()/2
    ratio_meas = stat_df.loc["measure_per_group"].item() * ml / stat_df.loc["latency"].item()/2

    result = digiq_df[["PowerStatic","Area"]].copy ()
    list_ = list ()
    list_.append (digiq_df.loc["Buffer1"]["EnergyDynamic"] * (ratio_1q + ratio_2q) * freq)
    list_.append (digiq_df.loc["Buffer2"]["EnergyDynamic"] * (ratio_1q + ratio_2q) * freq)
    list_.append (digiq_df.loc["Controller"]["EnergyDynamic"] * (ratio_1q) * freq)
    list_.append (digiq_df.loc["Bitgen"]["EnergyDynamic"] * (ratio_1q) * freq)
    # list_.append (digiq_df.loc["Bitgen controller"]["EnergyDynamic"] * (ratio_1q) * freq)
    list_.append (digiq_df.loc["Drive mux"]["EnergyDynamic"] * (ratio_1q) * freq)
    list_.append (digiq_df.loc["SFQDC"]["EnergyDynamic"] * (ratio_2q)*2 * freq)
    list_.append (digiq_df.loc["Pulse controller"]["EnergyDynamic"] * (ratio_2q) * freq)
    list_.append (digiq_df.loc["Readout"]["EnergyDynamic"] * (ratio_meas) * freq)
    result["PowerDynamic"] = list_
    
    result["Area"] = result["Area"] * digiq_df["Units"]
    if tech_type == "RSFQ":
        result["PowerStatic"] = result["PowerStatic"] * digiq_df["Units"]
        result["PowerDynamic"] = result["PowerDynamic"] * digiq_df["Units"]
    elif tech_type == "ERSFQ":
        result["PowerStatic"] = result["PowerStatic"] * digiq_df["Units"] * 0
        result["PowerDynamic"] = result["PowerDynamic"] * digiq_df["Units"] * 2
    else:
        print ("ERROR: QIsim supports RSFQ and ERSFQ only.")
        exit ()

    static = result["PowerStatic"].sum ()
    dynamic = result["PowerDynamic"].sum ()
    total_power = static + dynamic
    area = result["Area"].sum ()

    print ("\n================")
    print ("[DigiQ Summary; {} with {} qubits]".format (workload, qubits))
    print ("Frequency:\t\t{}\t\t[GHz]".format (freq))
    print ("Total power:\t\t{0:.1f}\t[nW]".format (total_power))
    print ("\tStatic power:\t{0:.1f}\t[nW]".format (static))
    print ("\tDynamic power:\t{0:.1f}\t[nW]".format (dynamic))
    print ("Area:\t\t\t{}\t[um^2]\n".format (area))
    
    result.to_csv ("results/power_results/device/{}_{}_{}.csv".format (workload, qubits, bs))

    # No SFQ pulse for 2/5 and 1/4 of gate time (for 1Q gate and resonator driving, respectively)
    # We exclude the active load of 2Q gates because they use the DC pulses with superconductor.
    ratio_wire = (stat_df.loc["1q"].item()*sl*3/5 + stat_df.loc["measure"].item()*ml*1/4)/stat_df.loc["latency"].item()
    total_result = dict ()
    wire_df = pd.read_csv ("wires.csv", index_col=0)
    # Total required max. BW per 1152 qubits is 82.8GHz (8.28 cables)
    total_result["power_4k"] = 9*wire_df.loc["microstrip"]["static_4k"] + 9*wire_df.loc["microstrip"]["dynamic_4k"] + total_power
    total_result["device_4k"] = total_power
    total_result["wire_static_4k"] = 9*wire_df.loc["microstrip"]["static_4k"]
    total_result["wire_dynamic_4k"] = 9*wire_df.loc["microstrip"]["dynamic_4k"]
    total_result["power_20mk"] = 6*qubits*wire_df.loc["superconducting_microstrip"]["static_20mk"] + ratio_wire*wire_df.loc["superconducting_microstrip"]["dynamic_20mk"]
    total_result["wire_static_20mk"] = 6*qubits*wire_df.loc["superconducting_microstrip"]["static_20mk"]
    total_result["wire_dynamic_20mk"] = ratio_wire*wire_df.loc["superconducting_microstrip"]["dynamic_20mk"]

    jpm_readout_file = DIGIQ_PATH + "digiq_results/jpm_readout_baseline.csv"
    jpm_readout = pd.read_csv (jpm_readout_file)

    jpm_power = None
    if tech_type == "RSFQ":
        jpm_power = float ((jpm_readout["PowerDynamic"]*2*ratio_meas*freq/ml + jpm_readout["PowerStatic"])*qubits)
    elif tech_type == "ERSFQ":
        jpm_power = float (jpm_readout["PowerDynamic"]*4*ratio_meas*freq/ml*qubits)
    else:
        print ("ERROR: QIsim supports RSFQ and ERSFQ only.")
        exit ()
    total_result["power_20mk"] += jpm_power

    print ("\n[Total power consumption; {} with {} qubits]".format (workload, qubits))
    print ("4K power:\t\t{0:.1f}\t[nW]".format (total_result["power_4k"]))
    print ("\tWire static:\t{0:.1f}\t[nW]".format (total_result["wire_static_4k"]))
    print ("\tWire dynamic:\t{0:.1f}\t[nW]".format (total_result["wire_dynamic_4k"]))
    print ("\t4K device:\t{0:.1f}\t[nW]".format (total_power))
    print ("20mK power:\t\t{0:.1f}\t[nW]".format (total_result["power_20mk"]))
    print ("\tWire static:\t{0:.1f}\t\t[nW]".format (total_result["wire_static_20mk"]))
    print ("\tWire dynamic:\t{0:.1f}\t\t[nW]".format (total_result["wire_dynamic_20mk"]))
    print ("\t20mK device:\t{0:.1f}\t[nW]".format (jpm_power))
    print ("================\n")

    total_result_df = pd.DataFrame.from_dict (total_result, orient="index")
    total_result_df.to_csv ("results/power_results/total/{}_{}_{}.csv".format (workload, qubits, bs))


def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--simulation_mode", "-sm", help="Simulation mode (i.e., NISQ, FTQC)", type=str, default="FTQC")
    parser.add_argument ("--single", "-s", help="1Q-gate time [ns]", type=int, default=25)
    parser.add_argument ("--two", "-t", help="2Q-gate time [ns]", type=int, default=50)
    parser.add_argument ("--measure", "-m", help="Measurement time [ns]", type=int, default=700)
    parser.add_argument ("--groups", "-g", help="#of same-frequency qubit groups in QCI", type=int, default=2)
    parser.add_argument ("--bs", "-b", help="#of different 1Q gates executable in group", type=int, default=8)
    parser.add_argument ("--y_length", "-y", help="Length of RY(pi/2) pulse", type=int, default=197)
    parser.add_argument ("--z_length", "-z", help="Length of RZ pulse (RZ precision)", type=int, default=256)
    parser.add_argument ("--tq_width", "-w", help="DC-pulse precision for CZ gate", type=int, default=4)
    parser.add_argument ("--tech_type", "-c", help="SFQ technology type (i.e., RSFQ, ERSFQ)", type=str, default="RSFQ")
    args = parser.parse_args ()
    return args


if __name__ == "__main__":

    args = arg_parse ()
    sim_mode = args.simulation_mode
    if sim_mode == "FTQC":
        workloads = ["esm"]
        qubit_lists = [2*(n_+1)**2 for n_ in range (3,25,2)]
    elif sim_mode == "NISQ":
        workloads = ['ghz', 'bitcode', 'hamiltonian', 'merminbell', \
                    'phase', 'qaoa_fermionic', 'qaoa_vanilla', 'vqe']
        qubit_lists = [2**n_ for n_ in range (1, 4)]

    sl = args.single
    tl = args.two
    ml = args.measure
    rl = args.measure
    groups = args.groups
    bs = [args.bs]
    y_length = args.y_length
    z_length = args.z_length
    tq_width = args.tq_width
    tech_type = args.tech_type
    
    # Parse the workloads to DigiQ executable.
    print ("Parsing the workloads with the DigiQ executable gate set...")
    parse_workloads ()
    print ("Complete!\n")
    
    # Timing simulation.
    print ("Timing simulation to calculate the execution time...")
    ps = list ()
    for workload in workloads:
        p = None
        p = multiprocessing.Process (target=timing_adjustment_threading, \
                args=(workload, qubit_lists, sl, tl, ml, rl, groups, bs))
        p.start ()
        ps.append (p)
    
    for p_ in ps:
        p_.join ()
    print ("Complete!\n")
    
    # Report power consumption.
    print ("Calculate runtime power consumption of DigiQ for each workload...")
    for workload in workloads:
        for bs_ in bs:
            for qubits in qubit_lists:
                power_calculation (workload, qubits, sl, tl, ml, rl, groups, \
                                   bs_, y_length, z_length, tq_width, tech_type)
    
    print ("Complete!")
    print ("You can find all of the simulation results in ./results file.\n")
