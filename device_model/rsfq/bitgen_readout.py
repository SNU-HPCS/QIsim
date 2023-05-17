import pandas as pd
import numpy as np
from math import *
import copy
from absl import flags, app
pd.set_option('display.max_row', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Define input arguments
FLAGS = flags.FLAGS
flags.DEFINE_integer ("ly", 481, "Length of Y-gate bitstream")
flags.DEFINE_string ("outdir", "./unit_csv", "output directory")
flags.DEFINE_string ("un", None, "unit name")

# User inputs
y_length = None

# Define output dataframes
connection_df = None
breakdown_df = None
connection_columns = ["Type","Name","Depth","A_type","A_name","A_depth_split","A_dist_loop",\
                    "B_type","B_name","B_depth_split","B_dist_loop"]
breakdown_columns = ["SPLITT_RSFQ", "ANDT_RSFQ", "DFFT_RSFQ", "NOTT_RSFQ", "NDROT_RSFQ"]

# gate numbering
num_and = 0
num_or = 0
num_dff = 0
num_not = 0
num_split = 0
num_ndro = 0


def init_setup ():
    global connection_df, breakdown_df, y_length
    global num_and, num_or, num_dff, num_not, num_split
    global connection_columns, breakdown_columns

    connection_df = pd.DataFrame (None, columns=connection_columns)
    breakdown_df = pd.DataFrame (dict.fromkeys (breakdown_columns, 0), \
                                index=[0], columns=breakdown_columns)
    y_length = FLAGS.ly
    return


def gen_bitgen ():
    global connection_df, breakdown_df, y_length
    global num_and, num_or, num_dff, num_not, num_split
    outputs_ = list ()
    # select declare
    input_df = pd.DataFrame({"Type": "input_bitstream", "Name": "bitstream"}, index=[0])
    output_, depth = gen_shift_register (input_df, y_length, 1)
    return output_


def gen_shift_register (input, target_dffs, depth):
    global connection_df, breakdown_df, y_length
    global num_and, num_or, num_dff, num_not, num_split
    if target_dffs <= 0:
        return input
    input_list_ = list ()
    input_list_.append (input)
    output_ = None
    for dff_index_ in range (target_dffs):
        ## insert DFF
        input_ = input_list_.pop ()
        if "input" in input_["Type"].item ():
            select_splits = 0
            dff0_ = {"Type": "ORT_RSFQ", \
                     "Name": "_OR{}_".format (num_or), \
                     "Depth": depth + dff_index_, \
                     "A_type": input_["Type"].item (), \
                     "A_name": input_["Name"].item (), \
                     "A_depth_split": select_splits, \
                     }
            num_or += 1
        else:
            select_splits = 0
            dff0_ = {"Type": "DFFT_RSFQ", \
                     "Name": "_DFF{}_".format (num_dff), \
                     "Depth": depth + dff_index_, \
                     "A_type": input_["Type"].item (), \
                     "A_name": input_["Name"].item (), \
                     "A_depth_split": select_splits, \
                     }
            num_dff += 1
        connection_df = connection_df.append (dff0_, ignore_index=True)
        num_split += select_splits
        input_list_.append (pd.DataFrame (dff0_, index=[0]))
        output_ = pd.DataFrame (dff0_, index=[0])
        
        if dff_index_ == target_dffs-1:
            num_split += 1
            connection_df.loc[0]["B_type"] = "DFFT_RSFQ"
            connection_df.loc[0]["B_name"] = "_DFF{}_".format ((num_dff-1))
            connection_df.loc[0]["B_depth_split"] = 1
            connection_df.loc[0]["B_dist_loop"] = dff_index_

    return output_, (depth + target_dffs) # output, depth


def connect_outputs (output_):
    global connection_df, breakdown_df, y_length
    global num_and, num_or, num_dff, num_not, num_split
    
    out_ = {"Type": "output_inst", \
            "Name": "inst", \
            "Depth": output_["Depth"].item () + 1, \
            "A_type": output_["Type"].item (), \
            "A_name": output_["Name"].item (), \
            "A_depth_split": 0, \
          }
    connection_df = connection_df.append (out_, ignore_index=True)


def update_breakdown ():
    breakdown_df["ANDT_RSFQ"] = num_and
    breakdown_df["DFFT_RSFQ"] = num_dff
    breakdown_df["NOTT_RSFQ"] = num_not
    breakdown_df["SPLITT_RSFQ"] = num_split
    breakdown_df["NDROT_RSFQ"] = num_ndro


# Build connection and breakdown csv file of the NDRO RAM with write-operation only
def main (argv):
    global connection_df, breakdown_df, y_length
    global num_and, num_or, num_dff, num_not, num_split

    unit_csv_dir = FLAGS.outdir
    unit_name = FLAGS.un
    init_setup ()
    
    output = gen_bitgen ()
    connect_outputs (output)
    
    update_breakdown ()
    template = "{}/bitgen_readout_{}_{}.csv"
    connection_df.to_csv(template.format(unit_csv_dir, y_length, "connection"), index = False)
    breakdown_df.to_csv(template.format(unit_csv_dir, y_length, "breakdown"), index = False)


if __name__ == "__main__":
    app.run (main)


