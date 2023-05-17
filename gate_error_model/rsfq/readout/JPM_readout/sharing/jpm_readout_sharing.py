import os, sys, argparse
from math import *
import pandas as pd

curr_path = curr_path = os.path.abspath(__file__)
curr_dir = os.path.dirname(curr_path)
par_dir = os.path.join(curr_dir, os.pardir)
sys.path.insert(0, par_dir)

def modify_cir_netlist(L_val, jpm_id, I_dir):
    # param
    I_jpm = 0.2     # uA
    M_val = 10      # pH
    L_jpm = 1000    # pH
    K_val = round(M_val / sqrt(L_val * L_jpm), 3) # pH

    # read
    cir_template = os.path.join(os.getcwd(), "sharing_circuit.cir")
    with open(cir_template, "r") as f:
        lines = f.readlines()

    # modify
    for idx, line in enumerate(lines):
        # set I_dir, jpm_id
        if "I_dir" in line and "jpm_id" in line:
            # I_dir
            if I_dir == "ccw":
                if "a" in line.split(' ')[0]: 
                    line = line.replace("{I_dir}", "-")
                elif "clk" in line.split(' ')[0]:
                    line = line.replace("{I_dir}", "+")
                else:
                    raise Exception()
            elif I_dir == "cw": 
                if "a" in line.split(' ')[0]: 
                    line = line.replace("{I_dir}", "+")
                elif "clk" in line.split(' ')[0]:
                    line = line.replace("{I_dir}", "-")
                else:
                    raise Exception()
            else:
                raise Exception()
            
            # jpm_id 
            if int(line[1]) == jpm_id:
                line = line.replace("{jpm_id}", str(I_jpm))
            else:
                line = line.replace("{jpm_id}", "0")
        
        # set L_val
        elif "L_val" in line:
            line = line.replace("{L_val}", str(L_val))

        # set K_val
        elif "K_val" in line:
            line = line.replace("{K_val}", str(K_val))
        else:
            pass

        # apply the change
        lines[idx] = line

    # write
    cir_target = os.path.join(os.getcwd(), "l{}_jpm{}_{}.cir".format(L_val, jpm_id, I_dir))
    with open(cir_target, "w") as f:
        f.writelines(lines)

    return cir_target


def run_josim(cir_path, regen):
    csv_path = cir_path.replace("cir", "csv")
    if regen or (not regen and not os.path.exists(csv_path)):
        cmdline = "josim-cli {} -o {} > /dev/null".format(cir_path, csv_path)
        os.system(cmdline)
    else:
        pass
    return csv_path

def calc_delay(csv_path):
    df = pd.read_csv(csv_path)
    threshold = 50e-6 # A
    # delay_a
    cond_a = df["V(DFFA)"] > threshold
    delay_a = df[cond_a]["time"].iloc[0] # sec
    # delay_clk
    cond_clk = df["V(DFFC)"] > threshold
    delay_clk = df[cond_clk]["time"].iloc[0] # sec
    # NOTE: delay_diff > 0 => DFFQ rises
    delay_diff = round((delay_clk - delay_a)*1e12) # ps
    detection_lat = round((max(delay_a, delay_clk) + 1e-11)*1e9, 1) # ns
    
    #print("delay_a: ", delay_a, type(delay_a))
    #print("delay_clk: ", delay_clk)
    #print("delay_diff: ", delay_diff)
    #print("detection_lat: ", detection_lat)
    return delay_a, delay_clk, delay_diff, detection_lat


def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--min_l_value", "-min", help="Minimum L value to sweep", type=int, default=2)
    parser.add_argument ("--max_l_value", "-max", help="Maximum L value to sweep", type=int, default=6)
    args = parser.parse_args ()
    return args


if __name__ == "__main__":
    columns = ["JPM_ID", "Detection_latency(ns)", "Delay_diff_CCW(ps)", "Delay_diff_CW(ps)"]
    args = arg_parse ()
    min_l = args.min_l_value
    max_l = args.max_l_value
    L_val_list = range (min_l, max_l+1)
    jpm_id_list = range (1, 9)
    I_dir_list = ["ccw", "cw"]
    
    for L_val in L_val_list:
        df = pd.DataFrame(columns=columns)
        print("L_val: {}pH".format(L_val))
        for jpm_id in jpm_id_list: 
            detection_lat = 0
            for I_dir in I_dir_list:
                cir_path = modify_cir_netlist(L_val=L_val, jpm_id=jpm_id, I_dir=I_dir)
                csv_path = run_josim(cir_path, regen=False)
                delay_a, delay_clk, delay_diff, lat = calc_delay(csv_path)
                if I_dir == "ccw":
                    delay_diff_ccw = delay_diff
                elif I_dir == "cw":
                    delay_diff_cw = delay_diff
                else:
                    raise Exception()
                detection_lat = max(detection_lat, lat)
            #
            entry = [jpm_id, detection_lat, delay_diff_ccw, delay_diff_cw]
            df.loc[len(df)] = entry
        #
        print(df)
        print()
    os.system ("rm *cw.cir *cw.csv")
