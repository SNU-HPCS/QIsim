import pandas as pd
import numpy as np
import math
import copy
from absl import flags, app
pd.set_option ('display.max_row', 500)
pd.set_option ('display.max_columns', 100)

# Define input arguments
# (Default inputs are the inputs for FULL ADDER)
FLAGS = flags.FLAGS
flags.DEFINE_string("gp", "mitll_param.csv", "sfq gate library information")
flags.DEFINE_string("cn", "final_csv/full_adder_connection.csv", "target unit's sfq gate connection")
flags.DEFINE_string("ccn", "final_csv/full_adder_clock_connection.csv", "target unit's sfq clk connection")
flags.DEFINE_string("clk", "concurrent", "clocking scheme: [concurrent / counter]")
flags.DEFINE_string("un", "full_adder", "unit name")


# global variables
## constants
final_vlg_folder = "final_vlg"

## global options
clk_scheme = None
unit_name = None

## output file
file = None

## data structure from previous pipelines
gate_param_df = None
connection_df = None
clk_connection_df = None

## numbering parameters for distinct naming
clk_conn_table = dict ()
gate_conn_table = dict ()
num_wire = 0
num_splitter = 0
num_buffer = 0
num_ptl = 0

def initial_setup ():
    global final_vlg_folder, clk_scheme, unit_name, file
    global gate_param_df, connection_df, clk_connection_df

    gate_param_df = pd.read_csv(FLAGS.gp).set_index ("Name")
    connection_df = pd.read_csv(FLAGS.cn)
    clk_connection_df = pd.read_csv(FLAGS.ccn)
    clk_scheme = FLAGS.clk
    unit_name = FLAGS.un
    file = open ("{}/{}_sfq.v".format (final_vlg_folder, unit_name), "w")
    return


def start_module ():
    global file, connection_df
    inputs_ = list ()
    outputs_ = list ()
    connection_df = connection_df.fillna ('NaN')

    # find inputs
    temp_df_ = connection_df[connection_df["A_type"].str.contains ("input")].copy ()
    inputs_ = inputs_ + temp_df_["A_type"].tolist ()
    temp_df_ = connection_df[connection_df["B_type"].str.contains ("input")].copy ()
    inputs_ = inputs_ + temp_df_["B_type"].tolist ()
    inputs_ = list (set (inputs_)) # deduplication
    inputs_.append ("input_clk")

    # find outputs
    temp_df_ = connection_df[connection_df["Type"].str.contains ("output")].copy ()
    outputs_ = outputs_ + temp_df_["Type"].tolist ()
    outputs_ = list (set (outputs_)) # deduplication

    # find arrays in in/outputs
    ## find arrays in inputs and parse them (i.e., [max_index_:0] name_)
    if any ("[" in input_ for input_ in inputs_):
        arrays_ = [input_ for input_ in inputs_ if ("[" in input_)]
        names_ = list (set ([entry_.split ("[")[0] for entry_ in arrays_]))
        for name_ in names_:
            print (name_)
            print (inputs_)
            inputs_ = [input_ for input_ in inputs_ if (name_ not in input_)]
            temp_ = [int (array_.split ("[")[1].split ("]")[0]) for array_ in arrays_ if (name_ in array_)]
            max_index_ = max (temp_)
            inputs_.append ("[{}:0] {}".format (max_index_, name_))
    ## find arrays in outputs and parse them (i.e., [max_index_:0] name_)
    if any ("[" in output_ for output_ in outputs_):
        arrays_ = [output_ for output_ in outputs_ if ("[" in output_)]
        names_ = list (set ([entry_.split ("[")[0] for entry_ in arrays_]))
        for name_ in names_:
            outputs_ = [output_ for output_ in outputs_ if (name_ not in output_)]
            temp_ = [int (array_.split ("[")[1].split ("]")[0]) for array_ in arrays_ if (name_ in array_)]
            max_index_ = max (temp_)
            outputs_.append ("[{}:0] {}".format (max_index_, name_))

    # declaration (file write)
    inouts_ = inputs_ + outputs_
    file.write ("/* Generated by SNU HPCS Lab - CryoTeam */\n")
    file.write ("module {}_sfq (".format (unit_name))
    for inout_ in inouts_:
        # because [x:0] should not be appended in module declaration.
        if "]" in inout_:
            file.write ("{}".format (inout_.split ("] ")[1]))
        else:
            file.write ("{}".format (inout_))
        if inout_ == outputs_[-1]:
            file.write (");\n")
        else:
            file.write (", ")
    file.write ("\n")
    file.write ("/* Input/output declaration */\n")
    for input_ in inputs_:
        file.write ("input {};\n".format (input_))
    for output_ in outputs_:
        file.write ("output {};\n".format (output_))
    file.write ("\n")
    return


def end_module ():
    global file
    file.write ("endmodule\n")
    file.close ()
    return


def clock_generation ():
    global clk_scheme, file, connection_df, clk_connection_df
    global clk_conn_table

    # find clock depth (max_depth_) and fanout (num_gates_)
    max_depth_ = int (max (connection_df["Depth"].tolist ()) - 1)
    num_gates_ = dict ()
    for depth_ in range (max_depth_):
        gates_ = len (connection_df[connection_df["Depth"] == (depth_+1)])
        num_gates_[depth_] = gates_
    
    # clock declaration
    file.write ("/*********************/\n")
    file.write ("/*** CLOCK NETWORK ***/\n")
    file.write ("/*********************/\n\n")
    intermediate_wires_ = list ()
    intermediate_wires_.append ("input_clk")

    # network for concurrent-flow clocking
    if clk_scheme == "concurrent":
        # generate the clock backbone network 
        # (i.e., clock without splitter trees)
        file.write ("\n/* 1. Clock backbone network */\n\n")
        for depth_ in range (max_depth_):
            file.write ("/* Depth {} */\n\n".format (depth_))
            clk_conn_depth_ = clk_connection_df.iloc [depth_].to_dict ()
            ## insert BUFFTs
            if clk_conn_depth_["BUFFT_RSFQ"] != 0.0:
                num_buffers_ = int (clk_conn_depth_["BUFFT_RSFQ"])
                input_wire_ = intermediate_wires_.pop ()
                output_wires_ = gen_buffer (input_wire_, num_buffers_)
                intermediate_wires_ = intermediate_wires_ + output_wires_
            ## insert PTLs
            if clk_conn_depth_["PTL_RSFQ"] != 0.0:
                num_ptls_ = int (clk_conn_depth_["PTL_RSFQ"])
                input_wire_ = intermediate_wires_.pop ()
                output_wires_ = gen_ptl (input_wire_, num_ptls_)
                intermediate_wires_ = intermediate_wires_ + output_wires_
            ## insert Splitters
            input_wire_ = intermediate_wires_.pop ()
            output_wires_ = gen_splitter_tree (input_wire_, 2)
            clk_conn_table[depth_] = [output_wires_.pop ()]
            intermediate_wires_ = intermediate_wires_ + output_wires_
        # generate clock-splitter tree
        file.write ("\n/* 2. Clock splitter tree */\n\n")
        for depth_ in range (max_depth_):
            file.write ("/* Depth {} */\n\n".format (depth_))
            input_wire_ = clk_conn_table[depth_].pop ()
            output_wires_ = gen_splitter_tree (input_wire_, num_gates_[depth_])
            clk_conn_table[depth_] = output_wires_

    # network for counter-flow clocking
    elif clk_scheme == "counter":
        # generate the clock backbone network 
        # (i.e., clock without splitter trees)
        file.write ("/* 1. Clock backbone network */\n\n")
        for depth_ in reversed (range (max_depth_)):
            file.write ("/* Depth {} */\n\n".format (depth_))
            clk_conn_depth_ = clk_connection_df.iloc [depth_].to_dict ()
            ## insert Splitters
            input_wire_ = intermediate_wires_.pop ()
            output_wires_ = gen_splitter_tree (input_wire_, 2)
            clk_conn_table[depth_] = [output_wires_.pop ()]
            intermediate_wires_ = intermediate_wires_ + output_wires_
            ## insert BUFFTs
            if clk_conn_depth_["BUFFT_RSFQ"] != 0.0:
                num_buffers_ = int (clk_conn_depth_["BUFFT_RSFQ"])
                input_wire_ = intermediate_wires_.pop ()
                output_wires_ = gen_buffer (input_wire_, num_buffers_)
                intermediate_wires_ = intermediate_wires_ + output_wires_
            ## insert PTLs
            if clk_conn_depth_["PTL_RSFQ"] != 0.0:
                num_ptls_ = int (clk_conn_depth_["PTL_RSFQ"])
                input_wire_ = intermediate_wires_.pop ()
                output_wires_ = gen_ptl (input_wire_, num_ptls_)
                intermediate_wires_ = intermediate_wires_ + output_wires_
        # generate clock-splitter tree
        file.write ("/* 2. Clock splitter tree */\n\n")
        for depth_ in range (max_depth_):
            file.write ("/* Depth {} */\n\n".format (depth_))
            input_wire_ = clk_conn_table[depth_].pop ()
            output_wires_ = gen_splitter_tree (input_wire_, num_gates_[depth_])
            clk_conn_table[depth_] = output_wires_
    return


def gate_generation ():
    global file, gate_param_df, connection_df, num_wire
    global gate_conn_table
    
    gates_df_ = connection_df[connection_df["Type"].str.contains ("_RSFQ")].copy ()
    
    # declare logic gates
    file.write ("/*********************/\n")
    file.write ("/**** LOGIC GATES ****/\n")
    file.write ("/*********************/\n\n")

    intermediate_wires_ = list ()
    for i in range (len (gates_df_)):
        gate_ = gates_df_.iloc[i]
        is_two_input = gate_["A_type"] != "NaN" and (gate_["B_type"] != "NaN")
        conn_entry_ = dict ()

        file.write ("/* {} gate */\n\n".format (gate_["Type"]))

        # declare single-input gates
        if is_two_input == False:
            # declare input-A
            file.write ("wire _W{}_;\n\n".format (num_wire))
            intermediate_wires_.append (num_wire)
            conn_entry_["input1"] = num_wire
            conn_entry_["input2"] = None
            num_wire += 1
            # BUFFs and PTLs for input-A
            ## insert BUFFTs
            if gate_["A_buff"] != 0:
                num_buffers_ = int (gate_["A_buff"])
                input_wire_ = intermediate_wires_.pop ()
                output_wires_ = gen_buffer (input_wire_, num_buffers_)
                intermediate_wires_ = intermediate_wires_ + output_wires_
            ## insert PTLs
            if gate_["A_ptl"] != 0:
                num_ptls_ = int (gate_["A_ptl"])
                input_wire_ = intermediate_wires_.pop ()
                output_wires_ = gen_ptl (input_wire_, num_ptls_)
                intermediate_wires_ = intermediate_wires_ + output_wires_
            
            # declare gate
            input_1_ = intermediate_wires_.pop ()
            clk_ = clk_conn_table[int (gate_["Depth"])-1].pop ()
            output_ = num_wire
            conn_entry_["output"] = num_wire
            num_wire += 1
            file.write ("wire _W{}_;\n\n".format (output_))
            file.write ("{} {} (\n".format (gate_["Type"], gate_["Name"]))
            file.write ("\t.a(_W{}_),\n".format (input_1_))
            file.write ("\t.clk(_W{}_),\n".format (clk_))
            file.write ("\t.q(_W{}_)\n".format (output_))
            file.write (");\n\n")

        # declare two-input gates
        elif is_two_input == True:
            # declare input-A
            file.write ("wire _W{}_;\n\n".format (num_wire))
            intermediate_wires_.append (num_wire)
            conn_entry_["input1"] = num_wire
            num_wire += 1
            # BUFFs and PTLs for input-A
            ## insert BUFFTs
            if gate_["A_buff"] != 0:
                num_buffers_ = int (gate_["A_buff"])
                input_wire_ = intermediate_wires_.pop ()
                output_wires_ = gen_buffer (input_wire_, num_buffers_)
                intermediate_wires_ = intermediate_wires_ + output_wires_
            ## insert PTLs
            if gate_["A_ptl"] != 0:
                num_ptls_ = int (gate_["A_ptl"])
                input_wire_ = intermediate_wires_.pop ()
                output_wires_ = gen_ptl (input_wire_, num_ptls_)
                intermediate_wires_ = intermediate_wires_ + output_wires_
            input_1_ = intermediate_wires_.pop ()
            
            # declare input-B
            file.write ("wire _W{}_;\n\n".format (num_wire))
            intermediate_wires_.append (num_wire)
            conn_entry_["input2"] = num_wire
            num_wire += 1
            # BUFFs and PTLs for input-B
            ## insert BUFFTs
            if gate_["B_buff"] != 0:
                num_buffers_ = int (gate_["B_buff"])
                input_wire_ = intermediate_wires_.pop ()
                output_wires_ = gen_buffer (input_wire_, num_buffers_)
                intermediate_wires_ = intermediate_wires_ + output_wires_
            ## insert PTLs
            if gate_["B_ptl"] != 0:
                num_ptls_ = int (gate_["B_ptl"])
                input_wire_ = intermediate_wires_.pop ()
                output_wires_ = gen_ptl (input_wire_, num_ptls_)
                intermediate_wires_ = intermediate_wires_ + output_wires_
            input_2_ = intermediate_wires_.pop ()

            # declare gate
            clk_ = clk_conn_table[int (gate_["Depth"])-1].pop ()
            output_ = num_wire
            conn_entry_["output"] = num_wire
            num_wire += 1
            file.write ("wire _W{}_;\n\n".format (output_))
            file.write ("{} {} (\n".format (gate_["Type"], gate_["Name"]))
            file.write ("\t.a(_W{}_),\n".format (input_1_))
            file.write ("\t.b(_W{}_),\n".format (input_2_))
            file.write ("\t.clk(_W{}_),\n".format (clk_))
            file.write ("\t.q(_W{}_)\n".format (output_))
            file.write (");\n\n")
        # update the gate-connection table
        conn_entry_["in1_gate"] = gate_["A_name"]
        conn_entry_["in2_gate"] = gate_["B_name"]
        temp_ = pd.concat ([connection_df[connection_df["A_name"]==gate_["Name"]], \
            connection_df[connection_df["B_name"]==gate_["Name"]]])
        conn_entry_["out_gate"] = temp_["Name"].tolist ()
        gate_conn_table[gate_["Name"]] = conn_entry_
    return


def gate_connection ():
    global gate_conn_table, connection_df
    input_table = dict ()

    file.write ("/*************************/\n")
    file.write ("/**** GATE CONNECTION ****/\n")
    file.write ("/*************************/\n\n")
    
    print (pd.DataFrame.from_dict (gate_conn_table, orient="index"))

    # connect the output of each gate with the appropriate wires
    for name_ in gate_conn_table.keys ():
        file.write ("/* Connection for {} */\n\n".format (name_))
        intermediate_wires_ = list ()
        target_list_ = gate_conn_table[name_]["out_gate"]
        intermediate_wires_.append (gate_conn_table[name_]["output"])
        # need splitter tree for higher fanout
        if len (target_list_) > 1:
            input_wire_ = intermediate_wires_.pop ()
            output_wires_ = gen_splitter_tree (input_wire_, len (target_list_))
            intermediate_wires_ = intermediate_wires_ + output_wires_
        # connect the output with the target gates
        for target_gate_ in target_list_:
            src_ = None
            dst_ = None
            #print ("name:\t{}".format (target_gate_))
            # case1: output of the module
            if "_" not in target_gate_[0]:
                dst_ = "output_{}".format (target_gate_)
            # case2: connect with input-A
            elif gate_conn_table[target_gate_]["in1_gate"] == name_:
                dst_ = "_W{}_".format (int (gate_conn_table[target_gate_]["input1"]))
            # case3: connect with input-B
            elif gate_conn_table[target_gate_]["in2_gate"] == name_:
                dst_ = "_W{}_".format (int (gate_conn_table[target_gate_]["input2"]))
            src_ = "_W{}_".format (intermediate_wires_.pop ())
            file.write ("assign {} = {};\n\n".format (dst_, src_))
        # remove abundant wires generated by splitters
        del intermediate_wires_
    
        # if the gate is connected with input
        #if (("_" not in gate_conn_table[name_]["in1_gate"]) and \
        #    (gate_conn_table[name_]["in1_gate"] != "NaN")):
        #    dst_ = "_W{}_".format (int (gate_conn_table[name_]["input1"]))
        #    src_ = "input_{}".format (gate_conn_table[name_]["in1_gate"])
        #    file.write ("assign {} = {};\n\n".format (dst_, src_))
        #if (("_" not in gate_conn_table[name_]["in2_gate"]) and \
        #    (gate_conn_table[name_]["in2_gate"] != "NaN")):
        #    dst_ = "_W{}_".format (int (gate_conn_table[name_]["input2"]))
        #    src_ = "input_{}".format (gate_conn_table[name_]["in2_gate"])
        #    file.write ("assign {} = {};\n\n".format (dst_, src_))
    
        if (("_" not in gate_conn_table[name_]["in1_gate"][0]) and \
            (gate_conn_table[name_]["in1_gate"] != "NaN")):
            input_ = gate_conn_table[name_]["in1_gate"]
            if input_ not in input_table:
                input_table[input_] = list ()
            input_table[input_].append (name_)
        if (("_" not in gate_conn_table[name_]["in2_gate"][0]) and \
            (gate_conn_table[name_]["in2_gate"] != "NaN")):
            input_ = gate_conn_table[name_]["in2_gate"]
            if input_ not in input_table:
                input_table[input_] = list ()
            input_table[input_].append (name_)
    
    print (input_table)
    # connect the inputs to the appropriate wires
    for name_ in input_table.keys ():
        file.write ("/* Connection for input_{} */\n\n".format (name_))
        intermediate_wires_ = list ()
        target_list_ = input_table[name_]
        intermediate_wires_.append ("input_{}".format (name_))
        # need splitter tree for higher fanout
        if len (target_list_) > 1:
            input_wire_ = intermediate_wires_.pop ()
            output_wires_ = gen_splitter_tree (input_wire_, len (target_list_))
            intermediate_wires_ = intermediate_wires_ + output_wires_
        # connect the output with the target gates
        for target_gate_ in target_list_:
            src_ = None
            dst_ = None
            # case1: connect with input-A
            if gate_conn_table[target_gate_]["in1_gate"] == name_:
                dst_ = "_W{}_".format (int (gate_conn_table[target_gate_]["input1"]))
            # case2: connect with input-B
            elif gate_conn_table[target_gate_]["in2_gate"] == name_:
                dst_ = "_W{}_".format (int (gate_conn_table[target_gate_]["input2"]))
            
            src_ = intermediate_wires_.pop ()
            if "int" in str (type (src_)):
                src_ = "_W{}_".format (src_)
            file.write ("assign {} = {};\n\n".format (dst_, src_))
        # remove abundant wires generated by splitters
        del intermediate_wires_
    

    return


def gen_splitter_tree (input_wire, num_fanout):
    global num_wire, num_splitter
    # find the depth of splitter tree
    depth_ = 0
    for i in range (1,1000):
        if 2**i >= num_fanout:
            depth_ = i
            break
    # declare splitter tree
    intermediate_wires_ = list ()
    intermediate_wires_.append (input_wire)
    file.write ("/* Fanout-{} splitter tree */\n\n".format (2**depth_))
    for i in range (depth_):
        next_wires_ = list ()
        for j in range (2**i):
            input_ = intermediate_wires_.pop ()
            output_1_ = num_wire
            output_2_ = num_wire + 1
            file.write ("wire _W{}_;\n\n".format (output_1_))
            file.write ("wire _W{}_;\n\n".format (output_2_))
            file.write ("SPLITT_RSFQ _SPLITT_{}_ (\n".format (num_splitter))
            if "input_" not in str (input_):
                file.write ("\t.a(_W{}_),\n".format (input_))
            else:
                file.write ("\t.a({}),\n".format (input_))
            file.write ("\t.q0(_W{}_),\n".format (output_1_))
            file.write ("\t.q1(_W{}_)\n".format (output_2_))
            file.write (");\n\n")
            num_wire += 2
            num_splitter += 1
            next_wires_.append (output_1_)
            next_wires_.append (output_2_)
        intermediate_wires_ = next_wires_
    # return output wires
    return intermediate_wires_


def gen_buffer (input_wire, num_buffers):
    global num_wire, num_buffer
    intermediate_wires_ = list ()
    intermediate_wires_.append (input_wire)
    file.write ("/* Depth-{} buffers */\n\n".format (num_buffers))
    for i in range (num_buffers):
        input_ = intermediate_wires_.pop ()
        output_ = num_wire
        file.write ("wire _W{}_;\n\n".format (output_))
        file.write ("BUFFT_RSFQ _BUFFT_{}_ (\n".format (num_buffer))
        if "input_" not in str (input_):
            file.write ("\t.a(_W{}_),\n".format (input_))
        else:
            file.write ("\t.a({}),\n".format (input_))
        file.write ("\t.q(_W{}_)\n".format (output_))
        file.write (");\n\n")
        num_wire += 1
        num_buffer += 1
        intermediate_wires_.append (output_)
    # return output wires
    return intermediate_wires_


def gen_ptl (input_wire, num_ptls):
    global num_wire, num_ptl
    intermediate_wires_ = list ()
    intermediate_wires_.append (input_wire)
    file.write ("/* Depth-{} PTLs */\n".format (num_ptls))
    for i in range (num_ptls):
        input_ = intermediate_wires_.pop ()
        output_ = num_wire
        file.write ("wire _W{}_;\n\n".format (output_))
        file.write ("PTL_RSFQ _PTL_{}_ (\n".format (num_ptl))
        if "input_" not in str (input_):
            file.write ("\t.a(_W{}_),\n".format (input_))
        else:
            file.write ("\t.a({}),\n".format (input_))
        file.write ("\t.q(_W{}_)\n".format (output_))
        file.write (");\n\n")
        num_wire += 1
        num_ptl += 1
        intermediate_wires_.append (output_)
    # return output wires
    return intermediate_wires_


def main (argv):
    initial_setup ()
    start_module ()
    clock_generation ()
    gate_generation ()
    gate_connection ()
    end_module ()


if __name__ == "__main__":
    app.run (main)


