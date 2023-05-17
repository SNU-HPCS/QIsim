import pandas as pd
from math import *
from absl import flags
from absl import app
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

FLAGS = flags.FLAGS
flags.DEFINE_integer ("b", 8, "# of broadcasted bitstreams (=BS)")
flags.DEFINE_integer ("g", 2, "# of groups")
flags.DEFINE_integer ("q", 1024, "# of qubits")
flags.DEFINE_integer ("y", 272, "Length of bitstream; y-length")
flags.DEFINE_integer ("z", 256, "# of bitstreams; z-length")
flags.DEFINE_integer ("l", 1200, "Two-qubit gate length; clock period *l")
flags.DEFINE_integer ("t", 5, "q2_sel per qubit")
flags.DEFINE_integer ("c", 32, "ctrl_data cable width")

flags.DEFINE_boolean ("m", False, "readout using mux [True] or shifter [False]")

gate_library = "mitll_param.csv"

class digiq_hardware:

    # User inputs.
    bs = None
    num_group = None
    num_qubit = None
    y_length = None
    z_length = None
    q2_length = None
    q2sel_width = None
    ctrl_width = None
    readout_mux = None

    # DigiQ units
    buffer1 = list ()
    buffer2 = list ()
    controller = list ()
    bitgen = list ()
    bitgen_controller = list ()
    drive_mux = list ()
    pulse_sfqdc = list ()
    pulse_bitgen = list ()
    pulse_controller = list ()
    readout = list ()
    jpm_readout = list ()

    # intermediate
    buffer1_size = None
    buffer2_size = None
    select_size = None  # sum of q1/q2_sel bits.
    digiq = None


    def __init__ (self, bs, num_group, num_qubit, y_length, z_length, q2_length, q2sel_width, ctrl_width, is_readmux):
        self.bs = bs
        self.num_group = num_group
        self.num_qubit = num_qubit
        self.y_length = y_length
        self.z_length = z_length
        self.q2_length = q2_length
        self.q2sel_width = q2sel_width
        self.ctrl_width = ctrl_width
        self.readout_mux = is_readmux
    
        self.gen_buffer1 ()
        self.gen_buffer2 ()
        #self.gen_bitgen () # Opt-4.
        self.gen_bitgen_baseline () # Baseline.
        # it requires too much time for simulation even with negligible power.
        # self.gen_bitgen_ctrl ()
        self.gen_drive_mux ()
        self.gen_pulse_ctrl ()
        self.gen_pulse_sfqdc ()
        self.gen_controller ()
        self.gen_readout ()
        self.gen_jpm_readout_baseline ()


    # Buffer1 for 1Q/2Q gates.
    def gen_buffer1 (self):
        data_size = log2 (self.z_length) * self.bs
        sel_size = (log2 (self.bs) + 1) * self.num_qubit # including per-bit mask for CZ gates.
        data_size += sel_size
        self.buffer1_size = data_size
        self.buffer2_size = data_size
        self.select_size = sel_size

        width = self.ctrl_width
        length = ceil (self.buffer1_size / self.ctrl_width)
        buffer1_file = "final_csv/buffer1_{}width_{}length_fpa.csv".format (1, length)

        print ("\n\n1. Buffer1.")
        if not os.path.isfile (buffer1_file):
            print ("\tNo {}.".format (buffer1_file))
            un = "buffer1_{}width_{}length".format (1, length)
            bd = "unit_csv/" + un + "_breakdown.csv"
            cn = "unit_csv/" + un + "_connection.csv"
            print ("\tCall buffer1.py...")
            os.system ("python buffer1.py -w {} -l {}".format (1, length))
            print ("\tCall sfq_unit_model.py...")
            os.system ("python sfq_unit_model.py -cn {} -bd {} -un {} -tn 0".format (cn, bd, un))
        self.buffer1 = pd.read_csv (buffer1_file)
        self.buffer1["Name"] = "Buffer1"
        self.buffer1["Units"] = width * self.num_group
        print (self.buffer1)
        return


    # Buffer2 for 1Q/2Q gates.
    def gen_buffer2 (self):
        data_bits = int (self.buffer2_size)
        buffer2_file = "final_csv/buffer2_{}data_fpa.csv".format (1)

        print ("\n\n2. Buffer2.")
        if not os.path.isfile (buffer2_file):
            print ("\tNo {}".format (buffer2_file))
            un = "buffer2_{}data".format (1)
            bd = "unit_csv/" + un + "_breakdown.csv"
            cn = "unit_csv/" + un + "_connection.csv"
            print ("\tCall buffer2.py...")
            os.system ("python buffer2.py -d {}".format (1))
            print ("\tCall sfq_unit_model.py...")
            os.system ("python sfq_unit_model.py -cn {} -bd {} -un {} -tn 0".format (cn, bd, un))
        self.buffer2 = pd.read_csv (buffer2_file)
        self.buffer2["Name"] = "Buffer2"
        self.buffer2["Units"] = data_bits
        print (self.buffer2)
        return


    # Optimized Bitstream generator in the drive circuit (Opt#4).
    def gen_bitgen (self):
        y = self.y_length
        z = self.z_length
        bitgen_file = "final_csv/bitgen_{}y_{}z_fpa.csv".format (y, z)

        print ("\n\n3. Bitgen.")
        if not os.path.isfile (bitgen_file):
            print ("\tNo {}".format (bitgen_file))
            un = "bitgen_{}y_{}z".format (y, z)
            bd = "unit_csv/" + un + "_breakdown.csv"
            cn = "unit_csv/" + un + "_connection.csv"
            print ("\tCall bitgen.py...")
            os.system ("python bitgen.py -ly {} -lz {}".format (y, z))
            print ("\tCall sfq_unit_model.py...")
            os.system ("python sfq_unit_model.py -cn {} -bd {} -un {} -clk counter".format (cn, bd, un))
        self.bitgen = pd.read_csv (bitgen_file)
        self.bitgen["Name"] = "Bitgen"
        self.bitgen["Units"] = self.num_group
        print (self.bitgen)
        return


    # Baseline Bitstream generator in the drive circuit.
    def gen_bitgen_baseline (self):
        y = self.y_length
        z = self.z_length
        print ("\n\n3. Bitgen (Baseline).")
        ybitgen_file = "final_csv/bitgen_readout_{}_fpa.csv".format (y+z)

        # 1. Y_bitgen.
        if not os.path.isfile (ybitgen_file):
            print ("\tNo {}".format (ybitgen_file))
            un = "bitgen_readout_{}".format (y+z)
            bd = "unit_csv/" + un + "_breakdown.csv"
            cn = "unit_csv/" + un + "_connection.csv"
            print ("\tCall bitgen_readout.py...")
            os.system ("python bitgen_readout.py -ly {}".format (y+z))
            print ("\tCall sfq_unit_model.py...")
            os.system ("python sfq_unit_model.py -cn {} -bd {} -un {} -clk counter".format (cn, bd, un))
        self.bitgen = pd.read_csv (ybitgen_file)
        frequency = self.bitgen["Frequency"].item ()
        
        # 2. Z_bitgen.
        for z_ in range (1, z+1):
            zbitgen_file = "final_csv/buffer1_{}width_{}length_fpa.csv".format (1, z_)
            if not os.path.isfile (zbitgen_file):
                print ("\tNo {}.".format (zbitgen_file))
                un = "buffer1_{}width_{}length".format (1, z_)
                bd = "unit_csv/" + un + "_breakdown.csv"
                cn = "unit_csv/" + un + "_connection.csv"
                print ("\tCall buffer1.py...")
                os.system ("python buffer1.py -w {} -l {}".format (1, z_))
                print ("\tCall sfq_unit_model.py...")
                os.system ("python sfq_unit_model.py -cn {} -bd {} -un {} -tn 0".format (cn, bd, un))
            zbitgen = pd.read_csv (zbitgen_file)
            self.bitgen = self.bitgen.add (zbitgen, fill_value=0)
        self.bitgen["Frequency"] = frequency

        # 3. Splitter tree between y_bitgen and z_bitgen.
        num_split = z

        # Sum up.
        gate_param_df = pd.read_csv (gate_library).set_index ("Name")
        self.bitgen["PowerStatic"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "PowerStatic"]
        self.bitgen["EnergyDynamic"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "EnergyDynamic"]
        self.bitgen["Area"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "Area"]
        self.bitgen["Name"] = "Bitgen"
        self.bitgen["Units"] = self.num_group
        print (self.bitgen)
        return


    # Bitstream-generator controller for Drive circuit.
    def gen_bitgen_ctrl (self):
        data_bits = self.y_length + self.z_length
        bitgen_ctrl_file = "final_csv/bitgenctrl_{}_fpa.csv".format (data_bits)

        print ("\n\n4. Bitgen controller.")
        if not os.path.isfile (bitgen_ctrl_file):
            print ("\tNo {}".format (bitgen_ctrl_file))
            un = "bitgenctrl_{}".format (data_bits)
            bd = "unit_csv/" + un + "_breakdown.csv"
            cn = "unit_csv/" + un + "_connection.csv"
            print ("\tCall bitgen.py...")
            os.system ("python bitgen_ctrl.py -l {}".format (data_bits))
            print ("\tCall sfq_unit_model.py...")
            os.system ("python sfq_unit_model.py -cn {} -bd {} -un {}".format (cn, bd, un))
        self.bitgen_controller = pd.read_csv (bitgen_ctrl_file)
        self.bitgen_controller["Name"] = "Bitgen controller"
        self.bitgen_controller["Units"] = 1
        print (self.bitgen_controller)
        return


    # Per-qubit controller (i.e., #BS+1:1 MUX) for Drive circuit.
    def gen_drive_mux (self):
        input_bits = self.bs
        select_bits = ceil (log2 (self.bs))
        output_bits = 1
        drivemux_file = "final_csv/mux_{}_{}_{}_fpa.csv".format (input_bits, select_bits, output_bits)

        print ("\n\n5. Drivemux.")
        if not os.path.isfile (drivemux_file):
            print ("\tNo {}".format (drivemux_file))
            un = "mux_{}_{}_{}".format (input_bits, select_bits, output_bits)
            bd = "unit_csv/" + un + "_breakdown.csv"
            cn = "unit_csv/" + un + "_connection.csv"
            print ("\tCall drive_mux.py...")
            os.system ("python drive_mux.py -i {} -s {} -o {}".format (input_bits, select_bits, output_bits))
            print ("\tCall sfq_unit_model.py...")
            os.system ("python sfq_unit_model.py -cn {} -bd {} -un {}".format (cn, bd, un))
        self.drive_mux = pd.read_csv (drivemux_file)
        self.drive_mux["Name"] = "Drive mux"
        self.drive_mux["Units"] = self.num_qubit
        print (self.drive_mux)
        return


    # SFQDC controller for Pulse circuit.
    def gen_pulse_ctrl (self):
        length = self.q2_length
        pulsectrl_file = "final_csv/pulsectrl_{}_fpa.csv".format (length)

        print ("\n\n6. Pulsectrl.")

        #1. Calculate the overhead of shift registers.
        pulsectrl_file = "final_csv/bitgen_readout_{}_fpa.csv".format (length)
        if not os.path.isfile (pulsectrl_file):
            print ("\tNo {}".format (pulsectrl_file))
            un = "bitgen_readout_{}".format (length)
            bd = "unit_csv/" + un + "_breakdown.csv"
            cn = "unit_csv/" + un + "_connection.csv"
            print ("\tCall bitgen_readout.py...")
            os.system ("python bitgen_readout.py -ly {}".format (length))
            print ("\tCall sfq_unit_model.py...")
            os.system ("python sfq_unit_model.py -cn {} -bd {} -un {} -clk counter".format (cn, bd, un))
        self.pulse_controller = pd.read_csv (pulsectrl_file)
        self.pulse_controller["PowerStatic"] *= self.q2sel_width*4
        self.pulse_controller["EnergyDynamic"] *= self.q2sel_width*4
        self.pulse_controller["Area"] *= self.q2sel_width*4

        #2. Calculate the overhead of 4:1 MUX.
        mux_file = "final_csv/mux_4_2_1_fpa.csv"
        if not os.path.isfile (mux_file):
            print ("\tNo {}".format (mux_file))
            un = "mux_4_2_1"
            bd = "unit_csv/" + un + "_breakdown.csv"
            cn = "unit_csv/" + un + "_connection.csv"
            print ("\tCall drive_mux.py...")
            os.system ("python drive_mux.py -i 4 -s 2 -o 1")
            print ("\tCall sfq_unit_model.py...")
            os.system ("python sfq_unit_model.py -cn {} -bd {} -un {}".format (cn, bd, un))
        mux_df = pd.read_csv (mux_file)
        self.pulse_controller["PowerStatic"] += mux_df["PowerStatic"]*4*self.q2sel_width
        self.pulse_controller["EnergyDynamic"] += mux_df["EnergyDynamic"]*4*self.q2sel_width
        self.pulse_controller["Area"] += mux_df["Area"]*4*self.q2sel_width

        #3. Calculate the overhead of splitter trees.
        qubits = ceil (self.num_qubit / self.num_group)
        split_depth = ceil(log2(qubits))
        num_split = (2**split_depth-1)*self.q2sel_width + 3*4*self.q2sel_width
        gate_param_df = pd.read_csv (gate_library).set_index ("Name")
        self.pulse_controller["PowerStatic"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "PowerStatic"]
        self.pulse_controller["EnergyDynamic"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "EnergyDynamic"]
        self.pulse_controller["Area"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "Area"]
        
        self.pulse_controller["Name"] = "Pulse controller"
        self.pulse_controller["Units"] = self.num_group
        print (self.pulse_controller)
        return


    def gen_pulse_sfqdc (self):
        q2sel_width = self.q2sel_width
        sfqdc_file = "final_csv/sfqdc_{}_fpa.csv".format (q2sel_width)

        print ("\n\n7. sfqdc.")

        #1. SFQDC controller part (AND gates).
        # (SFQDC is not included because it does not require clocks)
        if not os.path.isfile (sfqdc_file):
            print ("\tNo {}".format (sfqdc_file))
            un = "sfqdc_{}".format (q2sel_width)
            bd = "unit_csv/" + un + "_breakdown.csv"
            cn = "unit_csv/" + un + "_connection.csv"
            print ("\tCall sfqdc.py...")
            os.system ("python sfqdc.py -n {}".format (q2sel_width))
            print ("\tCall sfq_unit_model.py...")
            os.system ("python sfq_unit_model.py -cn {} -bd {} -un {}".format (cn, bd, un))
        pulse_sfqdc = pd.read_csv (sfqdc_file)
        
        #2. SFQDC (Analytic model).
        num_split = 0
        num_sfqdc = 0
        for width_ in range (q2sel_width):
            num_split += width_
            num_sfqdc += 2**width_
        gate_param_df = pd.read_csv (gate_library).set_index ("Name")
        pulse_sfqdc["PowerStatic"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "PowerStatic"]
        pulse_sfqdc["PowerStatic"] += num_sfqdc*gate_param_df.loc["SFQDC", "PowerStatic"]
        pulse_sfqdc["EnergyDynamic"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "EnergyDynamic"]
        pulse_sfqdc["EnergyDynamic"] += num_sfqdc*gate_param_df.loc["SFQDC", "EnergyDynamic"]
        pulse_sfqdc["Area"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "Area"]
        pulse_sfqdc["Area"] += num_sfqdc*gate_param_df.loc["SFQDC", "Area"]
        
        self.pulse_sfqdc = pulse_sfqdc
        self.pulse_sfqdc["Name"] = "SFQDC"
        self.pulse_sfqdc["Units"] = self.num_qubit
        print (self.pulse_sfqdc)
        return


    # Bitstream controller for Drive circuit.
    def gen_controller (self):
        bs = self.bs
        z = self.z_length
        controller_file = "final_csv/controller_{}_{}_fpa.csv".format (bs, z)
        
        #1. Verilog-defined controller.
        print ("\n\n8. Controller.")
        if not os.path.isfile (controller_file):
            print ("\tNo {}".format (controller_file))
            un = "controller_{}_{}".format (bs, z)
            bd = "unit_csv/" + un + "_breakdown.csv"
            cn = "unit_csv/" + un + "_connection.csv"
            print ("\tCall controller.py...")
            os.system ("python controller.py -b {} -n {}".format (bs, z))
            print ("\tCall sfq_unit_model.py...")
            os.system ("python sfq_unit_model.py -cn {} -bd {} -un {}".format (cn, bd, un))
        controller_df = pd.read_csv (controller_file)

        #2. Splitter trees for bitstreams (Analytic model)
        qubits = ceil (self.num_qubit / self.num_group)
        split_depth = ceil(log2(qubits))
        num_split = (2**split_depth-1)*self.bs
        # counting splitter for 2q_gate here.
        num_split += (2**split_depth-1)*self.q2sel_width

        #3. DFFs for aligning q1_sel and q2_sel (Analytic model)
        sel_size = self.select_size/self.num_group
        conn = pd.read_csv ("final_csv/controller_{}_{}_connection_final.csv".format (bs,z))
        depth = int (conn["Depth"].max ())
        num_dff = sel_size * depth
        num_split += 2**(ceil(log2(sel_size))) * depth

        #4. Buffers for timing adjustment due to splitter tree (Analytic model)
        num_buff = sel_size * split_depth

        # Sum up.
        gate_param_df = pd.read_csv (gate_library).set_index ("Name")
        controller_df["PowerStatic"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "PowerStatic"]
        controller_df["EnergyDynamic"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "EnergyDynamic"]
        controller_df["Area"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "Area"]

        controller_df["PowerStatic"] += num_dff*gate_param_df.loc["DFFT_RSFQ", "PowerStatic"]
        controller_df["EnergyDynamic"] += num_dff*gate_param_df.loc["DFFT_RSFQ", "EnergyDynamic"]
        controller_df["Area"] += num_dff*gate_param_df.loc["DFFT_RSFQ", "Area"]

        controller_df["PowerStatic"] += num_buff*gate_param_df.loc["BUFFT_RSFQ", "PowerStatic"]
        controller_df["EnergyDynamic"] += num_buff*gate_param_df.loc["BUFFT_RSFQ", "EnergyDynamic"]
        controller_df["Area"] += num_buff*gate_param_df.loc["BUFFT_RSFQ", "Area"]

        self.controller = controller_df
        self.controller["Name"] = "Controller"
        self.controller["Units"] = self.num_group
        print (self.controller)
        return


    # Readout circuit.
    def gen_readout (self):
            
        print ("\n\n9. Readout circuits")

        #1. Buffer1 for Resonator-drive, JPM-pulse and JPM-readout circuits (aggregated).
        data_size = ceil (self.num_qubit/self.num_group * (3+self.q2sel_width))
        buffer1_file = "final_csv/buffer1_{}width_{}length_fpa.csv".format (1, ceil (data_size))
        if not os.path.isfile (buffer1_file):
            print ("\tNo {}.".format (buffer1_file))
            un = "buffer1_{}width_{}length".format (1, ceil (data_size))
            bd = "unit_csv/" + un + "_breakdown.csv"
            cn = "unit_csv/" + un + "_connection.csv"
            print ("\tCall buffer1.py...")
            os.system ("python buffer1.py -w {} -l {}".format (1, ceil(data_size)))
            print ("\tCall sfq_unit_model.py...")
            os.system ("python sfq_unit_model.py -cn {} -bd {} -un {} -tn 0".format (cn, bd, un))
        buffer1_readout = pd.read_csv (buffer1_file)
        #print ("\n 9-1. Buffer1 for readout.")
        #print (buffer1_readout)

        #2. Buffer2 for Resonator-drive circuits.
        buffer2_file = "final_csv/buffer2_{}data_fpa.csv".format (1)
        if not os.path.isfile (buffer2_file):
            print ("\tNo {}".format (buffer2_file))
            un = "buffer2_{}data".format (1)
            bd = "unit_csv/" + un + "_breakdown.csv"
            cn = "unit_csv/" + un + "_connection.csv"
            print ("\tCall buffer2.py...")
            os.system ("python buffer2.py -d {}".format (1))
            print ("\tCall sfq_unit_model.py...")
            os.system ("python sfq_unit_model.py -cn {} -bd {} -un {} -tn 0".format (cn, bd, un))
        buffer2 = pd.read_csv (buffer2_file)
        #print ("\n 9-2. Buffer 2 for readout.")
        #print (buffer2)
        
        #3. Bitstream generator for Resonator driving.
        data_bits = 4
        bitgen_file = "final_csv/bitgen_readout_{}_fpa.csv".format (data_bits)
        if not os.path.isfile (bitgen_file):
            print ("\tNo {}".format (bitgen_file))
            un = "bitgen_readout_{}".format (data_bits)
            bd = "unit_csv/" + un + "_breakdown.csv"
            cn = "unit_csv/" + un + "_connection.csv"
            print ("\tCall bitgen_readout.py...")
            os.system ("python bitgen_readout.py -ly {}".format (data_bits))
            print ("\tCall sfq_unit_model.py...")
            os.system ("python sfq_unit_model.py -cn {} -bd {} -un {} -clk counter".format (cn, bd, un))
        bitgen_readout = pd.read_csv (bitgen_file)
        #print ("\n 9-3. Readout bitgen.")
        #print (bitgen_readout)

        #4. SFQDC for JPM pulse circuit.
        # SFQDC Controller
        q2sel_width = self.q2sel_width
        sfqdc_file = "final_csv/sfqdc_{}_fpa.csv".format (q2sel_width)
        if not os.path.isfile (sfqdc_file):
            print ("\tNo {}".format (sfqdc_file))
            un = "sfqdc_{}".format (q2sel_width)
            bd = "unit_csv/" + un + "_breakdown.csv"
            cn = "unit_csv/" + un + "_connection.csv"
            print ("\tCall sfqdc.py...")
            os.system ("python sfqdc.py -n {}".format (q2sel_width))
            print ("\tCall sfq_unit_model.py...")
            os.system ("python sfq_unit_model.py -cn {} -bd {} -un {}".format (cn, bd, un))
        pulse_sfqdc = pd.read_csv (sfqdc_file)

        # SFQDC (Analytic model).
        num_sfqdc = 0
        for width_ in range (q2sel_width):
            num_sfqdc += 2**width_
        gate_param_df = pd.read_csv (gate_library).set_index ("Name")
        pulse_sfqdc["PowerStatic"] += num_sfqdc*gate_param_df.loc["SFQDC", "PowerStatic"]
        pulse_sfqdc["EnergyDynamic"] += num_sfqdc*gate_param_df.loc["SFQDC", "EnergyDynamic"]
        pulse_sfqdc["Area"] += num_sfqdc*gate_param_df.loc["SFQDC", "Area"]
        #print ("\n 9-4. Readout SFQDC")
        #print (pulse_sfqdc)

        #5. Other small units inside Readout circuits (Analytic model).
        # (1) DFF-based Buffer2 inside JPM pulse and JPM readout circuits.
        num_dff = self.num_qubit/self.num_group * (2+self.q2sel_width)
        # (2) Splitter trees for Resonator drive circuit (i.e., bitstream & clock for per-qubit AND)
        #     and JPM pulse and JPM readout circuits (i.e., clock for DFF buffers).
        qubits = ceil (self.num_qubit / self.num_group)
        num_split = (qubits-1)*5
        # (3) AND inside Resonator drive circuit.
        num_and = (self.num_qubit/self.num_group)*(1+self.q2sel_width+1)
        # (4) SFQDC inside TX.
        num_sfqdc = (self.num_qubit/self.num_group)
        # (5) DCSFQ inside RX.
        num_dcsfq = (self.num_qubit/self.num_group)

        readout_etc = pd.read_csv (sfqdc_file) # Read anything.
        readout_etc["Frequency"] = None
        readout_etc["PowerStatic"] = (num_dff*gate_param_df.loc["DFFT_RSFQ", "PowerStatic"] + num_split*gate_param_df.loc["SPLITT_RSFQ", "PowerStatic"] \
                                    + num_and*gate_param_df.loc["ANDT_RSFQ", "PowerStatic"] + num_sfqdc*gate_param_df.loc["SFQDC", "PowerStatic"] \
                                    + num_dcsfq*gate_param_df.loc["DCSFQ", "PowerStatic"]).item ()
        readout_etc["EnergyDynamic"] = num_dff*gate_param_df.loc["DFFT_RSFQ", "EnergyDynamic"] + num_split*gate_param_df.loc["SPLITT_RSFQ", "EnergyDynamic"] \
                                    + num_and*gate_param_df.loc["ANDT_RSFQ", "EnergyDynamic"] + num_sfqdc*gate_param_df.loc["SFQDC", "EnergyDynamic"] \
                                    + num_dcsfq*gate_param_df.loc["DCSFQ", "EnergyDynamic"]
        readout_etc["Area"] = num_dff*gate_param_df.loc["DFFT_RSFQ", "Area"] + num_split*gate_param_df.loc["SPLITT_RSFQ", "Area"] + num_and*gate_param_df.loc["ANDT_RSFQ", "Area"] \
                            + num_sfqdc*gate_param_df.loc["SFQDC", "Area"] + num_dcsfq*gate_param_df.loc["DCSFQ", "Area"]
        #print ("\n 9-5. Readout others")
        #print (readout_etc)

        # Sum up.
        self.readout = pd.read_csv (sfqdc_file) # Read anything.
        self.readout["Frequency"] = min ([buffer1_readout["Frequency"].item (), buffer2["Frequency"].item (), bitgen_readout["Frequency"].item (), pulse_sfqdc["Frequency"].item ()])
        self.readout["PowerStatic"] = buffer1_readout["PowerStatic"] + buffer2["PowerStatic"]*(self.num_qubit/self.num_group) + bitgen_readout["PowerStatic"] + pulse_sfqdc["PowerStatic"]*(self.num_qubit/self.num_group) + readout_etc["PowerStatic"]
        self.readout["EnergyDynamic"] = buffer1_readout["EnergyDynamic"] + buffer2["EnergyDynamic"]*(self.num_qubit/self.num_group) + bitgen_readout["EnergyDynamic"] + pulse_sfqdc["EnergyDynamic"]*(self.num_qubit/self.num_group) + readout_etc["EnergyDynamic"]
        self.readout["Area"] = buffer1_readout["Area"] + buffer2["Area"]*(self.num_qubit/self.num_group) + bitgen_readout["Area"] + pulse_sfqdc["Area"]*(self.num_qubit/self.num_group) + readout_etc["Area"]
        self.readout["Name"] = "Readout"
        self.readout["Units"] = self.num_group
        #print ("\nTotal 4K readout")
        print (self.readout)
        return


    def gen_jpm_readout_baseline (self):

        print ("\n\n10. mK-located JPM-readout circuits")

        # Analytic model.
        num_dcsfq = 2
        num_sfqdc = 1
        num_merge = 2
        num_split = 1
        num_dff = 1
        num_ljj = 11*2 # two side
        gate_param_df = pd.read_csv (gate_library).set_index ("Name")
        file = "final_csv/sfqdc_{}_fpa.csv".format (self.q2sel_width) # Read anything.
        bitgen_readout = pd.read_csv (file)

        bitgen_readout["Frequency"] = None

        bitgen_readout["PowerStatic"] = num_dcsfq*gate_param_df.loc["DCSFQ", "PowerStatic"]
        bitgen_readout["PowerStatic"] += num_sfqdc*gate_param_df.loc["SFQDC", "PowerStatic"]
        bitgen_readout["PowerStatic"] += num_merge*gate_param_df.loc["MERGET_RSFQ", "PowerStatic"]
        bitgen_readout["PowerStatic"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "PowerStatic"]
        bitgen_readout["PowerStatic"] += num_dff*gate_param_df.loc["DFFT_RSFQ", "PowerStatic"]

        bitgen_readout["EnergyDynamic"] = num_dcsfq*gate_param_df.loc["DCSFQ", "EnergyDynamic"]
        bitgen_readout["EnergyDynamic"] += num_sfqdc*gate_param_df.loc["SFQDC", "EnergyDynamic"]
        bitgen_readout["EnergyDynamic"] += num_merge*gate_param_df.loc["MERGET_RSFQ", "EnergyDynamic"]
        bitgen_readout["EnergyDynamic"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "EnergyDynamic"]
        bitgen_readout["EnergyDynamic"] += num_dff*gate_param_df.loc["DFFT_RSFQ", "EnergyDynamic"]
        bitgen_readout["EnergyDynamic"] += num_ljj*gate_param_df.loc["JTLT_RSFQ", "EnergyDynamic"]

        bitgen_readout["Area"] = num_dcsfq*gate_param_df.loc["DCSFQ", "Area"]
        bitgen_readout["Area"] += num_sfqdc*gate_param_df.loc["SFQDC", "Area"]
        bitgen_readout["Area"] += num_merge*gate_param_df.loc["MERGET_RSFQ", "Area"]
        bitgen_readout["Area"] += num_split*gate_param_df.loc["SPLITT_RSFQ", "Area"]
        bitgen_readout["Area"] += num_dff*gate_param_df.loc["DFFT_RSFQ", "Area"]
        bitgen_readout["Area"] += num_ljj*gate_param_df.loc["JTLT_RSFQ", "Area"]
        pd.DataFrame.from_dict (bitgen_readout)

        # Applying 1/100x Ic scaling over 4K RSFQ.
        bitgen_readout["EnergyDynamic"] *= 1/100
        bitgen_readout["PowerStatic"] *= 1/100

        self.jpm_readout = bitgen_readout
        self.jpm_readout["Name"] = "JPM_Readout"
        self.jpm_readout["Units"] = self.num_qubit
        print (self.jpm_readout)
        return


    def summary (self):
        digiq = pd.DataFrame (None, columns=["Frequency", "PowerStatic", "EnergyDynamic", "Area"])
        digiq = digiq.append (self.buffer1, ignore_index=True)
        digiq = digiq.append (self.buffer2, ignore_index=True)
        digiq = digiq.append (self.controller, ignore_index=True)
        digiq = digiq.append (self.bitgen, ignore_index=True)
        # digiq = digiq.append (self.bitgen_controller, ignore_index=True)
        digiq = digiq.append (self.drive_mux, ignore_index=True)
        digiq = digiq.append (self.pulse_sfqdc, ignore_index=True)
        digiq = digiq.append (self.pulse_controller, ignore_index=True)
        digiq = digiq.append (self.readout, ignore_index=True)
        digiq = digiq.set_index ("Name")

        frequency = digiq["Frequency"].min ()
        static = (digiq["PowerStatic"] * digiq["Units"]).sum ()
        dynamic = (digiq["EnergyDynamic"] * digiq["Units"]).sum () * frequency
        total_power = static + dynamic
        area = (digiq["Area"] * digiq["Units"]).sum ()

        print ("\n\n[DigiQ Summary]")
        print ("Maximum frequency:\t{}\t\t[GHz]".format (frequency))
        print ("Total power:\t\t{0:.1f}\t[nW]".format (total_power))
        print ("\tStatic power:\t{0:.1f}\t[nW]".format (static))
        print ("\tDynamic power:\t{0:.1f}\t[nW]".format (dynamic))
        print ("Area:\t\t\t{}\t[um^2]\n".format (area))

        
        digiq["Power [%]"] = (digiq["PowerStatic"] + digiq["EnergyDynamic"]*frequency) * digiq["Units"] \
                              /total_power * 100
        digiq["Area [%]"] = (digiq["Area"]*digiq["Units"])/area * 100
        digiq.to_csv ("digiq_results/{}_{}_{}_{}_{}_{}_{}_{}_{}.csv".format (self.bs, self.num_group, self.num_qubit,\
                                                                            self.y_length, self.z_length, self.q2_length,\
                                                                            self.q2sel_width, self.ctrl_width, self.readout_mux))
        print ("\nDigiQ at 4K")
        print (digiq)
        
        # 3ns latency following JoSIM simulation.
        self.jpm_readout["PowerDynamic"] = self.jpm_readout["EnergyDynamic"] * 1/3
        self.jpm_readout.to_csv ("digiq_results/jpm_readout_baseline.csv")
        print ("\nJPM Readout at 20mK")
        print (self.jpm_readout)


def main (argv):

    b = FLAGS.b
    g = FLAGS.g
    q = FLAGS.q
    y = FLAGS.y
    z = FLAGS.z
    l = FLAGS.l
    t = FLAGS.t
    c = FLAGS.c
    m = FLAGS.m
    digiq = digiq_hardware (b, g, q, y, z, l, t, c, m)
    digiq.summary ()


if __name__ == "__main__":
    app.run (main)
