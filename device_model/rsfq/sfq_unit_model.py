import pandas as pd 
import numpy as np
import math
import copy
from absl import flags
from absl import app
from IPython.display import display
pd.set_option('display.max_row', 500)
pd.set_option('display.max_columns', 100)
pd.set_option('display.expand_frame_repr', False)

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Define input arguments
FLAGS = flags.FLAGS
flags.DEFINE_string("gp", "mitll_param.csv", "sfq gate library information")
flags.DEFINE_string("cn", "connection.csv", "target unit's sfq gate connection information")
flags.DEFINE_string("bd", "breakdown.csv", "target unit's sfq gate breakdown")
flags.DEFINE_string("clk", "concurrent", "clocking scheme: [concurrent / counter]")
flags.DEFINE_string("tn", "True", "frequency tuning enable (or not)")
flags.DEFINE_string("un", "test", "unit name")
flags.DEFINE_string("outdir", "final_csv", "output directory")

gate_param_df = None
connection_df = None
breakdown_df = None
clock_connection_df = None
clock_breakdown_df = None
# DM
depth_split_tree = None
split_trees = dict ()


def isNaN(arg):
    if arg != arg:
        return True
    else:
        return False


def cal_buff_ptl(timing_gap):
    # FIXME: heuristic
    global gate_param_df 
    
    #buff_delay = gate_param_df.loc["BUFFT_RSFQ", "Delay"]
    #ptl_delay = gate_param_df.loc["PTL_RSFQ", "Delay"]
    #
    #num_buff = math.floor(timing_gap / buff_delay)
    #timing_gap -= num_buff * buff_delay
    #if timing_gap < (buff_delay / 2):
    #    num_ptl = math.ceil(timing_gap / ptl_delay)
    #else:
    #    num_buff += 1
    #    num_ptl = 0
    ptl_delay = gate_param_df.loc["PTL_RSFQ", "Delay"]
    num_ptl = math.ceil(timing_gap / ptl_delay)
    num_buff = 0

    return num_buff, num_ptl


def cal_clkline_delay(input_clkconn_df, depth):
    global gate_param_df

    clk_conn_row = input_clkconn_df.loc[depth]
    clkline_delay = 0
    for gate_type, num_gate in clk_conn_row.items():
        clkline_delay  += num_gate * gate_param_df.loc[gate_type, "Delay"]
    return clkline_delay


def cal_connection_delay(clk_scheme, input_clkconn_df, conn_entry, net):
    global gate_param_df 

    split_delay = gate_param_df.loc["SPLITT_RSFQ", "Delay"]
    buff_delay = gate_param_df.loc["BUFFT_RSFQ", "Delay"]
    ptl_delay = gate_param_df.loc["PTL_RSFQ", "Delay"]

    depth = int(conn_entry["Depth"])
    gate_net = conn_entry["{}_type".format(net)] # A,B

    # DM
    gate_delay_net = None
    # TEST
    if "input" in gate_net:
        gate_delay_net = 0
    else:
        gate_delay_net = gate_param_df.loc[gate_net, "Delay"]
    # end DM

    wire_delay_net = 0
    for name, val in conn_entry.items():
        if "split" in name and net in name:
            wire_delay_net += split_delay * val
        if "buff" in name and net in name:
            wire_delay_net += buff_delay * val
        if "ptl" in name and net in name:
            wire_delay_net += ptl_delay * val

    loop_dist = conn_entry["{}_dist_loop".format(net)]
    from_loop = not isNaN(loop_dist)

    if clk_scheme == "concurrent":
        # DM
        if from_loop:
            clock_delay = cal_clkline_delay(input_clkconn_df, depth)
            clock_delay += split_delay * split_trees[depth]["split_depth"]
            data_delay = gate_delay_net + wire_delay_net
            data_delay += split_delay * split_trees[depth+int(loop_dist)]["split_depth"]
            for level in range(depth, depth + int(loop_dist) + 1):
                data_delay += cal_clkline_delay(input_clkconn_df, level)
        else:
            clock_delay = cal_clkline_delay(input_clkconn_df, depth)
            data_delay = gate_delay_net + wire_delay_net
            clock_delay += split_delay * split_trees[depth]["split_depth"]
            if "input" not in gate_net:
                data_delay += split_delay * split_trees[depth-1]["split_depth"]
        # end DM

    if clk_scheme == "counter":
        # DM
        if from_loop:
            clock_delay = split_delay * split_trees[depth]["split_depth"]
            for level in range(depth+1, depth + int(loop_dist) + 1):
                clock_delay += cal_clkline_delay(input_clkconn_df, level)
            data_delay = gate_delay_net + wire_delay_net
            data_delay += split_delay * split_trees[depth+int(loop_dist)]["split_depth"]
        else:
            clock_delay = split_delay * split_trees[depth]["split_depth"]
            data_delay = gate_delay_net + wire_delay_net
            if "input" not in gate_net:
                data_delay += cal_clkline_delay(input_clkconn_df, depth)
                data_delay += split_delay * split_trees[depth-1]["split_depth"]
        # end DM
    return  data_delay, clock_delay


def gen_clock_connection():
    global connection_df, clock_connection_df
    ret_dict = dict()
    ret_dict['Depth'] = []
    ret_dict['SPLITT_RSFQ'] = []
    ret_dict['BUFFT_RSFQ'] = []
    ret_dict['PTL_RSFQ'] = []
    clock_connection_df = pd.DataFrame(ret_dict) 

    unit_depth = int(max(connection_df['Depth']))
    for depth in range(1, unit_depth):
        df_row = dict()
        df_row['Depth'] = depth
        df_row['SPLITT_RSFQ'] = 1
        df_row['BUFFT_RSFQ'] = 0
        df_row['PTL_RSFQ'] = 0
        clock_connection_df = clock_connection_df.append(df_row, ignore_index = True)
    clock_connection_df = clock_connection_df.set_index("Depth")
    return


def gen_clock_breakdown():
    global connection_df, clock_breakdown_df
    # DM
    global depth_split_tree
    unit_depth = int(max(connection_df['Depth'])) #including output
    
    num_split = 0
    for depth in range(1, unit_depth):
        df = connection_df.loc[connection_df['Depth'] == depth]
        curr_width = len(df.index)
        curr_depth = math.ceil(math.log2(curr_width))
        num_split += pow(2, curr_depth)-1
        split_trees[depth] = dict ()
        split_trees[depth]["split_width"] = curr_width
        split_trees[depth]["split_depth"] = curr_depth
    #print (unit_depth)
    #print (split_trees)

    ret_dict = dict()
    ret_dict['SPLITT_RSFQ'] = num_split
    ret_dict['BUFFT_RSFQ'] = 0
    ret_dict['PTL_RSFQ'] = 0

    clock_breakdown_df = pd.DataFrame(ret_dict, index=[0])
    return


def update_breakdown():
    global connection_df, clock_connection_df
    global breakdown_df, clock_breakdown_df
    global gate_param_df
   
    # breakdown
    for i in range(len(connection_df.index)):
        row = connection_df.iloc[i]
        num_buff = row["A_buff"] + row["B_buff"]
        num_ptl = row["A_ptl"] + row["B_ptl"]
        try:
            breakdown_df["BUFFT_RSFQ"] += num_buff
        except:
            breakdown_df["BUFFT_RSFQ"] = num_buff
        try:
            breakdown_df["PTL_RSFQ"] += num_ptl
        except:
            breakdown_df["PTL_RSFQ"] = num_ptl

    # clock breakdown
    for i in range(len(clock_connection_df.index)):
        row = clock_connection_df.iloc[i]
        for gate_type, num_gate in row.items():
            clock_breakdown_df[gate_type] += num_gate
    return 


def timing_adjustment(clk_scheme, input_clkconn_df, input_conn_df):
    global gate_param_df
    ret_conn_df = input_conn_df.copy(deep=True)
    
    for i in range(len(ret_conn_df.index)):
        row = ret_conn_df.iloc[i].copy()
        ###
        gate_target = row["Type"]
        if 'output' in gate_target:
            continue

        A2B_time = gate_param_df.loc[gate_target, "A2BTime"]
        B2A_time = gate_param_df.loc[gate_target, "B2ATime"]
        C2I_time = gate_param_df.loc[gate_target, "C2ITime"]

        gate_A = row["A_type"]
        gate_B = row["B_type"]
        depth = row["Depth"]
        # IK FIXED
        A_from_loop = not isNaN(row["A_dist_loop"])
        B_from_loop = not isNaN(row["B_dist_loop"])

        # 0. A/B delay Balancing
        # DM
        if not (isNaN (gate_A)) and not (isNaN (gate_B)):
            data_delay_A, _ = cal_connection_delay(clk_scheme, input_clkconn_df, row, "A")
            data_delay_B, _ = cal_connection_delay(clk_scheme, input_clkconn_df, row, "B")
            
            delay_B2A = data_delay_A - data_delay_B 
            # IK: FIXED condition not to include the loop case
            # if delay_B2A - B2A_time > 0:
            if delay_B2A - B2A_time > 0 and not A_from_loop:
                timing_gap = delay_B2A - B2A_time
                num_buff, num_ptl = cal_buff_ptl(timing_gap)
                row["B_buff"] += num_buff
                row["B_ptl"] += num_ptl

            delay_A2B = data_delay_B - data_delay_A
            # IK: FIXED condition not to include the loop case
            # if delay_A2B - A2B_time > 0:
            if delay_A2B - A2B_time > 0 and not B_from_loop:
                timing_gap = delay_A2B - A2B_time
                num_buff, num_ptl = cal_buff_ptl(timing_gap)
                row["A_buff"] += num_buff
                row["A_ptl"] += num_ptl
        # end DM
        # 1. C2I timing
        # DM
        if not (isNaN(gate_A)):
            data_delay_A, clock_delay_A = cal_connection_delay(clk_scheme, input_clkconn_df, row, "A")
            delay_C2I = data_delay_A - clock_delay_A
            if C2I_time > delay_C2I:
                timing_gap = C2I_time - delay_C2I
                num_buff, num_ptl = cal_buff_ptl(timing_gap)
                row["A_buff"] += num_buff
                row["A_ptl"] += num_ptl
        
        if not (isNaN(gate_B)):
            data_delay_B, clock_delay_B = cal_connection_delay(clk_scheme, input_clkconn_df, row, "B")
            delay_C2I = data_delay_B - clock_delay_B
            if C2I_time > delay_C2I:
                timing_gap = C2I_time - delay_C2I
                num_buff, num_ptl = cal_buff_ptl(timing_gap)
                row["B_buff"] += num_buff
                row["B_ptl"] += num_ptl
        # end DM

        # 2. A2B & B2A timing 
        if (isNaN(gate_A) or 'input' in gate_A) or (isNaN(gate_B) or 'input' in gate_B):
            pass
        else:
            data_delay_A, _ = cal_connection_delay(clk_scheme, input_clkconn_df, row, "A")
            data_delay_B, _ = cal_connection_delay(clk_scheme, input_clkconn_df, row, "B")
            
            '''
            # IK: debugging in the revision
            if data_delay_A >= data_delay_B:
                delay_B2A = data_delay_A - data_delay_B
                timing_gap = abs(B2A_time - delay_B2A)
                num_buff, num_ptl = cal_buff_ptl(timing_gap)

                if B2A_time > delay_B2A:
                    row["A_buff"] += num_buff
                    row["A_ptl"] += num_ptl
                else: 
                    row["B_buff"] += num_buff
                    row["B_ptl"] += num_ptl
            else: # data_delay_A < data_delay_B
                delay_A2B = data_delay_B - data_delay_A
                timing_gap = abs(A2B_time - delay_A2B)
                num_buff, num_ptl = cal_buff_ptl(timing_gap)
                if A2B_time > delay_A2B:
                    row["B_buff"] += num_buff
                    row["B_ptl"] += num_ptl
                else:
                    row["A_buff"] += num_buff
                    row["A_ptl"] += num_ptl
            # END IK
            '''
            if data_delay_A >= data_delay_B: 
                delay_B2A = data_delay_A - data_delay_B 
                if B2A_time > delay_B2A:
                    timing_gap = B2A_time - delay_B2A
                    num_buff, num_ptl = cal_buff_ptl(timing_gap)
                    row["A_buff"] += num_buff
                    row["A_ptl"] += num_ptl

            if data_delay_A < data_delay_B: 
                delay_A2B = data_delay_B - data_delay_A
                if A2B_time > delay_A2B:
                    timing_gap = A2B_time - delay_A2B
                    num_buff, num_ptl = cal_buff_ptl(timing_gap)
                    row["B_buff"] += num_buff
                    row["B_ptl"] += num_ptl
        ret_conn_df.iloc[i] = row
    ret_conn_df = ret_conn_df.sort_values(by=['Depth'], ascending=True)
    return ret_conn_df


def cal_min_cct(clk_scheme, input_clkconn_df, input_conn_df):
    global gate_param_df

    ret_conn_df = input_conn_df.copy(deep=True)
    ret_conn_df['MinCCT'] = [None]*len(ret_conn_df.index)
    
    for i in range(len(ret_conn_df.index)):
        row = ret_conn_df.iloc[i].copy()
        gate_target = row["Type"]
        if 'output' in gate_target:
            continue

        A2A_time = gate_param_df.loc[gate_target, "A2ATime"]
        B2B_time = gate_param_df.loc[gate_target, "B2BTime"]
        C2C_time = gate_param_df.loc[gate_target, "C2CTime"]

        if row["A_depth_split"] > 0:
            A2A_time = max(A2A_time, gate_param_df.loc["SPLITT_RSFQ", "A2ATime"])
        if row["A_buff"] > 0:
            A2A_time = max(A2A_time, gate_param_df.loc["BUFFT_RSFQ", "A2ATime"])
        if row["A_ptl"] > 0:
            A2A_time = max(A2A_time, gate_param_df.loc["PTL_RSFQ", "A2ATime"])
        

        for gate_type, _ in input_clkconn_df.loc[row["Depth"]].items():
            A2A_time = max(A2A_time, gate_param_df.loc[gate_type, "A2ATime"])
        
        I2C_time = gate_param_df.loc[gate_target, "I2CTime"]

        gate_A = row["A_type"]
        gate_B = row["B_type"]
        depth = row["Depth"]

        # DM
        if not (isNaN(gate_A)):
            data_delay_A, clock_delay_A = cal_connection_delay(clk_scheme, input_clkconn_df, row, "A")
            delay_C2A = data_delay_A - clock_delay_A
        else:
            delay_C2A = 0
        # DM
        if not (isNaN(gate_B)):
            data_delay_B, clock_delay_B = cal_connection_delay(clk_scheme, input_clkconn_df, row, "B")
            delay_C2B = data_delay_B - clock_delay_B
        else:
            delay_C2B = 0

        delay_C2I = max(delay_C2A, delay_C2B)
        if delay_C2I == 0: # A and B are inputs
            continue

        I2I_time = max(max(A2A_time, B2B_time), C2C_time)
        min_cct = delay_C2I + I2C_time
        min_cct = max(min_cct, I2I_time)
        row['MinCCT'] = min_cct
        if row["Type"] == "NDROT_RSFQ":
            print ("C2I delay: {}".format (delay_C2I))
            print ("I2C time: {}".format (I2C_time))
            print ("I2I time: {}".format (I2I_time))
            print ("Min CCT: {}".format (min_cct))
        ret_conn_df.iloc[i] = row
    return ret_conn_df


def unit_freq(clk_scheme, tuning):
    global clock_connection_df, connection_df

    # Initial timing adjustment
    connection_df = timing_adjustment(clk_scheme, clock_connection_df, connection_df)
    # Calculate min_cct for each gate pair without tuning
    connection_df = cal_min_cct(clk_scheme, clock_connection_df, connection_df)
    connection_df = connection_df.sort_values(by=["MinCCT"], ascending=False)

    # Tuning
    if tuning == "True":
        #print("Frequency_tuning start: {}[GHz]".format(1000/connection_df.iloc[0]["MinCCT"]))
        temp_clkconn_df = clock_connection_df.copy(deep=True)
        temp_conn_df = connection_df.copy(deep=True)
        if clk_scheme == "concurrent":
            while(True):
                row = temp_conn_df.iloc[0].copy()
                # Check whether the tuning is possible or not
                # 0. MinCCT should not be None
                if row["MinCCT"] is None:
                    break
                # 1. Should not include the loop
                from_loop_A = not isNaN(row["A_dist_loop"])
                from_loop_B = not isNaN(row["B_dist_loop"])
                if from_loop_A or from_loop_B:
                    break
                # 2. data_delay should be meaningfully larger tan the clock_delay
                if not isNaN(row["A_type"]):
                    data_delay_A, clock_delay_A = cal_connection_delay(clk_scheme, temp_clkconn_df, row, "A") 
                    delay_C2A = data_delay_A - clock_delay_A
                else:
                    delay_C2A = 1000 # Heuristic
                if not isNaN(row["B_type"]):
                    data_delay_B, clock_delay_B = cal_connection_delay(clk_scheme, temp_clkconn_df, row, "B")
                    delay_C2B = data_delay_B - clock_delay_B
                else: 
                    delay_C2B = 1000 # Heuristic
                
                delay_C2I = min(delay_C2A, delay_C2B)
                C2I_time = gate_param_df.loc[row["Type"], "C2ITime"]
                timing_gap = delay_C2I - C2I_time
                ptl_delay = gate_param_df.loc["PTL_RSFQ", "Delay"]
                
                if timing_gap > ptl_delay: # Then, do tuning!
                    curr_cct = row["MinCCT"]
                    num_buff, num_ptl = cal_buff_ptl(timing_gap)
                    depth = int(row["Depth"])
                    clk_conn_row = temp_clkconn_df.loc[depth].copy()
                    clk_conn_row["BUFFT_RSFQ"] += num_buff
                    clk_conn_row["PTL_RSFQ"] += num_ptl
                    temp_clkconn_df.loc[depth] = clk_conn_row
                    temp_conn_df = timing_adjustment(clk_scheme, temp_clkconn_df, temp_conn_df)
                    temp_conn_df = cal_min_cct(clk_scheme, temp_clkconn_df, temp_conn_df)
                    temp_conn_df = temp_conn_df.sort_values(by=["MinCCT"], ascending=False)
                    new_cct = temp_conn_df.iloc[0]["MinCCT"]
                    
                    # TEST
                    print ("\n[{}]".format (row["Name"]))
                    print("Current frequency: {}[GHz]".format(1000/new_cct))
                    if (curr_cct - new_cct) >= -0.5:
                        connection_df = temp_conn_df.copy(deep=True)
                        clock_connection_df = temp_clkconn_df.copy(deep=True)
                        continue
                    else:
                        print("Frequency_tuned: {}[GHz]".format(1000/new_cct))
                        break
                else:
                    print("End of frequency tuning")
                    break
        else:
            print("No frequency tuning")
    else:
        print("No frequency tuning")
    min_cct = connection_df.iloc[0]["MinCCT"]
    frequency = round(1000/min_cct, 2) # GHz (cct's unit is ps)
    return frequency # GHz


def unit_area():
    global gate_param_df, breakdown_df, clock_breakdown_df
    area = 0
    jjs = 0
    for gate in breakdown_df.columns:
        gate_num = breakdown_df[gate][0]
        gate_area = gate_param_df.loc[gate, "Area"]
        gate_jjs = gate_param_df.loc[gate, "JJs"]
        area += gate_num * gate_area
        jjs += gate_num * gate_jjs

    for gate in clock_breakdown_df:
        gate_num = clock_breakdown_df[gate][0]
        gate_area = gate_param_df.loc[gate, "Area"]
        gate_jjs = gate_param_df.loc[gate, "JJs"]
        area += gate_num * gate_area
        jjs += gate_num * gate_jjs

    return area, jjs # um^2


def unit_power():
    global gate_param_df, breakdown_df, clock_breakdown_df 
    static_power = 0
    dynamic_energy = 0

    for gate in breakdown_df.columns:
        gate_num = breakdown_df[gate][0]
        gate_stat_p = gate_param_df.loc[gate, "PowerStatic"]
        gate_dyn_e = gate_param_df.loc[gate, "EnergyDynamic"]
        static_power += gate_num * gate_stat_p
        dynamic_energy += gate_num * gate_dyn_e

    for gate in clock_breakdown_df:
        gate_num = clock_breakdown_df[gate][0]
        gate_stat_p = gate_param_df.loc[gate, "PowerStatic"]
        gate_dyn_e = gate_param_df.loc[gate, "EnergyDynamic"]
        static_power += gate_num * gate_stat_p
        dynamic_energy += gate_num * gate_dyn_e



    dynamic_energy = round(dynamic_energy, 2)

    return static_power, dynamic_energy # nW, nJ/Gacc


def main(argv):
    global gate_param_df, connection_df, breakdown_df

    gate_param_df = pd.read_csv(FLAGS.gp)
    gate_param_df = gate_param_df.set_index("Name")
    connection_df = pd.read_csv(FLAGS.cn)
    breakdown_df = pd.read_csv(FLAGS.bd)
    clk_scheme = FLAGS.clk
    tuning = FLAGS.tn
    unit_name = FLAGS.un
    output_dir = FLAGS.outdir
    ###
    connection_df["A_buff"] = [0] * len(connection_df.index)
    connection_df["A_ptl"] = [0] * len(connection_df.index)
    connection_df["B_buff"] = [0] * len(connection_df.index)
    connection_df["B_ptl"] = [0] * len(connection_df.index)
    ###
    
    ###
    gen_clock_connection()
    gen_clock_breakdown()
    ###
    
    ###
    frequency = unit_freq(clk_scheme, tuning)
    update_breakdown()
    static_power, dynamic_energy = unit_power()
    area, jjs = unit_area()
    ###
    
    print("Frequency: {} [GHz]".format(frequency))
    print("Static power: {} [nW]".format(static_power))
    print("Dynamic energy: {} [nJ/Gacc]".format(dynamic_energy))
    print("Area: {} [um^2]".format(area))
    print("JJs: {} [#]".format(jjs))

    #print()
    #print("Final connection")
    #print(connection_df)
    ret_dict = dict()
    ret_dict["Frequency"] = frequency
    ret_dict["PowerStatic"] = static_power
    ret_dict["EnergyDynamic"] = dynamic_energy
    ret_dict["Area"] = area
    ret_df = pd.DataFrame(ret_dict, index=[0])
    
    if unit_name != "test":
        #connection_df.to_csv("final_csv/{}_connection.csv".format(unit_name), index=False)
        #clock_connection_df.to_csv("final_csv/{}_clock_connection.csv".format(unit_name), index=False)
        pass

    if output_dir is not None:
        #unit_name = FLAGS.cn.split("/")[-1].split(".")[0].replace("_connection", "")
        ret_df.to_csv("{}/{}_fpa.csv".format(output_dir, unit_name), index=False)
        connection_df.to_csv("{}/{}_connection_final.csv".format(output_dir, unit_name), index=False)
        clock_connection_df.to_csv("{}/{}_clkconnection_final.csv".format(output_dir, unit_name), index=False)
        breakdown_df.to_csv("{}/{}_breakdown_final.csv".format(output_dir, unit_name), index=False)
        clock_breakdown_df.to_csv("{}/{}_clkbreakdown_final.csv".format(output_dir, unit_name), index=False)

    return


if __name__ == "__main__":
    app.run(main)
