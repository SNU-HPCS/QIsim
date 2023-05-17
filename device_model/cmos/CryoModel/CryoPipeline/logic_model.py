#!/usr/bin/env python3.8

import argparse
import os
from subprocess import PIPE, run

def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--temperature", "-t", help="Target temeprature (i.e., 300K, 77K, or 4K)", type=int, default=4)
    parser.add_argument ("--node", "-n", help="Technology node (i.e., 45nm)", type=int, default=45)
    parser.add_argument ("--vdd", "-d", help="Supply voltage", type=float, default=0)
    parser.add_argument ("--vth", "-r", help="Threshold voltage at 300K (i.e., Vth_300k)", type=float, default=0)
    args = parser.parse_args ()
    return args


def run_synthesis (design_names, temperature):
    is_not_file = 0
    is_not_ddc = 0
    for design_name in design_names:
        if not os.path.isfile ("./latency_result/{}/critical_path_{}k".format (design_name, temperature)):
            is_not_file += 1
        if not os.path.isfile ("./{}_{}k.ddc".format (design_name, temperature)):
            is_not_ddc += 1

    if is_not_file:
        if is_not_ddc:
            os.system ("make dc-topo-{}k".format (temperature))


def run_delay_extraction (design_names, temperature):
    # Critical path at target temperature (transistor + wire).
    is_not_file = 0
    for design_name in design_names:
        if not os.path.isfile ("./latency_result/{}/critical_path_{}k".format (design_name, temperature)):
            is_not_file += 1

    if is_not_file:
        os.system ("make critical-{}k".format (temperature))


def clean_up ():
    os.system ("make clean")


def main ():

    args = arg_parse ()
    temperature = args.temperature
    node = args.node
    vdd = args.vdd if args.vdd > 0 else 1.0     # Vdd of 45nm ITRS
    vth = args.vth if args.vth > 0 else 0.46893 # Vth of 45nm ITRS
    design_names = ["drive_circuit", "pulse_circuit", "readout_rx_circuit", "readout_tx_circuit"]

    # Input-requirement checking.
    if node != 45:
        print ("Currently, CryoPipeline only supports 45nm.")
        exit ()
    if not any ((temperature == key_) for key_ in [300, 77, 4]):
        print ("Currently, CryoPipeline only supports 300K, 77K, and 4K.")
        exit ()
    
    run_synthesis (design_names, temperature)
    run_delay_extraction (design_names, temperature)
    clean_up ()

    
if __name__ == "__main__":
    main ()
