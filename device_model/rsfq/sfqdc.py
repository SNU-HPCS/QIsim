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
flags.DEFINE_integer ("n", 5, "Bit width of 2q_sel")
flags.DEFINE_string ("outdir", "./unit_csv", "output directory")
flags.DEFINE_string ("un", None, "unit name")

# User inputs
num_2q_sel = None

# Define output dataframes
connection_df = None
breakdown_df = None
connection_columns = ["Type","Name","Depth","A_type","A_name","A_depth_split","A_dist_loop",\
                    "B_type","B_name","B_depth_split","B_dist_loop"]
breakdown_columns = ["SPLITT_RSFQ", "ANDT_RSFQ", "DFFT_RSFQ", "NOTT_RSFQ", "NDROT_RSFQ", "SFQDC"]

# gate numbering
num_and = 0
num_or = 0
num_dff = 0
num_not = 0
num_split = 0
num_ndro = 0
num_sfqdc = 0


def init_setup ():
    global connection_df, breakdown_df, num_2q_sel
    global num_and, num_or, num_dff, num_not, num_split
    global connection_columns, breakdown_columns

    connection_df = pd.DataFrame (None, columns=connection_columns)
    breakdown_df = pd.DataFrame (dict.fromkeys (breakdown_columns, 0), \
                                index=[0], columns=breakdown_columns)
    num_2q_sel = FLAGS.n
    return


def gen_sfqdc ():
    global connection_df, breakdown_df, num_2q_sel
    global num_and, num_or, num_dff, num_not, num_split, num_sfqdc

    outputs1_ = list ()
    num_split += 2**(ceil (log (num_2q_sel, 2))) - 1
    for num_sel_ in range (num_2q_sel):
        and_ = {"Type": "ANDT_RSFQ", \
                "Name": "_AND{}_".format (num_and), \
                "Depth": 1, \
                "A_type": "input_ctrl", \
                "A_name": "ctrl", \
                "A_depth_split": ceil (log (num_2q_sel, 2)), \
                "B_type": "input_q2_sel[{}]".format (num_sel_), \
                "B_name": "q2_sel[{}]".format (num_sel_), \
                "B_depth_split": 0,
                }
        and_ = pd.DataFrame (and_, index=[0])
        num_and += 1
        connection_df = connection_df.append (and_, ignore_index=True)
        outputs1_.append (and_)
    '''
    outputs_ = list ()
    for num_sel_, and_ in enumerate (outputs1_):
        num_split += 2**num_sel_ - 1
        for n_ in range (2**num_sel_):
            sfqdc_ = {"Type": "SFQDC", \
                    "Name": "_SFQDC{}_".format (num_sfqdc), \
                    "Depth": 2, \
                    "A_type": and_["Type"], \
                    "A_name": and_["Name"], \
                    "A_depth_split": num_sel_, \
                    }
            sfqdc_ = pd.DataFrame (sfqdc_, index=[0])
            num_sfqdc += 1
            connection_df = connection_df.append (sfqdc_, ignore_index=True)
            outputs_.append (sfqdc_)
    '''
    return outputs1_ # SFQ/DC output ports
    #return outputs_ # SFQ/DC output ports


def connect_outputs (outputs):
    global connection_df, breakdown_df, num_2q_sel
    global num_and, num_or, num_dff, num_not, num_split, num_sfqdc
    
    for output_ in outputs:
        # insert output
        out_ = {"Type": "output_pulse", \
                "Name": "pulse", \
                "Depth": output_["Depth"].item () + 1, \
                "A_type": output_["Type"].item (), \
                "A_name": output_["Name"].item (), \
                "A_depth_split": 0, \
              }
        connection_df = connection_df.append (out_, ignore_index=True)
    return


def update_breakdown ():
    global connection_df, breakdown_df, num_2q_sel
    global num_and, num_or, num_dff, num_not, num_split, num_sfqdc
    breakdown_df["ANDT_RSFQ"] = num_and
    breakdown_df["DFFT_RSFQ"] = num_dff
    breakdown_df["NOTT_RSFQ"] = num_not
    breakdown_df["SPLITT_RSFQ"] = num_split
    breakdown_df["NDROT_RSFQ"] = num_ndro
    breakdown_df["SFQDC"] = num_sfqdc


# Build connection and breakdown csv file of the NDRO RAM with write-operation only
def main (argv):
    global connection_df, breakdown_df, num_2q_sel
    global num_and, num_or, num_dff, num_not, num_split

    unit_csv_dir = FLAGS.outdir
    unit_name = FLAGS.un
    init_setup ()
    
    outputs_ = gen_sfqdc ()
    connect_outputs (outputs_)
    
    update_breakdown ()
    template = "{}/sfqdc_{}_{}.csv"
    connection_df.to_csv(template.format(unit_csv_dir, num_2q_sel, "connection"), index = False)
    breakdown_df.to_csv(template.format(unit_csv_dir, num_2q_sel, "breakdown"), index = False)


if __name__ == "__main__":
    app.run (main)


