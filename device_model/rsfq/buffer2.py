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
flags.DEFINE_integer ("d", 1, "number of data bits")
flags.DEFINE_string ("outdir", "./unit_csv", "output directory")
flags.DEFINE_string ("un", None, "unit name")

# User inputs
num_data_bits = None

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
    global connection_df, breakdown_df, num_data_bits
    connection_df = pd.DataFrame (None, columns=connection_columns)
    breakdown_df = pd.DataFrame (dict.fromkeys (breakdown_columns, 0), \
                                index=[0], columns=breakdown_columns)
    num_data_bits = FLAGS.d
    return


def gen_ndro_array (wr_data_list, wr_enable_list, depth):
    global connection_df, breakdown_df, num_data_bits
    global num_and, num_or, num_dff, num_not, num_split, num_ndro
    output_list_ = list ()
    for wr_data_, wr_enable_ in zip (wr_data_list, wr_enable_list):
        output_list_.append ((gen_ndro_cell (wr_data_, wr_enable_, depth)))
    return output_list_
    

def gen_ndro_cell (wr_data, wr_enable, depth):
    global connection_df, breakdown_df, num_data_bits
    global num_and, num_or, num_dff, num_not, num_split, num_ndro
    # Depth 1
    ## insert AND
    and0_ = {"Type": "ANDT_RSFQ", \
             "Name": "_AND{}_".format (num_and), \
             "Depth": depth, \
             "A_type": wr_data["Type"].item (), \
             "A_name": wr_data["Name"].item (), \
             "A_depth_split": 0, \
             "B_type": wr_enable["Type"].item (), \
             "B_name": wr_enable["Name"].item (), \
             #"B_depth_split": 1, \
             "B_depth_split": 1 + ceil(log(num_data_bits,2)), \
             }
    connection_df = connection_df.append (and0_, ignore_index=True)
    num_and += 1
    num_split += 1
    ## insert DFF
    dff0_ = {"Type": "DFFT_RSFQ", \
             "Name": "_DFF{}_".format (num_dff), \
             "Depth": depth, \
             "A_type": wr_enable["Type"].item (), \
             "A_name": wr_enable["Name"].item (), \
             #"A_depth_split": 1, \
             "A_depth_split": 1 + ceil(log(num_data_bits,2)), \
             }
    connection_df = connection_df.append (dff0_, ignore_index=True)
    num_dff += 1
    ## insert NDRO
    ndro0_ = {"Type": "NDROT_RSFQ", \
             "Name": "_NDRO{}_".format (num_ndro), \
             "Depth": depth+1, \
             "A_type": "ANDT_RSFQ", \
             "A_name": "_AND{}_".format ((num_and-1)), \
             "A_depth_split": 0, \
             "B_type": "DFFT_RSFQ", \
             "B_name": "_DFF{}_".format ((num_dff-1)), \
             "B_depth_split": 0, \
             }
    connection_df = connection_df.append (ndro0_, ignore_index=True)
    num_ndro += 1
    return pd.DataFrame (ndro0_, index=[0])


def connect_outputs (ndro_list, depth):
    global connection_df, breakdown_df, num_data_bits
    global num_and, num_or, num_dff, num_not, num_split, num_ndro
    
    for n_, ndro_ in enumerate (ndro_list):
        ## insert output
        out_ = {"Type": "output_ndro[{}]".format (n_), \
                 "Name": "ndro[{}]".format (n_), \
                 "Depth": depth, \
                 "A_type": "NDROT_RSFQ", \
                 "A_name": "_NDRO{}_".format ((n_)), \
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
    unit_csv_dir = FLAGS.outdir
    unit_name = FLAGS.un
    init_setup ()
    enable_df = pd.DataFrame({"Type": "input_enable", "Name": "enable"}, index=[0])
    output_list = list ()
    for data_bit_ in range (num_data_bits):
        data_df = None
        if num_data_bits == 1:
            data_df = pd.DataFrame({"Type": "input_data", "Name": "data"}, index=[0])
        else:
            data_df = pd.DataFrame({"Type": "input_data[{}]".format (data_bit_), \
                                    "Name": "data[{}]".format (data_bit_)}, index=[0])
        enable_list = list ()
        enable_list.append (enable_df)
        data_list = list ()
        data_list.append (data_df)
        output_list = output_list + gen_ndro_array (data_list, enable_list, 1)
    connect_outputs (output_list, 3)
    update_breakdown ()
    template = "{}/buffer2_{}data_{}.csv"
    if unit_name is None:
        connection_df.to_csv (template.format (unit_csv_dir, num_data_bits, "connection"), index=False)
        breakdown_df.to_csv (template.format (unit_csv_dir, num_data_bits, "breakdown"), index=False)
    else:
        connection_df.to_csv("{}/{}_write_connection.csv".format(unit_csv_dir, unit_name), index = False)
        breakdown_df.to_csv("{}/{}_write_breakdown.csv".format(unit_csv_dir, unit_name), index = False)


'''
# Build connection and breakdown csv file of the NDRO RAM with write-operation only
def main (argv):
    unit_csv_dir = FLAGS.outdir
    unit_name = FLAGS.un
    init_setup ()
    output_list = list ()
    for data_bit_ in range (num_data_bits):
        enable_df = None
        data_df = None
        if num_data_bits == 1:
            enable_df = pd.DataFrame({"Type": "input_enable", "Name": "enable"}, index=[0])
            data_df = pd.DataFrame({"Type": "input_data", "Name": "data"}, index=[0])
        else:
            enable_df = pd.DataFrame({"Type": "input_enable[{}]".format (data_bit_), \
                                    "Name": "enable[{}]".format (data_bit_)}, index=[0])
            data_df = pd.DataFrame({"Type": "input_data[{}]".format (data_bit_), \
                                    "Name": "data[{}]".format (data_bit_)}, index=[0])
        enable_list = list ()
        enable_list.append (enable_df)
        data_list = list ()
        data_list.append (data_df)
        output_list = output_list + gen_ndro_array (data_list, enable_list, 1)
    connect_outputs (output_list, 3)
    update_breakdown ()
    template = "{}/buffer2_{}data_{}.csv"
    if unit_name is None:
        connection_df.to_csv (template.format (unit_csv_dir, num_data_bits, "connection"), index=False)
        breakdown_df.to_csv (template.format (unit_csv_dir, num_data_bits, "breakdown"), index=False)
    else:
        connection_df.to_csv("{}/{}_write_connection.csv".format(unit_csv_dir, unit_name), index = False)
        breakdown_df.to_csv("{}/{}_write_breakdown.csv".format(unit_csv_dir, unit_name), index = False)
'''


if __name__ == "__main__":
    app.run (main)


