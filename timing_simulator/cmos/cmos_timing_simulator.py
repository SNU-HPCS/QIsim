import pandas as pd
import numpy as np
from math import *
import decimal, os, multiprocessing, warnings, argparse, json

warnings.simplefilter (action='ignore', category=FutureWarning)
warnings.simplefilter (action='ignore', category=DeprecationWarning)


### WORKLOAD PARSER

def insert_cx (cq, tq, q1_name, q2_name, file):
    # Hadamard
    file.write ("ry(pi*{}) {}[{}];\n".format (0.5, q2_name, tq))
    file.write ("rx(pi*{}) {}[{}];\n".format (1.0, q2_name, tq))
    # CZ
    file.write ("cz {}[{}],{}[{}];\n".format (q1_name, cq, q2_name, tq)) 
    # Hadamard
    file.write ("rz(pi*{}) {}[{}];\n".format (1.0, q2_name, tq))
    file.write ("ry(pi*{}) {}[{}];\n".format (0.5, q2_name, tq))

def insert_ccx (cq1, cq2, tq, q1_name, q2_name, q3_name, file):
    # H 3
    file.write ("rz(pi*{}) {}[{}];\n".format (1.0, q3_name, tq))
    file.write ("ry(pi*{}) {}[{}];\n".format (0.5, q3_name, tq))
    # CX 2,3
    insert_cx (cq2, tq, q2_name, q3_name, file)
    # TDG 3
    file.write ("rz(pi*{}) {}[{}];\n".format (-0.25, q3_name, tq))
    # CX 1,3
    insert_cx (cq1, tq, q1_name, q3_name, file)
    # T 3
    file.write ("rz(pi*{}) {}[{}];\n".format (0.25, q3_name, tq))
    # CX 2,3
    insert_cx (cq2, tq, q2_name, q3_name, file)
    # TDG 3
    file.write ("rz(pi*{}) {}[{}];\n".format (-0.25, q3_name, tq))
    # CX 1,3
    insert_cx (cq1, tq, q1_name, q3_name, file)
    # T 2
    file.write ("rz(pi*{}) {}[{}];\n".format (0.25, q2_name, cq2))
    # T 3
    file.write ("rz(pi*{}) {}[{}];\n".format (0.25, q3_name, tq))
    # H 3
    file.write ("ry(pi*{}) {}[{}];\n".format (-0.5, q3_name, tq))
    file.write ("rz(pi*{}) {}[{}];\n".format (1.0, q3_name, tq))
    # CX 1,2
    insert_cx (cq1, cq2, q1_name, q2_name, file)
    # T 1
    file.write ("rz(pi*{}) {}[{}];\n".format (0.25, q1_name, cq1))
    # TDG 2
    file.write ("rz(pi*{}) {}[{}];\n".format (-0.25, q2_name, cq2))
    # CX 1,2
    insert_cx (cq1, cq2, q1_name, q2_name, file)

def parse_circuit (workload, nq):
    parse_file = "./workloads_parse/{}_{}".format (workload, nq)
       
    if not os.path.isfile (parse_file):
        file = "./workloads/{}_{}".format (workload, nq)
        nf = open (parse_file, "w")
        f = open (file, "r")
        lines = f.readlines ()
        prev_line = ""
        q_names = list()
        
        for n, line in enumerate (lines):
            words = line.split (' ')

            if words[0] == "qreg":
                qubits = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                q_names.append(q_name)

            # Insert barrier between start of measure and reset for timing optimization
            if (words[0] == "measure" and prev_line.split (' ')[0] != "measure") or \
                (words[0] != "measure" and prev_line.split (' ')[0] == "measure") or \
                (words[0] == "reset" and prev_line.split (' ')[0] != "reset") or \
                (words[0] != "reset" and prev_line.split (' ')[0] == "reset"):
                inst_ = "barrier "
                for n_, qubit_ in enumerate (q_names):
                    if n_ == 0:
                        inst_ = inst_ + qubit_
                    else:
                        inst_ = inst_ + "," + qubit_
                inst_ = inst_ + ";\n"
                nf.write (inst_)

            # Pauli gates (X,Y,Z).
            if words[0] == "x" or words[0] == "X":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                nf.write ("rx(pi*{}) {}[{}];\n".format (1.0, q_name, qubit))
            elif words[0] == "y" or words[0] == "Y":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                nf.write ("ry(pi*{}) {}[{}];\n".format (1.0, q_name, qubit))
            elif words[0] == "z" or words[0] == "Z":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                nf.write ("rz(pi*{}) {}[{}];\n".format (1.0, q_name, qubit))

            # H, SDG, S gates.
            elif words[0] == "h":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                nf.write ("rz(pi*{}) {}[{}];\n".format (1.0, q_name, qubit))
                nf.write ("ry(pi*{}) {}[{}];\n".format (0.5, q_name, qubit))
            elif words[0] == "sdg":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                nf.write ("rz(pi*{}) {}[{}];\n".format (-0.5, q_name, qubit))
            elif words[0] == "s":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                nf.write ("rz(pi*{}) {}[{}];\n".format (0.5, q_name, qubit))
            elif words[0] == "t":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                nf.write ("rz(pi*{}) {}[{}];\n".format (0.25, q_name, qubit))
            elif words[0] == "tdg":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                nf.write ("rz(pi*{}) {}[{}];\n".format (-0.25, q_name, qubit))

            # RX, RY, RZ gates.
            elif words[0].split ("(")[0] == "rx":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                angle = None
                if "pi" in words[0]:
                    angle = float (words[0].split ("*")[1].split (")")[0])*180
                else:
                    angle = float (words[0].split ("(")[1].split (")")[0])/pi*180
                if (angle % 45) <= 0.01 or (45 - angle % 45) <= 0.01:
                    angle = angle % 360
                    if angle >= 180:
                        nf.write ("rx(pi*{}) {}[{}];\n".format (1.0, q_name, qubit))
                        angle -= 180
                    if angle >= 90:
                        nf.write ("rx(pi*{}) {}[{}];\n".format (0.5, q_name, qubit))
                        angle -= 90
                    if angle >= 45:
                        nf.write ("rx(pi*{}) {}[{}];\n".format (0.25, q_name, qubit))
                else :
                    nf.write ("ry(pi*{}) {}[{}];\n".format (0.5, q_name, qubit))
                    nf.write ("rz(pi*{}) {}[{}];\n".format ((180 - angle)/180, q_name, qubit))
                    nf.write ("ry(pi*{}) {}[{}];\n".format (0.5, q_name, qubit))
                    nf.write ("rz(pi*{}) {}[{}];\n".format (1.0, q_name, qubit))
            elif words[0].split ("(")[0] == "ry":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                angle = None
                if "pi" in words[0]:
                    angle = float (words[0].split ("*")[1].split (")")[0])*180
                else:
                    angle = float (words[0].split ("(")[1].split (")")[0])/pi*180
                if (angle % 45) <= 0.01 or (45 - angle % 45) <= 0.01:
                    angle = angle % 360
                    if angle >= 180:
                        nf.write ("ry(pi*{}) {}[{}];\n".format (1.0, q_name, qubit))
                        angle -= 180
                    if angle >= 90:
                        nf.write ("ry(pi*{}) {}[{}];\n".format (0.5, q_name, qubit))
                        angle -= 90
                    if angle >= 45:
                        nf.write ("ry(pi*{}) {}[{}];\n".format (0.25, q_name, qubit))
                else :
                    nf.write ("rz(pi*{}) {}[{}];\n".format (1.0, q_name, qubit))
                    nf.write ("rx(pi*{}) {}[{}];\n".format (0.5, q_name, qubit))
                    nf.write ("rz(pi*{}) {}[{}];\n".format ((180 - angle)/180, q_name, qubit))
                    nf.write ("rx(pi*{}) {}[{}];\n".format (0.5, q_name, qubit))
            elif words[0].split ("(")[0] == "rz":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                angle = None
                if "pi" in words[0]:
                    angle = float (words[0].split ("*")[1].split (")")[0])*180
                else:
                    angle = float (words[0].split ("(")[1].split (")")[0])/pi*180
                nf.write ("rz(pi*{}) {}[{}];\n".format (angle/180, q_name, qubit))

            # Two-qubit gates (CX, SWAP).
            elif words[0] == "cx":
                cq = int (words[1].split (",")[0].split ("[")[1].split ("]")[0])
                tq = int (words[1].split (",")[1].split ("[")[1].split ("]")[0])
                q1_name = words[1].split (",")[0].split ("[")[0]
                q2_name = words[1].split (",")[1].split ("[")[0]
                insert_cx (cq, tq, q1_name, q2_name, nf)
            elif words[0] == "swap":
                cq = int (words[1].split (",")[0].split ("[")[1].split ("]")[0])
                tq = int (words[1].split (",")[1].split ("[")[1].split ("]")[0])
                q1_name = words[1].split (",")[0].split ("[")[0]
                q2_name = words[1].split (",")[1].split ("[")[0]
                insert_cx (cq, tq, q1_name, q2_name, nf)
                insert_cx (tq, cq, q2_name, q1_name, nf)
                insert_cx (cq, tq, q1_name, q2_name, nf)

            # Three-qubit gates (Toffoli; CCX)
            elif words[0] == "ccx":
                cq1 = int (words[1].split (",")[0].split ("[")[1].split ("]")[0])
                cq2 = int (words[1].split (",")[1].split ("[")[1].split ("]")[0])
                tq = int (words[1].split (",")[2].split ("[")[1].split ("]")[0])
                q1_name = words[1].split (",")[0].split ("[")[0]
                q2_name = words[1].split (",")[1].split ("[")[0]
                q3_name = words[1].split (",")[2].split ("[")[0]
                insert_ccx (cq1, cq2, tq, q1_name, q2_name, q3_name, nf)
            else:
                nf.write (line)
            if (words[0] != "//") or (not line.isspace ()):
                prev_line = line
        return

# Optimizing parsed workloads
def insert_xyz (gate, qubit, q_name, opt_list, x_angles, y_angles, z_angles):
    x_angle = x_angles[q_name][qubit]
    y_angle = y_angles[q_name][qubit]
    z_angle = z_angles[q_name][qubit]
    x_angle = x_angle % 2
    y_angle = y_angle % 2
    z_angle = z_angle % 2
    if gate != "x" and x_angle !=  0:
        if x_angle >= 1.0:
            opt_list.append ("rx(pi*{}) {}[{}];".format (1.0, q_name, qubit))
            x_angle -= 1.0
        if x_angle >= 0.5:
            opt_list.append ("rx(pi*{}) {}[{}];".format (0.5, q_name, qubit))
            x_angle -= 0.5
        if x_angle >= 0.25:
            opt_list.append ("rx(pi*{}) {}[{}];".format (0.25, q_name, qubit))
        x_angles[q_name][qubit] = 0.0
    if gate != "y" and y_angle !=  0:
        if y_angle >= 1.0:
            opt_list.append ("ry(pi*{}) {}[{}];".format (1.0, q_name, qubit))
            y_angle -= 1.0
        if y_angle >= 0.5:
            opt_list.append ("ry(pi*{}) {}[{}];".format (0.5, q_name, qubit))
            y_angle -= 0.5
        if y_angle >= 0.25:
            opt_list.append ("ry(pi*{}) {}[{}];".format (0.25, q_name, qubit))
        y_angles[q_name][qubit] = 0.0
    if gate != "z" and z_angle !=  0:
        opt_list.append ("rz(pi*{}) {}[{}];".format (z_angle, q_name, qubit))
        z_angles[q_name][qubit] = 0.0

        

def optimize_circuit (workload, nq):
    new_file = "./workloads_opt/{}_{}".format (workload, nq)
    # if os.path.isfile (new_file):
    if False:
        return
    parse_file = open("./workloads_parse/{}_{}".format (workload, nq), "r")
    x_angles = dict()
    y_angles = dict()
    z_angles = dict()

    insts = parse_file.read()
    inst_list = insts.split("\n")
    mr_list = list()

    while 1:
        opt_list = list()
        for inst_ in inst_list.copy ():
            words = inst_.split(' ')
            op = words[0].split("(")[0]

            if op != "barrier" and op != "measure" and op != "reset" and len(mr_list) != 0:
                for mr_inst_ in mr_list:
                    opt_list.append(mr_inst_)
                mr_list = list()
            # Build the x,y,z-angle objects
            if op == "qreg":
                qubits = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                x_angles[q_name] = [0 for _ in range (qubits)]
                y_angles[q_name] = [0 for _ in range (qubits)]
                z_angles[q_name] = [0 for _ in range (qubits)]
                opt_list.append(inst_)

            # X, Y, Z gates
            elif op == "rx":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                angle = float (words[0].split("*")[1].split(")")[0])
                insert_xyz ("x", qubit, q_name, opt_list, x_angles, y_angles, z_angles)
                x_angles[q_name][qubit] += angle
            elif op == "ry":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                angle = float (words[0].split("*")[1].split(")")[0])
                insert_xyz ("y", qubit, q_name, opt_list, x_angles, y_angles, z_angles)
                y_angles[q_name][qubit] += angle
            elif op == "rz":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                angle = float (words[0].split("*")[1].split(")")[0])
                insert_xyz ("z", qubit, q_name, opt_list, x_angles, y_angles, z_angles)
                z_angles[q_name][qubit] += angle

            # Barrier
            elif op == "barrier":
                mr_list.append(inst_)
            # Measure, reset
            elif op == "measure":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                insert_xyz (" ", qubit, q_name, opt_list, x_angles, y_angles, z_angles)
                mr_list.append(inst_) 
            elif op == "reset":
                qubit = int (words[1].split ("[")[1].split ("]")[0])
                q_name = words[1].split ("[")[0]
                insert_xyz (" ", qubit, q_name, opt_list, x_angles, y_angles, z_angles)
                mr_list.append(inst_) 

            # CZ gate
            elif op == "cz":
                cq = int (words[1].split (",")[0].split ("[")[1].split("]")[0])
                tq = int (words[1].split (",")[1].split ("[")[1].split("]")[0])
                q1_name = words[1].split (",")[0].split("[")[0]
                q2_name = words[1].split (",")[1].split("[")[0]
                insert_xyz (" ", cq, q1_name, opt_list, x_angles, y_angles, z_angles)
                insert_xyz (" ", tq, q2_name, opt_list, x_angles, y_angles, z_angles)
                opt_list.append(inst_) 

            # etc
            else:
                opt_list.append(inst_)
        if len(mr_list) != 0:
            for mr_inst_ in mr_list:
                opt_list.append(mr_inst_)
            mr_list = list()
                    
        if inst_list == opt_list:
            break
        else:
            inst_list = opt_list

    nf = open(new_file, "w")
    for inst_ in opt_list:
        nf.write (inst_+"\n")

    


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
        print ("Parsing {} / {}".format (workload, qubit))
        parse_circuit (workload, qubit)
        print ("Optimizing {} / {}".format (workload, qubit))
        optimize_circuit (workload, qubit)

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

def timing_adjustment (architecture, workload, qubits, sl, tl, ml, rl, qubit_per_group, channel_per_group, readout_group):
    
    if os.path.isfile ("workloads_final/{}_{}_{}".format (architecture, workload, qubits)):
        return

    text_file = open ("workloads_opt/{}_{}".format (workload, qubits), "r")
    new_file = open ("workloads_final/{}/{}_{}".format (architecture, workload, qubits), "w")
    data = text_file.read ()
    data_list = data.split ("\n")
    gate_sequence_per_qubit = dict() # remaining gate sequence for each qubits
    cur_gate_per_qubit = dict() # currently executing gate or waiting CZ gates
    valid_gate_per_qubit = dict() # validity (wait time decreases only if the qubit is valid)
    wait_time_per_qubit = dict() # remaining cycle for completing operation
    virtual_z = dict()
        
    cycle_time = float_gcd(float_gcd(float_gcd(sl, tl), ml), rl)
    sl, tl, ml, rl = int(decimal.Decimal("{}".format(sl)) // decimal.Decimal("{}".format(cycle_time))),\
                    int(decimal.Decimal("{}".format(tl)) // decimal.Decimal("{}".format(cycle_time))), \
                    int(decimal.Decimal("{}".format(ml)) // decimal.Decimal("{}".format(cycle_time))), \
                    int(decimal.Decimal("{}".format(rl)) // decimal.Decimal("{}".format(cycle_time)))
    global_clock = 0
    
    # 300K CMOS, Multiplexer version 1, and photonic link architecture
    if architecture == "300k_cmos":
        num_1q = 0
        num_2q = 0
        num_meas = 0
        num_reset = 0

        # Initializing dicts 
        for n, inst_ in enumerate(data_list.copy()):
            words = inst_.split(" ")
            if any ((key_ in words[0]) for key_ in ["//", "OPENQASM", "include", "qreg", "creg"]):
                if words[0] == "qreg":
                    qubits_ = int (words[1].split ("[")[1].split ("]")[0])
                    q_name = words[1].split ("[")[0]
                    gate_sequence_per_qubit[q_name] = [list() for _ in range (qubits_)]
                    cur_gate_per_qubit[q_name] = [" " for _ in range (qubits_)]
                    valid_gate_per_qubit[q_name] = [1 for _ in range (qubits_)]
                    wait_time_per_qubit[q_name] = [0 for _ in range (qubits_)]
                    virtual_z[q_name] = [" " for _ in range (qubits_)]
                if words[0] == "//" or words[0] == "barrier":
                    data_list.remove(inst_)
                else:
                    new_file.write(inst_ + "\n")
                    data_list.remove(inst_)
            
            if any ((key_ in words[0]) for key_ in ["reset"]):
                num_reset += 1


        # Initializing gate_sequence_per_qubit & num_gate
        num_gate = 0 # Total nubmer of gates(or operations).  
        cz_num = 0 # for labeling CZ gates
        for n, inst_ in enumerate(data_list.copy()):
            words = inst_.split(' ')
            op = words[0].split("(")[0]
            
            if op == "rx" or op == "ry" or op == "rz" or words[0] == "measure" or words[0] == "reset":
                qubit = int(words[1].split("[")[1].split("]")[0])
                q_name = words[1].split("[")[0]
                gate_sequence_per_qubit[q_name][qubit].append(inst_)
                num_gate += 1

                if op == "rx" or op == "ry":
                    num_1q += 1
                elif words[0] == "measure":
                    num_meas += 1

            if words[0] == "cz":
                cz_num += 1
                cq = int (words[1].split (",")[0].split ("[")[1].split ("]")[0])
                tq = int (words[1].split (",")[1].split ("[")[1].split ("]")[0])
                q1_name = words[1].split (",")[0].split ("[")[0]
                q2_name = words[1].split (",")[1].split ("[")[0]
                gate_sequence_per_qubit[q1_name][cq].append(inst_ + " {}".format(cz_num))
                gate_sequence_per_qubit[q2_name][tq].append(inst_ + " {}".format(cz_num))
                num_gate += 2
                num_2q += 1
            
        # For CZ gate's validity check
        cz_num_list = list() # [CZ gate #, ...]
        cz_target_list = list() # [(qubit name, qubit #)]

        while 1:
            is_1q_counted = 0
            is_2q_counted = 0
            is_meas_counted = 0
            is_reset_counted = 0
            is_rz = 0
            # new gate fetch only if there are completed gates
            if min([min(wait_time_per_qubit[key_]) for key_ in wait_time_per_qubit.keys()]) == 0:
                timing_point_generated = 0
                for q_name in wait_time_per_qubit.keys():
                    for qubit in range(len(wait_time_per_qubit[q_name])):
                        if wait_time_per_qubit[q_name][qubit] == 0:
                            if len(gate_sequence_per_qubit[q_name][qubit]) != 0:
                                # Timing point generate
                                if timing_point_generated == 0:
                                    new_file.write("//** {}ns\n".format (float(global_clock * decimal.Decimal("{}".format(cycle_time)))))
                                    timing_point_generated += 1
                                # Get new gate
                                inst_ = gate_sequence_per_qubit[q_name][qubit].pop(0)
                                words = inst_.split(" ")
                                op = words[0].split("(")[0]

                                if op == "rz":
                                    is_rz = 1
                                    virtual_z[q_name][qubit] = inst_
                                    num_gate -= 1

                                elif op == "rx" or op == "ry":
                                    # Fetch new gate
                                    cur_gate_per_qubit[q_name][qubit] = "rxyz"     
                                    if virtual_z[q_name][qubit] != " ":
                                        new_file.write(virtual_z[q_name][qubit] + "\n")
                                        virtual_z[q_name][qubit] = " "
                                    new_file.write(inst_ + "\n")
                                    num_gate -= 1
                                    wait_time_per_qubit[q_name][qubit] = sl

                                elif op == "cz":
                                    cz_label = int(words[-1])
                                    cur_gate_per_qubit[q_name][qubit] = "cz {}".format(cz_label)
                                    if cz_label in cz_num_list:
                                        # Fetch new CZgate only if every target qubits of the CZ gate is ready
                                        (tq_name, tq) = cz_target_list[cz_num_list.index(cz_label)]
                                        valid_gate_per_qubit[q_name][qubit] = 1
                                        valid_gate_per_qubit[tq_name][tq] = 1
                                        cz_num_list.remove(cz_label)
                                        cz_target_list.remove((tq_name, tq))
                                        if virtual_z[q_name][qubit] != " ":
                                            new_file.write(virtual_z[q_name][qubit] + "\n")
                                            virtual_z[q_name][qubit] = " "
                                        if virtual_z[tq_name][tq] != " ":
                                            new_file.write(virtual_z[tq_name][tq] + "\n")
                                            virtual_z[tq_name][tq] = " "
                                        new_file.write(remove_suffix(inst_, " {}".format(cz_label)) + "\n")
                                        num_gate -= 2
                                    else:
                                        cz_num_list.append(cz_label)
                                        cz_target_list.append((q_name, qubit))
                                        valid_gate_per_qubit[q_name][qubit] = 0
                                    wait_time_per_qubit[q_name][qubit] = tl

                                elif op == "measure":
                                    # Fetch new gate
                                    cur_gate_per_qubit[q_name][qubit] = "measure" 
                                    virtual_z[q_name][qubit] = " "    
                                    new_file.write(inst_ + "\n")
                                    num_gate -= 1
                                    wait_time_per_qubit[q_name][qubit] = ml

                                elif op == "reset":
                                    # Fetch new gate
                                    cur_gate_per_qubit[q_name][qubit] = "reset"     
                                    new_file.write(inst_ + "\n")
                                    num_gate -= 1
                                    wait_time_per_qubit[q_name][qubit] = rl

                                else:
                                    print("Our model does not support {} operation\n".format(op))
                                    exit
                            else :
                                # Update wait time, currengt gate info, and valid info of operation done qubits
                                cur_gate_per_qubit[q_name][qubit] = " "
                                valid_gate_per_qubit[q_name][qubit] = 0
                                wait_time_per_qubit[q_name][qubit] = 0.1 
            # Reduce wait time by 1 only valid qubits
            if is_rz == 0:
                for q_name in valid_gate_per_qubit.keys():
                        for qubit in range(len(valid_gate_per_qubit[q_name])):
                            if valid_gate_per_qubit[q_name][qubit] == 1:
                                wait_time_per_qubit[q_name][qubit] -= 1
                global_clock += 1

            # If there is no gate to execute, generate the last timing point by adding max waiting time
            if num_gate == 0:
                max_wait_time = int(max(max([wait_time_per_qubit[key_] for key_ in wait_time_per_qubit.keys()])))
                global_clock += max_wait_time
                if max_wait_time >= 1:
                    new_file.write("//** {}ns\n".format (float(global_clock * decimal.Decimal("{}".format(cycle_time)))))        
                break
        stat = {'1q': int(num_1q), '2q': int(num_2q), 'measure': int(num_meas), 'reset': int (num_reset),\
                'latency': float(global_clock * decimal.Decimal("{}".format(cycle_time)))}
        stat_df = pd.DataFrame.from_dict (stat, orient='index')
        stat_df.to_csv ("results/stats/{}/{}_{}.csv".format (architecture, workload, qubits))

    # Intel horseridge architecture
    elif architecture == "horseridge":
        num_qubit_1q = 0 # 1q inst num
        num_group_1q = 0 # Sum of 1q inst num per drive group 
        num_z = 0 # z gates (e.g., rz, s, sdg, z...).
        num_qubit_2q = 0 # 2q inst num * 2
        num_inst_per_total_2q = 0 # 2q activation num * 2
        num_qubit_meas = 0 # measure inst num
        num_group_meas = 0 # Sum of measure inst num per readout group 
        num_qubit_reset = 0 # reset inst num

        qubit_count = 0
        # Initializing dicts 
        sg_operating = dict() # {(group #, channel #): 0 or 1}
        sg_operate_cycle_gr = dict() # {group # : operate cycle #}
        tg_operating = 0  # number of operating 2q
        meas_operating = dict() # {meas group # : number of operating measure}
        meas_operate_cycle = dict() # {meas group # : operate cycle #}
        for n, inst_ in enumerate(data_list.copy()):
            words = inst_.split(" ")
            if any ((key_ in words[0]) for key_ in ["//", "OPENQASM", "include", "qreg", "creg"]):
                if words[0] == "qreg":
                    qubits_ = int (words[1].split ("[")[1].split ("]")[0])
                    q_name = words[1].split ("[")[0]
                    gate_sequence_per_qubit[q_name] = [list() for _ in range (qubits_)]
                    cur_gate_per_qubit[q_name] = [" " for _ in range (qubits_)]
                    valid_gate_per_qubit[q_name] = [1 for _ in range (qubits_)]
                    wait_time_per_qubit[q_name] = [0 for _ in range (qubits_)]
                    virtual_z[q_name] = [" " for _ in range (qubits_)]
                    qubit_count += qubits_
                if words[0] == "//" or words[0] == "barrier":
                    data_list.remove(inst_)
                else:
                    new_file.write(inst_ + "\n")
                    data_list.remove(inst_)
            
            if any ((key_ in words[0]) for key_ in ["reset"]):
                num_qubit_reset += 1

        # Initializing gate_sequence_per_qubit & num_gate
        num_gate = 0 # Total nubmer of gates(or operations).  
        cz_label = 0 # for labeling CZ gates
        #barrier_label = 0 # for labeling barriers
        
        # Assign group # and channel # of qubits
        qubit_info = dict() # {(q_name, qubit #) : [group #, channel #], ...}
        qubit_meas_info = dict() # {(q_name, qubit #) : readout group #, ...}
        group_num = (qubit_count - 1) // qubit_per_group + 1
        meas_group_num = (qubit_count - 1) // readout_group + 1
        for gr_num_ in range(group_num):
            for ch_num_ in range(channel_per_group):
                sg_operating[(gr_num_, ch_num_)] = 0
            sg_operate_cycle_gr[gr_num_] = 0
        for m_gr_num_ in range(meas_group_num):
            meas_operating[m_gr_num_] = 0
            meas_operate_cycle[m_gr_num_] = 0

        cnt = 0
        for q_name in cur_gate_per_qubit.keys():
            for qubit in range(len(cur_gate_per_qubit[q_name])):
                qubit_info[(q_name, qubit)] = 0
                qubit_meas_info[(q_name, qubit)] = cnt // readout_group
                cnt += 1

        channel_qubit_count = np.zeros((group_num, channel_per_group), int)
        for i in range(group_num - 1):
            for j in range(channel_per_group):
                channel_qubit_count[i][j] = qubit_per_group // channel_per_group
            for k in range(qubit_per_group % channel_per_group):
                channel_qubit_count[i][k] += 1
        for i in range(channel_per_group):
            channel_qubit_count[-1][i] = ((qubit_count - 1) % qubit_per_group + 1) // channel_per_group
        for i in range(((qubit_count - 1) % qubit_per_group + 1) % channel_per_group):
            channel_qubit_count[-1][i] += 1

        cnt = 0
        qubit_info_keys = list(qubit_info.keys())
        for i in range(len(channel_qubit_count)):
            for j in range(len(channel_qubit_count[0])):
                for k in range(channel_qubit_count[i][j]):
                    qubit_info[qubit_info_keys[cnt]] = [i, j]
                    cnt += 1
                
        for n, inst_ in enumerate(data_list.copy()):
            words = inst_.split(' ')
            op = words[0].split("(")[0]
            
            if op == "rx" or op == "ry" or op == "rz" or words[0] == "measure" or words[0] == "reset":
                qubit = int(words[1].split("[")[1].split("]")[0])
                q_name = words[1].split("[")[0]
                gate_sequence_per_qubit[q_name][qubit].append(inst_)
                num_gate += 1

                if op == "rx" or op == "ry":
                    num_qubit_1q += 1
                elif words[0] == "measure":
                    num_qubit_meas += 1
                    
            if words[0] == "cz":
                cz_label += 1
                cq = int (words[1].split (",")[0].split ("[")[1].split ("]")[0])
                tq = int (words[1].split (",")[1].split ("[")[1].split ("]")[0])
                q1_name = words[1].split (",")[0].split ("[")[0]
                q2_name = words[1].split (",")[1].split ("[")[0]
                gate_sequence_per_qubit[q1_name][cq].append(inst_ + " {}".format(cz_label))
                gate_sequence_per_qubit[q2_name][tq].append(inst_ + " {}".format(cz_label))
                num_gate += 2
                num_qubit_2q += 2

            '''
            if words[0] == "barrier":
                barrier_label += 1
                for q_name in gate_sequence_per_qubit.keys():
                    for qubit in range(len(gate_sequence_per_qubit[q_name])):
                        gate_sequence_per_qubit[q_name][qubit].append(inst_ + " {}".format(barrier_label))
                        num_gate += 1
            '''

        # For CZ gate's validity check
        cz_num_list = list() # [CZ gate #, ...]
        cz_target_list = list() # [(qubit name, qubit #)]
        #barrier_list = dict() # {barrier # : barrier count}
        while 1:
            is_rz = 0
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

                                if cur_gate_per_qubit[q_name][qubit].split("(")[0] == "rx" or cur_gate_per_qubit[q_name][qubit].split("(")[0] == "ry":
                                    sg_operating[(qubit_info[(q_name, qubit)][0], qubit_info[(q_name, qubit)][1])] -= 1
                                elif cur_gate_per_qubit[q_name][qubit] == "measure":
                                    meas_operating[qubit_meas_info[(q_name, qubit)]] -= 1
                                elif cur_gate_per_qubit[q_name][qubit].split(" ")[0] == "cz":
                                    tg_operating -= 1

                                # Timing point generate
                                if timing_point_generated == 0 :
                                    new_file.write("//** {}ns\n".format (float(global_clock * decimal.Decimal("{}".format(cycle_time))))) 
                                    timing_point_generated += 1

                                # Get new gate        
                                # Single qubit gates                
                                if op == "rz":
                                    is_rz = 1
                                    virtual_z[q_name][qubit] = inst_
                                    num_gate -= 1
                                    cur_gate_per_qubit[q_name][qubit] = words[0]
                                    num_z += 1

                                elif op == "rx" or op == "ry":
                                    # Fetch new gate
                                    # channel_count update
                                    cur_gate_per_qubit[q_name][qubit] = words[0]
                                    wait_time_per_qubit[q_name][qubit] = sl
                                    valid_gate_per_qubit[q_name][qubit] = 0

                                # Two qubit gate
                                elif op == "cz":
                                    cz_label = int(words[-1])
                                    cur_gate_per_qubit[q_name][qubit] = "cz {}".format(cz_label)
                                    if cz_label in cz_num_list:
                                        # Fetch new CZgate only if every target qubits of the CZ gate is ready
                                        (tq_name, tq) = cz_target_list[cz_num_list.index(cz_label)]
                                        valid_gate_per_qubit[q_name][qubit] = 1
                                        valid_gate_per_qubit[tq_name][tq] = 1
                                        cz_num_list.remove(cz_label)
                                        cz_target_list.remove((tq_name, tq))
                                        if virtual_z[q_name][qubit] != " ":
                                            new_file.write(virtual_z[q_name][qubit] + "\n")
                                            virtual_z[q_name][qubit] = " "
                                        if virtual_z[tq_name][tq] != " ":
                                            new_file.write(virtual_z[tq_name][tq] + "\n")
                                            virtual_z[tq_name][tq] = " "
                                        new_file.write(remove_suffix(inst_, " {}".format(cz_label)) + "\n")
                                        num_gate -= 2
                                        tg_operating += 2
                                    else:
                                        cz_num_list.append(cz_label)
                                        cz_target_list.append((q_name, qubit))
                                        valid_gate_per_qubit[q_name][qubit] = 0
                                    wait_time_per_qubit[q_name][qubit] = tl

                                # Measure
                                elif op == "measure":
                                    # Fetch new gate
                                    cur_gate_per_qubit[q_name][qubit] = "measure"
                                    virtual_z[q_name][qubit] = " "      
                                    new_file.write(inst_ + "\n")
                                    num_gate -= 1
                                    wait_time_per_qubit[q_name][qubit] = ml
                                    meas_operating[qubit_meas_info[(q_name, qubit)]] += 1

                                # Reset    
                                elif op == "reset":
                                    # Fetch new gate
                                    cur_gate_per_qubit[q_name][qubit] = "reset"     
                                    new_file.write(inst_ + "\n")
                                    num_gate -= 1
                                    wait_time_per_qubit[q_name][qubit] = rl
                                
                                # Barrier
                                #elif op == "barrier":
                                #    barrier_label_ = int(words[-1])
                                #    cur_gate_per_qubit[q_name][qubit] = "barrier {}".format(barrier_label_) 
                                #    if len(barrier_list) != 0:
                                #        barrier_list[barrier_label_] += 1
                                #    else:
                                #        barrier_list[barrier_label_] = 1
                                #    valid_gate_per_qubit[q_name][qubit] = 0
                                #    wait_time_per_qubit[q_name][qubit] = 1

                                # etc
                                else:
                                    print("Our model does not support {} operation\n".format(op))
                                    exit
                            else :
                                if cur_gate_per_qubit[q_name][qubit].split("(")[0] == "rx" or cur_gate_per_qubit[q_name][qubit].split("(")[0] == "ry":
                                    sg_operating[(qubit_info[(q_name, qubit)][0], qubit_info[(q_name, qubit)][1])] -= 1
                                elif cur_gate_per_qubit[q_name][qubit] == "measure":
                                    meas_operating[qubit_meas_info[(q_name, qubit)]] -= 1
                                elif cur_gate_per_qubit[q_name][qubit].split(" ")[0] == "cz":
                                    tg_operating -= 1
                                # Update wait time, currengt gate info, and valid info of operation done qubits
                                cur_gate_per_qubit[q_name][qubit] = " "
                                valid_gate_per_qubit[q_name][qubit] = 0
                                wait_time_per_qubit[q_name][qubit] = 0.1 

            if is_rz == 0:
                # Only one qubit can execute single qubit gate for each channel in one cycle
                for _, (gr_num_, ch_num_) in enumerate(sg_operating.keys()):
                    if sg_operating[(gr_num_, ch_num_)] == 0:
                        is_selected = 0
                        for _, (q_name, qubit) in enumerate(qubit_info.keys()):
                            if qubit_info[(q_name, qubit)] == [gr_num_, ch_num_]:
                                cur_inst_ = cur_gate_per_qubit[q_name][qubit]
                                if cur_inst_.split("(")[0] == "rx" or cur_inst_.split("(")[0] == "ry":
                                    if is_selected == 0:
                                        valid_gate_per_qubit[q_name][qubit] = 1
                                        if virtual_z[q_name][qubit] != " ":
                                            new_file.write(virtual_z[q_name][qubit] + "\n")
                                            virtual_z[q_name][qubit] = " "  
                                        new_file.write("{} {}[{}];\n".format(cur_inst_, q_name, qubit))
                                        num_gate -= 1
                                        is_selected = 1
                                        sg_operating[(gr_num_, ch_num_)] += 1
                                    else:
                                        valid_gate_per_qubit[q_name][qubit] = 0
                for gr_num_ in range((qubit_count - 1) // qubit_per_group + 1):
                    is_group_operating = 0
                    for ch_num_ in range(channel_per_group):
                        if sg_operating[(gr_num_, ch_num_)] >= 1:
                            is_group_operating = 1
                    if is_group_operating == 1:
                        sg_operate_cycle_gr[gr_num_] += 1

                for m_gr_num_ in meas_operating.keys():
                    if meas_operating[m_gr_num_] > 0:
                        meas_operate_cycle[m_gr_num_] += 1
                
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
                max_1q = np.zeros(group_num, int)
                max_2q = 0
                max_meas = np.zeros(meas_group_num, int)
                for qname_ in cur_gate_per_qubit.keys():
                    for qnum_, cur_gate_ in enumerate(cur_gate_per_qubit[qname_]):
                        if (cur_gate_.split("(")[0] == "rx" or cur_gate_.split("(")[0] == "ry") and max_1q[qubit_info[(qname_, qnum_)][0]] < wait_time_per_qubit[qname_][qnum_]:
                            max_1q[qubit_info[(qname_, qnum_)][0]] = wait_time_per_qubit[qname_][qnum_]
                        elif cur_gate_.split(" ")[0] == "cz" and max_2q < wait_time_per_qubit[qname_][qnum_]:
                            max_2q = wait_time_per_qubit[qname_][qnum_]
                        elif cur_gate_ == "measure" and max_meas[qubit_meas_info[(qname_, qnum_)]] < wait_time_per_qubit[qname_][qnum_]:
                            max_meas[qubit_meas_info[(qname_, qnum_)]] = wait_time_per_qubit[qname_][qnum_]
                for gnum_, max_wait_1q_per_group in enumerate(max_1q):
                    if max_wait_1q_per_group >= 1:
                        sg_operate_cycle_gr[gnum_] += max_wait_1q_per_group
                if max_2q >= 1: num_inst_per_total_2q += 2 * max_2q
                for m_gnum_, max_wait_meas_per_group in enumerate(max_meas):
                    if max_wait_meas_per_group >= 1:
                        meas_operate_cycle[m_gnum_] += max_wait_meas_per_group
                max_wait_time = int(max(max([wait_time_per_qubit[key_] for key_ in wait_time_per_qubit.keys()])))
                global_clock += max_wait_time
                if max_wait_time >= 1:
                    new_file.write("//** {}ns\n".format (float(global_clock * decimal.Decimal("{}".format(cycle_time)))))      
                break     
        
        num_group_1q = sum(sg_operate_cycle_gr.values()) / sl
        num_inst_per_total_2q = num_inst_per_total_2q / tl
        num_group_meas = sum(meas_operate_cycle.values()) / ml

        stat = {'num_z': int (num_z), '1q': int(num_qubit_1q), '1q_per_group': (num_group_1q), \
                '2q': int(num_qubit_2q), '2q overlap': num_inst_per_total_2q, 'measure': int(num_qubit_meas), 'reset': int (num_qubit_reset), 'measure_per_group': (num_group_meas),\
                'latency': float(global_clock * decimal.Decimal("{}".format(cycle_time)))}
        stat_df = pd.DataFrame.from_dict (stat, orient='index')
        stat_df.to_csv ("results/stats/{}/{}_{}.csv".format (architecture, workload, qubits))
    else:
        print("Our model does not support {} architecture\n".format(architecture))
        exit()

def rm_time_point(architecture, workload, qubits):
    if os.path.isfile ("workloads_final/{}_{}_{}".format (architecture, workload, qubits)):
        return
    data_list = list()
    with open ("workloads_final/{}/{}_{}".format (architecture, workload, qubits), "r") as f:
        data = f.read ()
        data_list = data.split ("\n")
    with open ("workloads_final/{}/{}_{}".format (architecture, workload, qubits), "w") as nf:
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
    with open ("workloads_final/{}/{}_{}".format (architecture, workload, qubits), "r") as f:
        data = f.read ()
        data_list = data.split ("\n")
    with open ("workloads_final/{}/{}_{}".format (architecture, workload, qubits), "w") as nf:
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

def timing_adjustment_threading (architecture, workload, qubit_range, sl, tl, ml, rl, qubit_per_group, channel_per_group, readout_group):
    for qubits in qubit_range:
        print ("Current file: {}_{}_{}".format (architecture, workload, qubits))
        timing_adjustment (architecture, workload, qubits, sl, tl, ml, rl, qubit_per_group, channel_per_group, readout_group)
        rm_time_point (architecture, workload, qubits)


def power_calculation (architecture, workload, qubits, sl, tl, ml, rl, qubit_per_group, channel_per_group, readout_group, node, vdd, vth):
    arch_file = architecture
    if architecture == "photonic_link":
        arch_file = "300k_cmos"

    stat_file = "results/stats/{}/{}_{}.csv".format(arch_file, workload, qubits)
    stat_df = pd.read_csv(stat_file, index_col=0)

    ratio_1q = stat_df.loc["1q"].item() * sl / stat_df.loc["latency"].item()
    ratio_2q = stat_df.loc["2q"].item() * tl / stat_df.loc["latency"].item()
    ratio_meas = stat_df.loc["measure"].item() * ml / stat_df.loc["latency"].item()
    ratio_reset = stat_df.loc["reset"].item() * rl / stat_df.loc["latency"].item()

    total_result = dict()
    wire_df = pd.read_csv ("wires.csv", index_col=0)

    list_ = list()

    # 300K CMOS
    if architecture == "300k_cmos":

        # Coaxial cable.
        num_wire_per_qubit = 4
        ## When applying the state-of-the-art FDM
        #num_wire_per_qubit = 1 + 1/32 + 1/4
        total_result["wire_static_4k"] = num_wire_per_qubit*qubits*wire_df.loc["coaxial_cable"]["static_4k"]
        total_result["wire_dynamic_4k"] = (ratio_1q + ratio_2q + ratio_meas + ratio_reset) * wire_df.loc["coaxial_cable"]["dynamic_4k"]
        total_result["power_4k"] = total_result["wire_static_4k"] + total_result["wire_dynamic_4k"]

        total_result["wire_static_1k"] = num_wire_per_qubit*qubits*wire_df.loc["coaxial_cable"]["static_1k"]
        total_result["wire_dynamic_1k"] = (ratio_1q + ratio_2q + ratio_meas + ratio_reset) * wire_df.loc["coaxial_cable"]["dynamic_1k"]
        total_result["power_1k"] = total_result["wire_static_1k"] + total_result["wire_dynamic_1k"]

        total_result["wire_static_100mk"] = num_wire_per_qubit*qubits*wire_df.loc["coaxial_cable"]["static_100mk"]
        total_result["wire_dynamic_100mk"] = (ratio_1q + ratio_2q + ratio_meas + ratio_reset) * wire_df.loc["coaxial_cable"]["dynamic_100mk"]
        total_result["power_100mk"] = total_result["wire_static_100mk"] + total_result["wire_dynamic_100mk"]

        total_result["wire_static_20mk"] = num_wire_per_qubit*qubits*wire_df.loc["coaxial_cable"]["static_20mk"]
        total_result["wire_dynamic_20mk"] = (ratio_1q + ratio_2q + ratio_meas + ratio_reset) * wire_df.loc["coaxial_cable"]["dynamic_20mk"]
        total_result["power_20mk"] = total_result["wire_static_20mk"] + total_result["wire_dynamic_20mk"]

        print ("================")
        print ("1. Coaxial cable.")
        print ("\n[Total power consumption; {} with {} qubits]".format (workload, qubits))
        print ("4K power:\t\t{0:.1f}\t[nW]".format (total_result["power_4k"]))
        print ("\tWire static:\t{0:.1f}\t[nW]".format (total_result["wire_static_4k"]))
        print ("\tWire dynamic:\t{0:.1f}\t[nW]".format (total_result["wire_dynamic_4k"]))
        print ("1K power:\t\t{0:.1f}\t[nW]".format (total_result["power_1k"]))
        print ("\tWire static:\t{0:.1f}\t[nW]".format (total_result["wire_static_1k"]))
        print ("\tWire dynamic:\t{0:.1f}\t\t[nW]".format (total_result["wire_dynamic_1k"]))
        print ("100mK power:\t\t{0:.1f}\t[nW]".format (total_result["power_100mk"]))
        print ("\tWire static:\t{0:.1f}\t[nW]".format (total_result["wire_static_100mk"]))
        print ("\tWire dynamic:\t{0:.1f}\t\t[nW]".format (total_result["wire_dynamic_100mk"]))
        print ("20mK power:\t\t{0:.1f}\t\t[nW]".format (total_result["power_20mk"]))
        print ("\tWire static:\t{0:.1f}\t\t[nW]".format (total_result["wire_static_20mk"]))
        print ("\tWire dynamic:\t{0:.1f}\t\t[nW]".format (total_result["wire_dynamic_20mk"]))
        
        total_result_df = pd.DataFrame.from_dict (total_result, orient="index")
        total_result_df.to_csv ("results/power_results/{}/{}_coaxial_{}.csv".format (architecture, workload, qubits))

        # Microstrip.
        num_wire_per_qubit = 1 + 1/32 + 1/8
        #num_wire_per_qubit = 4
        total_result["wire_static_4k"] = num_wire_per_qubit*qubits*wire_df.loc["microstrip"]["static_4k"]
        total_result["wire_dynamic_4k"] = (ratio_1q + ratio_2q + ratio_meas + ratio_reset) * wire_df.loc["microstrip"]["dynamic_4k"]
        total_result["power_4k"] = total_result["wire_static_4k"] + total_result["wire_dynamic_4k"]

        total_result["wire_static_1k"] = num_wire_per_qubit*qubits*wire_df.loc["microstrip"]["static_1k"]
        total_result["wire_dynamic_1k"] = (ratio_1q + ratio_2q + ratio_meas + ratio_reset) * wire_df.loc["microstrip"]["dynamic_1k"]
        total_result["power_1k"] = total_result["wire_static_1k"] + total_result["wire_dynamic_1k"]

        total_result["wire_static_100mk"] = num_wire_per_qubit*qubits*wire_df.loc["microstrip"]["static_100mk"]
        total_result["wire_dynamic_100mk"] = (ratio_1q + ratio_2q + ratio_meas + ratio_reset) * wire_df.loc["microstrip"]["dynamic_100mk"]
        total_result["power_100mk"] = total_result["wire_static_100mk"] + total_result["wire_dynamic_100mk"]

        total_result["wire_static_20mk"] = num_wire_per_qubit*qubits*wire_df.loc["microstrip"]["static_20mk"]
        total_result["wire_dynamic_20mk"] = (ratio_1q + ratio_2q + ratio_meas + ratio_reset) * wire_df.loc["microstrip"]["dynamic_20mk"]
        total_result["power_20mk"] = total_result["wire_static_20mk"] + total_result["wire_dynamic_20mk"]

        print ("\n\n2. Microstrip.")
        print ("\n[Total power consumption; {} with {} qubits]".format (workload, qubits))
        print ("4K power:\t\t{0:.1f}\t[nW]".format (total_result["power_4k"]))
        print ("\tWire static:\t{0:.1f}\t[nW]".format (total_result["wire_static_4k"]))
        print ("\tWire dynamic:\t{0:.1f}\t[nW]".format (total_result["wire_dynamic_4k"]))
        print ("1K power:\t\t{0:.1f}\t[nW]".format (total_result["power_1k"]))
        print ("\tWire static:\t{0:.1f}\t[nW]".format (total_result["wire_static_1k"]))
        print ("\tWire dynamic:\t{0:.1f}\t\t[nW]".format (total_result["wire_dynamic_1k"]))
        print ("100mK power:\t\t{0:.1f}\t[nW]".format (total_result["power_100mk"]))
        print ("\tWire static:\t{0:.1f}\t[nW]".format (total_result["wire_static_100mk"]))
        print ("\tWire dynamic:\t{0:.1f}\t\t[nW]".format (total_result["wire_dynamic_100mk"]))
        print ("20mK power:\t\t{0:.1f}\t\t[nW]".format (total_result["power_20mk"]))
        print ("\tWire static:\t{0:.1f}\t\t[nW]".format (total_result["wire_static_20mk"]))
        print ("\tWire dynamic:\t{0:.1f}\t\t[nW]".format (total_result["wire_dynamic_20mk"]))
        
        total_result_df = pd.DataFrame.from_dict (total_result, orient="index")
        total_result_df.to_csv ("results/power_results/{}/{}_microstrip_{}.csv".format (architecture, workload, qubits))

        # Photonic link.
        total_result["wire_static_4k"] = qubits*wire_df.loc["photonic_link"]["static_4k"]
        total_result["wire_dynamic_4k"] = 0
        total_result["power_4k"] = total_result["wire_static_4k"] + total_result["wire_dynamic_4k"]

        total_result["wire_static_1k"] = qubits*wire_df.loc["photonic_link"]["static_1k"]
        total_result["wire_dynamic_1k"] = 0
        total_result["power_1k"] = total_result["wire_static_1k"] + total_result["wire_dynamic_1k"]

        total_result["wire_static_100mk"] = qubits*wire_df.loc["photonic_link"]["static_100mk"]
        total_result["wire_dynamic_100mk"] = 0
        total_result["power_100mk"] = total_result["wire_static_100mk"] + total_result["wire_dynamic_100mk"]

        total_result["wire_static_20mk"] = 3*qubits*wire_df.loc["photonic_link"]["static_20mk"] + qubits*wire_df.loc["coaxial_cable"]["static_20mk"]
        total_result["wire_dynamic_20mk"] = (ratio_1q + ratio_2q + ratio_meas + ratio_reset) * wire_df.loc["photonic_link"]["dynamic_20mk"]
        total_result["power_20mk"] = total_result["wire_static_20mk"] + total_result["wire_dynamic_20mk"]

        print ("\n\n3. Photonic link.")
        print ("\n[Total power consumption; {} with {} qubits]".format (workload, qubits))
        print ("4K power:\t\t{0:.1f}\t[nW]".format (total_result["power_4k"]))
        print ("\tWire static:\t{0:.1f}\t[nW]".format (total_result["wire_static_4k"]))
        print ("\tWire dynamic:\t{0:.1f}\t[nW]".format (total_result["wire_dynamic_4k"]))
        print ("1K power:\t\t{0:.1f}\t[nW]".format (total_result["power_1k"]))
        print ("\tWire static:\t{0:.1f}\t[nW]".format (total_result["wire_static_1k"]))
        print ("\tWire dynamic:\t{0:.1f}\t\t[nW]".format (total_result["wire_dynamic_1k"]))
        print ("100mK power:\t\t{0:.1f}\t[nW]".format (total_result["power_100mk"]))
        print ("\tWire static:\t{0:.1f}\t[nW]".format (total_result["wire_static_100mk"]))
        print ("\tWire dynamic:\t{0:.1f}\t\t[nW]".format (total_result["wire_dynamic_100mk"]))
        print ("20mK power:\t\t{0:.1f}\t\t[nW]".format (total_result["power_20mk"]))
        print ("\tWire static:\t{0:.1f}\t\t[nW]".format (total_result["wire_static_20mk"]))
        print ("\tWire dynamic:\t{0:.1f}\t\t[nW]".format (total_result["wire_dynamic_20mk"]))
        print ("================\n")
        
        total_result_df = pd.DataFrame.from_dict (total_result, orient="index")
        total_result_df.to_csv ("results/power_results/{}/{}_photonic_{}.csv".format (architecture, workload, qubits))


    # Intel horseridge 1
    elif architecture == "horseridge":

        cmos_file = "../../device_model/cmos/cmos_results/4k_{}nm_{}v_{}v.json".format (node, vdd, vth)
        if not os.path.isfile (cmos_file):
            current_dir_ = os.getcwd ()
            os.chdir ("../../device_model/cmos/")
            os.system ("python cmos_device_model.py --node {} --vdd {} --vth {}".format (node, vdd, vth))
            os.chdir (current_dir_)
        cmos_powers = None
        with open (cmos_file, "r") as f:
            cmos_powers = json.load (f)
        drive = cmos_powers["drive_circuit"]
        pulse = cmos_powers["pulse_circuit"]
        tx = cmos_powers["readout_tx_circuit"]
        rx = cmos_powers["readout_rx_circuit"]

        # Static power (aggregated).
        ## We assume the qubits without frequency drift; zero DC-bias.
        device_static = (drive["z_correction_module"]["static"] + qubit_per_group*drive["nco"]["static"] + channel_per_group*drive["other_inside_bank"]["static"] \
            + drive["other_outside_bank"]["static"] + drive["analog"]["static"] + drive["inst_table"]["static"] \
            + drive["gate_table"]["static"] + drive["wave_table"]["static"] \
            + qubit_per_group*(pulse["several"]["static"] + pulse["once"]["static"] + pulse["analog"]["static"] + pulse["inst_table"]["static"] + pulse["amp_table"]["static"]) \
            + qubit_per_group*(tx["inst_table"]["static"] + tx["lut"]["static"]) + qubit_per_group/readout_group*tx["analog"]["static"] \
            + qubit_per_group*rx["digital_per_qubit"]["static"] + qubit_per_group/readout_group*(rx["other_digital"]["static"]+ rx["inst_table"]["static"]+ rx["analog"]["static"]))*1e9
        
        # Dynamic energy per access.
        ## Drive circuit.
        drive_inst_table = drive["inst_table"]["dynamic"]*1e9
        drive_gate_table = drive["gate_table"]["dynamic"]*1e9
        drive_wave_table = drive["wave_table"]["dynamic"]*1e9
        drive_z_correction_module = drive["z_correction_module"]["dynamic"]*1e9
        drive_nco = drive["nco"]["dynamic"]*1e9
        drive_other_digital_inside_bank = drive["other_inside_bank"]["dynamic"]*1e9
        drive_other_digital_outside_bank = drive["other_outside_bank"]["dynamic"]*1e9
        drive_analog = drive["analog"]["dynamic"]*1e9

        ## Pulse circuit.
        pulse_inst_table = pulse["inst_table"]["dynamic"]*1e9
        pulse_amp_table = pulse["amp_table"]["dynamic"]*1e9
        pulse_once = pulse["once"]["dynamic"]*1e9
        pulse_several = pulse["several"]["dynamic"]*1e9
        pulse_analog = pulse["analog"]["dynamic"]*1e9

        ## Readout TX circuit.
        tx_inst_table = tx["inst_table"]["dynamic"]*1e9
        tx_signal_gen = tx["signal_gen"]["dynamic"]*1e9
        tx_sin_table = tx["lut"]["dynamic"]*1e9
        tx_analog = tx["analog"]["dynamic"]*1e9

        ## Readout RX circuit.
        rx_inst_table = rx["inst_table"]["dynamic"]*1e9
        rx_digital_per_qubit = rx["digital_per_qubit"]["dynamic"]*1e9
        rx_other_digital = rx["other_digital"]["dynamic"]*1e9
        rx_analog = rx["analog"]["dynamic"]*1e9
        frequency = 2.5e9

        device_power = dict ()
        device_power["drive"] = float (((drive_inst_table + drive_z_correction_module + drive_nco) * 4 * stat_df.loc["num_z"] \
                                + (drive_inst_table + drive_gate_table + drive_z_correction_module) * 2 * stat_df.loc["1q"] \
                                + (drive_nco + drive_wave_table + drive_other_digital_inside_bank) * sl*1e-9*frequency * stat_df.loc["1q"] \
                                + (drive_analog + drive_other_digital_outside_bank) * sl*1e-9*frequency * stat_df.loc["1q_per_group"]) \
                                * 1e9/stat_df.loc["latency"])
        device_power["pulse"] = float (((pulse_inst_table + pulse_amp_table + pulse_several)*10 + pulse_analog*tl + pulse_once)*1e-9*frequency*(stat_df.loc["2q"]+stat_df.loc["reset"])*2\
                                * 1e9/stat_df.loc["latency"])
        device_power["read_tx"] = float ((tx_inst_table * 1 * stat_df.loc["measure"] \
                                + (tx_signal_gen + tx_sin_table) * ml*1e-9*frequency * stat_df.loc["measure"] \
                                + (tx_analog) * ml*1e-9*frequency * stat_df.loc["measure_per_group"]/readout_group) \
                                * 1e9/stat_df.loc["latency"])
        device_power["read_rx"] = float ((rx_inst_table * 1 * stat_df.loc["measure"] \
                                + rx_digital_per_qubit * ml*1e-9*frequency * stat_df.loc["measure"] \
                                + (rx_analog + rx_other_digital) * ml*1e-9*frequency * stat_df.loc["measure_per_group"]/readout_group) \
                                * 1e9/stat_df.loc["latency"])
        device_power["static"] = device_static * ceil (qubits/qubit_per_group)

        device_power_df = pd.DataFrame.from_dict (device_power, orient="index")
        device_power_df.to_csv ("results/power_results/horseridge/device/{}_{}.csv".format (workload, qubits))

        device_dynamic = device_power["drive"] + device_power["pulse"] + device_power["read_tx"] + device_power["read_rx"]
        total_device_power = device_dynamic + device_static
        num_coax = 1 + ceil (qubits/qubit_per_group*5.5) # 1 global clock + 5.5 cable per Horseridge (to support 55Gbps of worst-case BW in baseline).
        num_microstrip = ceil (qubits/qubit_per_group)*3 + qubits # 1 driveline and 2 readline per group + 1 pulseline per qubit.

        total_result["wire_static_4k"] = num_coax * wire_df.loc["microstrip"]["static_4k"]
        total_result["wire_dynamic_4k"] = num_coax * wire_df.loc["microstrip"]["dynamic_4k"]
        total_result["device_4k"] = total_device_power
        total_result["power_4k"] = total_result["wire_static_4k"] + total_result["wire_dynamic_4k"] + total_device_power

        total_result["wire_static_20mk"] = num_microstrip * wire_df.loc["superconducting_microstrip"]["static_20mk"]
        # We exclude the active load of 2Q gates because they use the DC pulses with superconductor.
        total_result["wire_dynamic_20mk"] = (ratio_1q + ratio_meas) * wire_df.loc["superconducting_microstrip"]["dynamic_20mk"]
        total_result["power_20mk"] = total_result["wire_static_20mk"] + total_result["wire_dynamic_20mk"]

        
        print ("\n================")
        print ("[Intel Horseridge Summary; {} with {} qubits]".format (workload, qubits))
        print ("Frequency:\t\t{}\t\t[GHz]".format (frequency/1e9))
        print ("Total power:\t\t{0:.1f}\t[nW]".format (total_device_power))
        print ("\tStatic power:\t{0:.1f}\t[nW]".format (device_static))
        print ("\tDynamic power:\t{0:.1f}\t[nW]".format (device_dynamic))
        print ("\t\tDrive power:\t{0:.1f}\t[nW]".format (device_power["drive"]))
        print ("\t\tPulse power:\t{0:.1f}\t[nW]".format (device_power["pulse"]))
        print ("\t\tReadTX power:\t{0:.1f}\t[nW]".format (device_power["read_tx"]))
        print ("\t\tReadRX power:\t{0:.1f}\t[nW]".format (device_power["read_rx"]))

        print ("\n[Total power consumption; {} with {} qubits]".format (workload, qubits))
        print ("4K power:\t\t{0:.1f}\t[nW]".format (total_result["power_4k"]))
        print ("\tWire static:\t{0:.1f}\t[nW]".format (total_result["wire_static_4k"]))
        print ("\tWire dynamic:\t{0:.1f}\t[nW]".format (total_result["wire_dynamic_4k"]))
        print ("\t4K device:\t{0:.1f}\t[nW]".format (total_device_power))
        print ("20mK power:\t\t{0:.1f}\t\t[nW]".format (total_result["power_20mk"]))
        print ("\tWire static:\t{0:.1f}\t\t[nW]".format (total_result["wire_static_20mk"]))
        print ("\tWire dynamic:\t{0:.1f}\t\t[nW]".format (total_result["wire_dynamic_20mk"]))
        print ("================\n")
    
        total_result_df = pd.DataFrame.from_dict (total_result, orient="index")
        total_result_df.to_csv ("results/power_results/horseridge/total/{}_{}.csv".format (workload, qubits))


def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--simulation_mode", "-sm", help="Simulation mode (i.e., NISQ, FTQC)", type=str, default="FTQC")
    parser.add_argument ("--single", "-s", help="1Q-gate time [ns]", type=int, default=25)
    parser.add_argument ("--two", "-t", help="2Q-gate time [ns]", type=int, default=50)
    parser.add_argument ("--measure", "-m", help="Measurement time [ns]", type=int, default=550)
    parser.add_argument ("--qubit_per_group", "-q", help="#Qubits in 4K CMOS", type=int, default=32)
    parser.add_argument ("--channel_per_group", "-c", help="#Banks in 4K CMOS", type=int, default=2)
    parser.add_argument ("--readout_group", "-r", help="#Qubits sharing same analog", type=int, default=8)
    parser.add_argument ("--node", "-n", help="Technology node [nm] (i.e., 45, 22, 14, 7)", type=int, default=14)
    parser.add_argument ("--vdd", "-d", help="Operating voltage at 300K (i.e., Vdd_300k)", type=float, default=1.0)
    parser.add_argument ("--vth", "-v", help="Threshold voltage at 300K (i.e., Vth_300k)", type=float, default=0.46893)
    args = parser.parse_args ()
    return args


if __name__ == "__main__":
    
    args = arg_parse ()
    architectures = ["300k_cmos", "horseridge"]
    sim_mode = args.simulation_mode
    if sim_mode == "FTQC":
        workloads = ["esm"]
        qubit_lists = [2*(n_+1)**2 for n_ in range (3,25,2)]
    elif sim_mode == "NISQ":
        workloads = ['ghz', 'bitcode', 'hamiltonian', 'merminbell', \
                    'phase', 'qaoa_fermionic', 'qaoa_vanilla', 'vqe']
        qubit_lists = [2**n_ for n_ in range (1, 11)]

    t_1q = args.single
    t_2q = args.two
    t_m = args.measure
    qubit_per_group = args.qubit_per_group
    channel_per_group = args.channel_per_group
    readout_group = args.readout_group
    node = args.node
    vdd = args.vdd
    vth = args.vth
    
    # Parse the workloads to CMOS controller executable.
    print ("Parsing the workloads with the CMOS controller executable gate set...")
    parse_workloads ()
    print ("Complete!\n")
    
    # Timing simulation.
    print ("Timing simulation to calculate the execution time...")
    ps = list ()
    for workload in workloads:
        for architecture in architectures:
            p = None
            p = multiprocessing.Process (target=timing_adjustment_threading, \
                    args=(architecture, workload, qubit_lists, t_1q, t_2q, t_m, t_m, qubit_per_group, channel_per_group, readout_group))
            p.start ()
            ps.append (p)

    for p_ in ps:
        p_.join ()
    
    # Report power consumption.
    print ("Calculate runtime-power consumption of QC interfaces for each workload...")
    for workload in workloads:
        for architecture in architectures:
            for qubits in qubit_lists:
                power_calculation (architecture, workload, qubits, t_1q, t_2q, t_m, t_m, qubit_per_group, channel_per_group, readout_group, node, vdd, vth)

    print ("Complete!")
    print ("You can find all of the simulation results in ./results file.\n")


