from absl import flags
from absl import app
import os

import numpy as np
from pprint import pprint as pp
import copy

from qiskit import *

import ray

FLAGS = flags.FLAGS
# flags.DEFINE_string("distance", "3", "Target distance of a logical qubit (default == 3)")
flags.DEFINE_string("esm_rounds", "10", "Number of ESM iterations (default == 1)")

def trace_esm(distance, esm_rounds = 10, patch_size = (1,1)):
    trace = []
    # Initialize
    height, width = patch_size
    '''
    esm_setup = np.array( \
    [[['i', 'i', 'i', 'i']] + [['i', 'i', 'z', 'z'],['i', 'i', 'i', 'i']] * (((distance +1)//2)*width-1) + [['i', 'i', 'i', 'i']]] + \
    [[['i', 'i', 'i', 'i']] + [['x', 'x', 'x', 'x'],['z', 'z', 'z', 'z']] * (((distance +1)//2)*width-1) + [['x', 'i', 'x', 'i']], \
     [['i', 'x', 'i', 'x']] + [['z', 'z', 'z', 'z'],['x', 'x', 'x', 'x']] * (((distance +1)//2)*width-1) + [['i', 'i', 'i', 'i']]] * (((distance +1)//2)*height-1) + \
    [[['i', 'i', 'i', 'i']] + [['i', 'i', 'i', 'i'],['z', 'z', 'i', 'i']] * (((distance +1)//2)*width-1) + [['i', 'i', 'i', 'i']]])
    '''
    esm_setup = np.array( \
    [[['i', 'i', 'i', 'i']] + [['i', 'i', 'i', 'i'],['i', 'i', 'x', 'x']] * (((distance +1)//2)*width-1) + [['i', 'i', 'i', 'i']]] + \
    [[['i', 'z', 'i', 'z']] + [['x', 'x', 'x', 'x'],['z', 'z', 'z', 'z']] * (((distance +1)//2)*width-1) + [['i', 'i', 'i', 'i']], \
     [['i', 'i', 'i', 'i']] + [['z', 'z', 'z', 'z'],['x', 'x', 'x', 'x']] * (((distance +1)//2)*width-1) + [['z', 'i', 'z', 'i']]] * (((distance +1)//2)*height-1) + \
    [[['i', 'i', 'i', 'i']] + [['x', 'x', 'i', 'i'],['i', 'i', 'i', 'i']] * (((distance +1)//2)*width-1) + [['i', 'i', 'i', 'i']]])
    
    # print("esm_setup")
    # pp(esm_setup)
    
    esm_len = 7 # depth
    for r in range(esm_rounds):
        seq = []
        # for i in range(distance+1):
        for i in range(patch_size[0] * (distance+1)):
            seq_col = []
            # for j in range(distance+1):
            for j in range(patch_size[1] * (distance+1)):
                if 'z' in esm_setup[i][j]:
                    z_seq = [esm_setup[i][j][1], esm_setup[i][j][3], esm_setup[i][j][0], esm_setup[i][j][2]]
                    seq_col.append(['h'] + ['cz' if op != 'i' else 'i' for op in z_seq] + ['h','meas'])
                elif 'x' in esm_setup[i][j]:
                    x_seq = [esm_setup[i][j][1], esm_setup[i][j][0], esm_setup[i][j][3], esm_setup[i][j][2]]
                    seq_col.append(['h'] + ['cnot' if op != 'i' else 'i' for op in x_seq] + ['h','meas'])
                else:
                    seq_col.append(['i'] * esm_len)
            seq.append(seq_col)

        for ts in range(esm_len):
            trace_per_timestep = []
            # Generate ESM with CNOT and CZ
            for p_idx in np.ndindex(patch_size):
                for i in range(patch_size[0] * (distance+1)):
                    for j in range(patch_size[1] * (distance+1)):
                        # aq index
                        aq_idx = (p_idx[0] * (distance + 1) + i,p_idx[1] * (distance + 1) + j)
                        # patch_idx, ucl_idx, qb_idx = decompose_idx((p_idx[0] * (distance + 1) + i,p_idx[1] * (distance + 1) + j), distance)
                        if seq[i][j][ts] == 'cz': # Z-stabilizer
                            # dq index
                            if ts == 1:
                                dq_idx = (aq_idx[0] +0, aq_idx[1] +1)
                            elif ts == 2:
                                dq_idx = (aq_idx[0] +1, aq_idx[1] +1)
                            elif ts == 3:
                                dq_idx = (aq_idx[0] +0, aq_idx[1] +0)
                            elif ts == 4:
                                dq_idx = (aq_idx[0] +1, aq_idx[1] +0)
                            else:
                                raise Exception()
                            trace_per_timestep.append({'type':seq[i][j][ts], 'aq':aq_idx, 'dq':dq_idx})
                            # dq_patch_idx, dq_ucl_idx, dq_qb_idx = decompose_idx(dq_idx, distance)
                            # trace_per_timestep.append(op(seq[i][j][ts],patch_idx,ucl_idx,'aq',qb_idx, dq_patch_idx,dq_ucl_idx,'dq',dq_qb_idx))
                        elif seq[i][j][ts] == 'cnot': # X-stabilizer
                            if ts == 1:
                                dq_idx = (aq_idx[0] +0, aq_idx[1] +1)
                            elif ts == 2:
                                dq_idx = (aq_idx[0] +0, aq_idx[1] +0)
                            elif ts == 3:
                                dq_idx = (aq_idx[0] +1, aq_idx[1] +1)
                            elif ts == 4:
                                dq_idx = (aq_idx[0] +1, aq_idx[1] +0)
                            else:
                                raise Exception()
                            trace_per_timestep.append({'type':seq[i][j][ts], 'aq':aq_idx, 'dq':dq_idx})
                            # dq_patch_idx, dq_ucl_idx, dq_qb_idx = decompose_idx(dq_idx, distance)
                            # trace_per_timestep.append(op(seq[i][j][ts],patch_idx,ucl_idx,'aq',qb_idx, dq_patch_idx,dq_ucl_idx,'dq',dq_qb_idx))
                        else: # i, h, meas
                            trace_per_timestep.append({'type':seq[i][j][ts], 'aq':aq_idx, 'dq':None})
                            # trace_per_timestep.append(op(seq[i][j][ts],patch_idx,ucl_idx,'aq',qb_idx))
            
            # Convert CNOT into CZ
            cnot_indices = [i for (i,x) in enumerate(trace_per_timestep) if (x['type'] == 'cnot')]
            if cnot_indices:
                trace_prev = copy.deepcopy(trace_per_timestep)
                trace_next = copy.deepcopy(trace_per_timestep)
                for (idx, _) in enumerate(trace_per_timestep):
                    if idx in cnot_indices:
                        trace_prev[idx]['type'] = 'h'
                        trace_prev[idx]['aq'] = None
                        
                        trace_per_timestep[idx]['type'] = 'cz'
                        
                        trace_next[idx]['type'] = 'h'
                        trace_next[idx]['aq'] = None
                    else:
                        trace_prev[idx]['type'] = 'i'
                        trace_prev[idx]['aq'] = None
                        trace_next[idx]['type'] = 'i'
                        trace_next[idx]['aq'] = None
                
                trace.append(trace_prev)
                trace.append(trace_per_timestep)
                trace.append(trace_next)
            else:      
                trace.append(trace_per_timestep)
        # 
    
    return trace

def convert_trace_to_circuit (trace, distance):
    num_dq = (distance +1) ** 2
    num_aq = (distance +1) ** 2
    dq = QuantumRegister(num_dq, name='data')
    aq = QuantumRegister(num_aq, name='ancilla')
    mz = ClassicalRegister(num_aq, name='mz')
    
    qc = QuantumCircuit(dq, aq, mz)
    
    for i, trace_per_timestep in enumerate(trace):
        # qc.barrier()
        if any([inst['type'] == 'meas' for inst in trace_per_timestep]):
            qc.barrier()
        
        for inst in trace_per_timestep:
            if inst['type'] == 'h':
                if inst['dq'] is None:
                    idx = inst['aq'][0] * (distance +1) + inst['aq'][1]
                    qc.h(aq[idx])
                else:
                    idx = inst['dq'][0] * (distance +1) + inst['dq'][1]
                    qc.h(dq[idx])
            elif inst['type'] == 'cz':
                aq_idx = inst['aq'][0] * (distance +1) + inst['aq'][1]
                dq_idx = inst['dq'][0] * (distance +1) + inst['dq'][1]
                qc.cz(aq[aq_idx], dq[dq_idx])
            elif inst['type'] == 'i':
                pass
                '''
                if inst['dq'] is None:
                    idx = inst['aq'][0] * (distance +1) + inst['aq'][1]
                    qc.i(dq[idx])
                else:
                    idx = inst['dq'][0] * (distance +1) + inst['dq'][1]
                    qc.i(aq[idx])
                '''
            elif inst['type'] == 'meas':
                aq_idx = inst['aq'][0] * (distance +1) + inst['aq'][1]
                qc.measure(aq[aq_idx], mz[aq_idx])
            else:
                raise Exception("Undefined instruction: {}".format(inst))
        
        if (i < len(trace)-1) and any([inst['type'] == 'meas' for inst in trace_per_timestep]):
            qc.barrier()
        # qc.barrier()
    
    return qc

def convert_circuit_to_qasm (qc, filename = "result.qasm"):
    qc.qasm(formatted=False, filename=filename, encoding=None)
    return

'''
# Multiprocessing does not work for qiskit transpilers
@ray.remote
def esm_generation_ray (distance, esm_rounds):
    print("Generate {}x ESM with distance {}".format(esm_rounds, distance))
    
    trace = trace_esm(distance, esm_rounds)
    qc = convert_trace_to_circuit(trace, distance)
    # return qc
    
    backend = Aer.get_backend('aer_simulator')
    qc_opt = transpile(qc, backend, optimization_level=1) # remove repeated hadamard gates
    return qc_opt

def simulation_ray (distance_list, esm_rounds):
    if not ray.is_initialized():
        ray.init()
    
    sims = [esm_generation_ray.remote (distance, esm_rounds) for distance in distance_list]
    qc_opt_list = ray.get(sims)
    
    filename_list = [os.getcwd() + "/workloads/esm_{}".format(2* ((distance +1) ** 2)) for distance in distance_list]
    
    for qc_opt, filename in zip(qc_opt_list, filename_list):
        convert_circuit_to_qasm(qc_opt, filename)
    
    return
'''

def main(argv):
    '''
    distance = int(FLAGS.distance)
    esm_rounds = int(FLAGS.esm_rounds)
    trace = trace_esm(distance, esm_rounds)
    qc = convert_trace_to_circuit(trace, distance)
    backend = Aer.get_backend('aer_simulator')
    qc_opt = transpile(qc, backend, optimization_level=1) # remove repeated hadamard gates
    
    num_qb = 2* ((distance +1) ** 2)
    #filename = os.getcwd() + "/esm_workloads/esm_d{}_q{}.qasm".format(distance, num_qb)
    # filename = os.getcwd() + "/esm_workloads/esm_{}".format(num_qb)
    filename = os.getcwd() + "/workloads/esm_{}".format(num_qb)
    convert_circuit_to_qasm(qc_opt, filename)
    '''

    esm_rounds = int(FLAGS.esm_rounds)
    distance_list = [3,5,7,9,11,13,15,17,19,21,23]

    for distance in distance_list:
        print("Generate {}x ESM with distance {}".format(esm_rounds, distance))
        
        trace = trace_esm(distance, esm_rounds)
        qc = convert_trace_to_circuit(trace, distance)
        backend = Aer.get_backend('aer_simulator')
        qc_opt = transpile(qc, backend, optimization_level=1) # remove repeated hadamard gates
        
        num_qb = 2* ((distance +1) ** 2)
        #filename = os.getcwd() + "/esm_workloads/esm_d{}_q{}.qasm".format(distance, num_qb)
        # filename = os.getcwd() + "/esm_workloads/esm_{}".format(num_qb)
        filename = os.getcwd() + "./workloads/esm_{}".format(num_qb)
        convert_circuit_to_qasm(qc_opt, filename)

    print ("Complete!")
    print ("You can find all of the esm workloads in ./workloads folder.\n")

    return

if __name__ == "__main__":
    app.run(main)
