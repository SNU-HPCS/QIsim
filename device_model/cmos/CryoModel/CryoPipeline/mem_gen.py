from absl import flags
from absl import app
import os

import numpy as np


FLAGS = flags.FLAGS
flags.DEFINE_string("num_points", "1024", "Number of points to generate")
flags.DEFINE_string("bitwidth", "16", "Bitwidth of a point")
flags.DEFINE_string("wave_type", "sin", "Wave type: (signed_)sin, (signed_)cos, gaussian, const, linear, zero")
flags.DEFINE_string("target_path", "/src_vlg/drive_circuit", "Location to generate file")

def get_sin_point (max_amplitude, num_points, i):
    point = (max_amplitude/2) * (np.sin((2*np.pi)*(i/num_points)) + 1)
    return int(np.round(point))

def get_cos_point (max_amplitude, num_points, i):
    point = (max_amplitude/2) * (np.cos((2*np.pi)*(i/num_points)) + 1)
    return int(np.round(point))

def get_signed_sin_point (max_amplitude, num_points, i):
    point = (max_amplitude/2-1) * (np.sin((2*np.pi)*(i/num_points)))
    return int(np.round(point))

def get_signed_cos_point (max_amplitude, num_points, i):
    point = (max_amplitude/2-1) * (np.cos((2*np.pi)*(i/num_points)))
    return int(np.round(point))

def get_gaussian_point (max_amplitude, num_points, i):
    sigma = (0.5/3)
    mean = 0
    x = ((i + 0.5) / num_points) - 0.5
    
    # point = (1 / np.sqrt(2*np.pi*(sigma**2))) * np.exp(-((i-mean)**2) / (2*(sigma**2)))
    point = max_amplitude * np.exp(-((x-mean)**2) / (2*(sigma**2)))
    
    return int(np.round(point))

def get_const_point (max_amplitude, num_points, i):
    return max_amplitude

def get_linear_point (max_amplitude, num_points, i):
    point = max_amplitude * (i / num_points)
    return int(np.round(point))

def get_zero_point (max_amplitude, num_points, i):
    return 0

def get_points(num_points, bitwidth, wave_type):
    max_amplitude = (2 ** bitwidth) -1

    if wave_type == 'sin':     
        result = [get_sin_point(max_amplitude, num_points, i) for i in range(num_points)]
    elif wave_type == 'cos':
        result = [get_cos_point(max_amplitude, num_points, i) for i in range(num_points)]
    elif wave_type == 'signed_sin':
        result = [get_signed_sin_point(max_amplitude, num_points, i) for i in range(num_points)]
    elif wave_type == 'signed_cos':
        result = [get_signed_cos_point(max_amplitude, num_points, i) for i in range(num_points)]
    elif wave_type == 'gaussian':
        result = [get_gaussian_point(max_amplitude, num_points, i) for i in range(num_points)]
    elif wave_type == 'const':
        result = [get_const_point(max_amplitude, num_points, i) for i in range(num_points)]
    elif wave_type == 'linear':
        result = [get_linear_point(max_amplitude, num_points, i) for i in range(num_points)]
    elif wave_type == 'zero':
        result = [get_zero_point(max_amplitude, num_points, i) for i in range(num_points)]
    # elif wave_type == 'inst_table':
    #     # TODO: parameterize this
    #     INST_TABLE_NUM_ENTRY = 8
    #     INST_TABLE_DATA_WIDTH = 34
    #     NUM_QUBITS = 16
    #     inst_table = [["0"*INST_TABLE_DATA_WIDTH for _ in range(NUM_QUBITS)] for _ in range(INST_TABLE_NUM_ENTRY)]
    #     inst_table[0][14] = '{0:016b}'.format(0) + '{0:016b}'.format(1023) + '00'
    #     inst_table[2][3] = '{0:016b}'.format(2048) + '{0:016b}'.format(4095) + '00'

    #     # print(inst_table)
    #     result = []
    #     for inst_line_list in inst_table:
    #         inst_line = ""
    #         for inst in reversed(inst_line_list):
    #             inst_line = inst_line + inst
    #         result.append(int(inst_line,2))
    #         # print("inst_line: ", inst_line)
    #         # print("len(inst_line): ", len(inst_line))
    #         # print("inst_line_hex: ", inst_line_hex)
    #         # print("len(inst_line_hex): ", len(inst_line_hex))
    else:
        raise Exception("Undefined wave_type: {}".format(wave_type))
        
    # print(result)
    return result

def main(argv):
    num_points = FLAGS.num_points
    bitwidth = FLAGS.bitwidth
    wave_type = FLAGS.wave_type
    target_path= FLAGS.target_path
    
    num_points = int(num_points)
    bitwidth = int(bitwidth)
    bitwidth_hex = (bitwidth // 4) + (1 if bitwidth % 4 > 0 else 0)
    pad = '0' + str(bitwidth_hex) + 'x'
    
    result = get_points(num_points, bitwidth, wave_type)
    
    # Change directory to the target
    os.chdir((os.getcwd() + target_path))

    # Write result to file
    file_name = wave_type + '_n' + str(num_points) + '_' + str(bitwidth) + 'b.mem'
    with open(file_name, 'w') as f:
        for r in result:
            f.write(format(r & (2 ** bitwidth -1), pad)+'\n')
    return

if __name__ == "__main__":
    app.run(main)
