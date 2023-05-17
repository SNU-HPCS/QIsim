from absl import flags
from absl import app
import os
import shutil

FLAGS = flags.FLAGS
flags.DEFINE_string("top_unit", "drive_circuit", "top unit's name (for finding directory)")
flags.DEFINE_string("target_unit", "drive_signal_gen_unit", "target unit name")
# TODO: remove mem_list argument
flags.DEFINE_string("mem_list", "mem_list_drive_circuit.txt", "List of *.mem filenames")
flags.DEFINE_string("option", "visualize", "compile/run/visualize")

'''
Example
python run_rtl_sim.py --top_unit drive_circuit --target_unit drive_signal_gen_unit
python run_rtl_sim.py --top_unit drive_circuit --target_unit drive_circuit
'''

def copy_mems_to_temp (mem_dir, mem_list, temp_dir):
    filename = mem_dir + "mem_list/" + mem_list
    print("filename: {}".format(filename))
    with open(filename) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        
    print("lines:")
    print(lines)
    
    for line in lines:
        src_file = mem_dir + line
        dest_file = temp_dir + line
        print("src_file: {}".format(src_file))
        print("dest_file: {}".format(dest_file))
        
        shutil.copy(src_file, dest_file)
    
    return

def copy_tb_to_temp (tb_dir, target_unit, temp_dir):
    src_file = tb_dir + "{}_tb.v".format(target_unit)
    dest_file = temp_dir + "{}_tb.v".format(target_unit)
    print("src_file: {}".format(src_file))
    print("dest_file: {}".format(dest_file))
    
    shutil.copy(src_file, dest_file)
    
    try:
        src_file = tb_dir + "{}.gtkw".format(target_unit)
        dest_file = temp_dir + "{}.gtkw".format(target_unit)
        print("src_file: {}".format(src_file))
        print("dest_file: {}".format(dest_file))
        
        shutil.copy(src_file, dest_file)
    except:
        pass
    
    return

def copy_def_to_temp (src_dir, top_unit, temp_dir):
    src_file = src_dir + "define.v".format(top_unit)
    dest_file = temp_dir + "define.v".format(top_unit)
    print("src_file: {}".format(src_file))
    print("dest_file: {}".format(dest_file))
    
    shutil.copy(src_file, dest_file)

    src_file = src_dir + "define_{}.v".format(top_unit)
    dest_file = temp_dir + "define_{}.v".format(top_unit)
    print("src_file: {}".format(src_file))
    print("dest_file: {}".format(dest_file))
    
    shutil.copy(src_file, dest_file)
    
    return

def main(argv):
    top_unit = FLAGS.top_unit
    target_unit = FLAGS.target_unit
    mem_list = FLAGS.mem_list
    option = FLAGS.option
    
    ''' Store paths for libraries and files '''
    src_vlg_str = "src_vlg_inmem"
    # src_vlg_str = "src_vlg"
    
    lib_dir_list = []
    # lib_dir = os.getcwd() + "/src_vlg/".format(top_unit)
    lib_dir_list.append(os.getcwd() + "/{}/submodules/".format(src_vlg_str))
    lib_dir_list.append(os.getcwd() + "/{}/{}/".format(src_vlg_str, top_unit))
    lib_dir_list.append(os.getcwd() + "/{}/".format(src_vlg_str))
    print("lib_dir: ", lib_dir_list)
    
    if top_unit == target_unit:
        tb_dir = os.getcwd() + "/tb_vlg/".format(top_unit)
    else:
        tb_dir = os.getcwd() + "/tb_vlg/{}/".format(top_unit)

    src_dir = os.getcwd() + "/{}/".format(src_vlg_str)
    mem_dir = os.getcwd() + "/mem_files/"
    temp_dir = os.getcwd() + "/temp/"
    
    # ''' Read define.v file '''
    
    
    ''' Make a temporary folder and load files '''
    if (os.path.isdir(temp_dir)):
        pass
    else:
        os.mkdir(temp_dir)
        
    copy_mems_to_temp(mem_dir, mem_list, temp_dir)
    copy_tb_to_temp(tb_dir, target_unit, temp_dir)
    copy_def_to_temp(src_dir, top_unit, temp_dir)

    os.chdir(temp_dir)
    
    # """
    # print("tb_dir: ", tb_dir)
    
    ''' Compile, elaborate, and run the rtl simulation '''
    if option in ["compile", "run", "visualize"]:
        print("Start compilation...")
        cmd = "iverilog -Wall -Wno-timescale -o {}.out".format(target_unit)
        for lib_dir in lib_dir_list:
            cmd = cmd + " -y {}".format(lib_dir)
            
        cmd = cmd + " {}_tb.v".format(target_unit)
        print("cmd: ", cmd)
        os.system(cmd)
        print("Compilation end...")
        
    if option in ["run", "visualize"]:
        print("Start simulation...")
        cmd = "vvp {}.out".format(target_unit)
        print("cmd: ", cmd)
        os.system(cmd)
        print("Simulation end...")
        
    if option in ["visualize"]:
        print("Start visualization...")
        cmd = "gtkwave {}.vcd {}.gtkw".format(target_unit, target_unit)
        print("cmd: ", cmd)
        os.system(cmd)
        print("Visualization end...")
        
        
    ''' Clear temporary files '''
    # TODO: move a waveform save file to tb_vlg
    
    # TODO: remove the temporary folder
    
    # """
    print("run_rtl_sim finished")
    return

if __name__ == "__main__":
    app.run(main)
