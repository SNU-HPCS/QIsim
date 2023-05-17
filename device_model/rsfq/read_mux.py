from absl import flags
from absl import app
import os

FLAGS = flags.FLAGS
flags.DEFINE_integer ("i", 8, "Number of inputs")
flags.DEFINE_integer ("s", 3, "Number of select bits")
flags.DEFINE_integer ("o", 1, "Width of output")

num_inputs = None
num_selects = None
num_outputs = None

def init_setup ():
    global num_inputs, num_selects, num_outputs
    num_inputs = FLAGS.i
    num_selects = FLAGS.s
    num_outputs = FLAGS.o
    return


def gen_yoscript ():
    global num_inputs, num_selects, num_outputs
    read_file = open ("yosys_verilog/mux_param_template.v", "r")
    write_file = open ("yosys_verilog/mux_param.v", "w")

    lines = read_file.readlines ()
    for line in lines:
        if "*NUM_INPUTS" in line:
            write_file.write ("\tparameter NUM_INPUT = {},\n".format (num_inputs))
        elif "*NUM_SELECTS" in line:
            write_file.write ("\tparameter SEL_WIDTH = {},\n".format (num_selects))
        elif "*NUM_OUTPUTS" in line:
            write_file.write ("\tparameter DATA_WIDTH = {},\n".format (num_outputs))
        else:
            write_file.write (line)
    return


def run_gate_synthesis ():
    os.chdir ("yosys_script")
    os.system ("yosys mux_param.ys")


def run_sfq_synthesis ():
    global num_inputs, num_selects, num_outputs
    os.chdir ("../")
    os.system ("python sfq_gate_analysis.py --un mux_{}_{}_{} --vlg synth_vlg/synth_mux_param.v".format \
                (num_inputs, num_selects, num_outputs))


def main (argv):
    init_setup ()
    gen_yoscript ()
    run_gate_synthesis ()
    run_sfq_synthesis ()


if __name__ == "__main__":
    app.run (main)
