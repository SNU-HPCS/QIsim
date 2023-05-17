#!/usr/bin/python3.8
import os, argparse
from multiprocessing import Pool
from math import ceil

def parsing (output_name):
    f = open (output_name, "r")
    lines = f.readlines ()
    for line in lines:
        if "time" in line:
            continue
        data = line.split (",")
        time = float (data[0])
        output = float (data[4])
        if (time > 1e-9) and (output > 1e-5):
            return 1

def monte_carlo (thread_num, sim_num):
    num_corrects = 0
    num_errors = 0
    for n in range (sim_num):
        os.system ("josim-cli -o output{}.csv baseline_circuit_noise.cir > /dev/null".format (thread_num))
        result = parsing ("output{}.csv".format (thread_num))
        if result == 0:
            num_errors += 1
        else:
            num_corrects += 1
    os.system ("rm output{}.csv".format (thread_num))
    return num_corrects, num_errors


def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--num_simulation", "-n", help="Number of trials for Monte-Carlo simulation", type=int, default=1000)
    args = parser.parse_args ()
    return args


if __name__ == "__main__":
    
    args = arg_parse ()
    num_sims = args.num_simulation
    num_cpus = os.cpu_count ()
    ps = list ()
    pool = Pool (num_cpus)
    os.system ("awk -f noise.awkf baseline_circuit.cir > baseline_circuit_noise.cir")
    for thread_num in range (num_cpus):
        ps.append (pool.apply_async (monte_carlo, (thread_num, ceil (num_sims/num_cpus))))
    corrects = 0
    errors = 0
    for result in ps:
        correct, error = result.get ()
        corrects += correct
        errors += error
    print ("Error rate: {}".format (errors/(corrects+errors)))
