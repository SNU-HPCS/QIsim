from absl import flags
from absl import app
import os

FLAGS = flags.FLAGS
flags.DEFINE_integer ("b", 8, "# of broadcasted bitstreams")
flags.DEFINE_integer ("n", 256, "# of bitstreams")

bs = None
num_bs = None


def init_setup ():
    global bs, num_bs
    bs = FLAGS.b
    num_bs = FLAGS.n
    return


def gen_yoscript ():
    global bs, num_bs
    read_file = open ("yosys_verilog/controller_template.v", "r")
    write_file = open ("yosys_verilog/controller.v", "w")

    lines = read_file.readlines ()
    for line in lines:
        if "**BS" in line:
            write_file.write ("`define BS\t{}\n".format (bs))
        elif "**NUM_BS" in line:
            write_file.write ("`define NUM_BS\t{}\n".format (num_bs))
        else:
            write_file.write (line)
    return


def run_gate_synthesis ():
    os.chdir ("yosys_script")
    os.system ("yosys controller.ys")


def run_sfq_synthesis ():
    global bs, num_bs
    os.chdir ("../")
    os.system ("python sfq_gate_analysis.py --un controller_{}_{} --vlg synth_vlg/controller.v".format \
                (bs, num_bs))


def main (argv):
    init_setup ()
    gen_yoscript ()
    run_gate_synthesis ()
    run_sfq_synthesis ()


if __name__ == "__main__":
    app.run (main)
