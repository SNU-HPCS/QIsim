#!/usr/bin/env python3.8

import argparse
import os
from subprocess import PIPE, run
import pandas as pd
import json

def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--temperature", "-t", help="Target temeprature (i.e., 300K, 77K, or 4K)", type=int, default=4)
    parser.add_argument ("--node", "-n", help="Technology node (i.e., 45nm)", type=int, default=45)
    parser.add_argument ("--vdd", "-d", help="Supply voltage", type=float, default=0)
    parser.add_argument ("--vth", "-r", help="Threshold voltage at 300K (i.e., Vth_300k)", type=float, default=0)
    args = parser.parse_args ()
    return args


def run_synthesis ():
    current_dir_ = os.getcwd ()
    os.chdir ("./CryoModel/CryoPipeline")
    result = run ("python3.8 ./logic_model.py", \
    stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    os.chdir (current_dir_)
    

def run_pgen (temperature, node=45, vdd=None, vth=None):
    result = None
    if temperature >= 77:
        if vdd == None and vth == None:
            result = run ("python ./CryoModel/CryoMOSFET/CryoMOSFET_77K/pgen.py -n {} -t {}".format \
            (node, temperature), stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        else:
            result = run ("python ./CryoModel/CryoMOSFET/CryoMOSFET_77K/pgen.py -n {} -d {} -r {} -t {}".format \
                (node, vdd, vth, temperature), stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    else:
        if vdd == None and vth == None:
            result = run ("python ./CryoModel/CryoMOSFET/CryoMOSFET_4K/pgen.py -n {} -t {}".format \
                (node, temperature), stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        else:
            result = run ("python ./CryoModel/CryoMOSFET/CryoMOSFET_4K/pgen.py -n {} -d {} -r {} -t {}".format \
                (node, vdd, vth, temperature), stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
    return result.stdout


def run_cacti (config_file, capacity, vdd, vth):
    result = run ("python ./memory_model.py ./configs/{} 4 45 {} {} {} cache".format \
    (config_file, vdd, vth, capacity), stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True, cwd="./CryoModel/CryoMEM")
    return result.stdout


def parse_cacti (cacti_output, power_scaling_factor, is_double_accessed=False):
    cacti_output_lines = cacti_output.split ("\n")
    parsed_result = dict ()
    #TODO: insert appropriate targets.
    for line in cacti_output_lines:
        if "Total leakage power of a bank (mW)" in line:
            parsed_result["static"] = float (line.split (":")[1])*1e-3
        elif "Total gate leakage power of a bank (mW)" in line:
            parsed_result["static"] += float (line.split (":")[1])*1e-3
        elif "Total dynamic read energy per access (nJ)" in line:
            parsed_result["dynamic"] = float (line.split (":")[1])*1e-9*power_scaling_factor
        elif is_double_accessed and "Total dynamic write energy per access (nJ)" in line:
            parsed_result["dynamic"] += float (line.split (":")[1])*1e-9*power_scaling_factor
    return parsed_result


def report_perf_power (design_names, temperature, node, vdd, vth):
    critical_delay = 0
    final_powers = dict ()
    for design_name in design_names:
        f = open ("./CryoModel/CryoPipeline/latency_result/{}/critical_path_4k".format (design_name), "r")
        lines = f.readlines ()
        for line in lines:
            if "data arrival time" in line:
                critical_delay = float (line.split ()[-1])
                break
        f.close ()

        pgen_300k = run_pgen (300, 45, 1.1, 0.46893) # FreePDK 45nm (Vdd) & ITRS (Vth)
        pgen_temp = run_pgen (temperature, 45, vdd, vth)

        pgen_ref = dict ()
        lines = pgen_300k.split ("\n")
        for line in lines:
            if "Vdd" in line:
                pgen_ref["Vdd"] = float (line.split ()[1])
            if "Ion" in line:
                pgen_ref["Ion"] = float (line.split ()[1])
            if "Isub" in line:
                pgen_ref["Isub"] = float (line.split ()[1])
            if "Igate" in line:
                pgen_ref["Igate"] = float (line.split ()[1])
                break

        pgen_target = dict ()
        lines = pgen_temp.split ("\n")
        for line in lines:
            if "Vdd" in line:
                pgen_target["Vdd"] = float (line.split ()[1])
            if "Ion" in line:
                pgen_target["Ion"] = float (line.split ()[1])
            if "Isub" in line:
                pgen_target["Isub"] = float (line.split ()[1])
            if "Igate" in line:
                pgen_target["Igate"] = float (line.split ()[1])
                break

        # Transistor speed-up (Ion/Vdd)
        trans_speedup = (pgen_target["Ion"]/pgen_target["Vdd"]) / (pgen_ref["Ion"]/pgen_ref["Vdd"])
        # Dynamic power reduction (Vdd^2)
        dyn_reduction = ((pgen_target["Vdd"]**2) / (pgen_ref["Vdd"]**2))
        # Static power reduction (Isub+Igate)
        stat_reduction = ((pgen_target["Vdd"]*(pgen_target["Isub"]+pgen_target["Igate"])) / (pgen_ref["Vdd"]*(pgen_ref["Isub"]+pgen_ref["Igate"])))

        
        unit_powers_total = dict ()
        f = open ("./CryoModel/CryoPipeline/latency_result/{}/power_4k".format (design_name), "r")
        lines = f.readlines ()
        
        # Based on ITRS roadmap.
        ## Power scaling value is huge because we fix frequency and the number of transistors.
        ## (except 45nm->22nm which increase the clock frequency)
        if node == 45:
            power_scaling_factor = 1
            perf_scaling_factor = 1
        if node == 22:
            power_scaling_factor = 1/2.01
            perf_scaling_factor = 1.438
        elif node == 14:
            power_scaling_factor = 1/8.19
            perf_scaling_factor = 2.929
        elif node == 7:
            power_scaling_factor = 1/33.99
            perf_scaling_factor = 6.308

        # We fix the clock frequency to 2.5GHz (except 45nm)
        # If the frequency is lower than 2.5GHz, you should find the new configuration.
        critical_delay_total = critical_delay / trans_speedup / perf_scaling_factor
        if critical_delay_total > 1/2.5:
            print ("Frequency is lower than 2.5GHz; Too low Vdd with high Vth.")
            exit ()
        
        if design_name == "drive_circuit":
            unit_powers = dict ()
            for n, line in enumerate (lines):
                data = line.split ()
                if len (data) < 1:
                    continue
                elif "drive_z_corr_table_instance" in data[0]:
                    next_data = lines[n+1].split ()
                    dynamic_power = (float (next_data[0])*1e-6 + float (next_data[1])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (next_data[2])*1e-9)*stat_reduction
                    unit_powers["z_corr_table"] = {"static": static_power, "dynamic": dynamic_power}
                
                elif "genblk_nco[15]" in data[0]:
                    next_data = lines[n+1].split ()
                    dynamic_power = (float (next_data[0])*1e-6 + float (next_data[1])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (next_data[2])*1e-9)*stat_reduction
                    unit_powers["nco"] = {"static": static_power, "dynamic": dynamic_power}

                elif "drive_calibration_unit_instance" in data[0]:
                    next_data = lines[n+1].split ()
                    dynamic_power = (float (next_data[0])*1e-6 + float (next_data[1])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (next_data[2])*1e-9)*stat_reduction
                    unit_powers["calibration_unit"] = {"static": static_power, "dynamic": dynamic_power}

                elif "polar_modulation_unit_instance" in data[0]:
                    next_data = lines[n+1].split ()
                    dynamic_power = (float (next_data[0])*1e-6 + float (next_data[1])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (next_data[2])*1e-9)*stat_reduction
                    unit_powers["polar_modulation_unit"] = {"static": static_power, "dynamic": dynamic_power}

                elif "nco_mux" in data[0]:
                    next_data = lines[n+1].split ()
                    dynamic_power = (float (next_data[0])*1e-6 + float (next_data[1])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (next_data[2])*1e-9)*stat_reduction
                    unit_powers["nco_mux"] = {"static": static_power, "dynamic": dynamic_power}
        
                elif "inst_table_mux" in data[0]:
                    next_data = lines[n+1].split ()
                    dynamic_power = (float (next_data[0])*1e-6 + float (next_data[1])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (next_data[2])*1e-9)*stat_reduction
                    unit_powers["inst_table_mux"] = {"static": static_power, "dynamic": dynamic_power}
        
                elif "pc_0" in data[0]:
                    dynamic_power = (float (data[2])*1e-6 + float (data[3])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (data[4])*1e-9)*stat_reduction
                    unit_powers["pc"] = {"static": static_power, "dynamic": dynamic_power}

                elif "control_unit" in data[0]:
                    next_data = lines[n+1].split ()
                    dynamic_power = (float (next_data[0])*1e-6 + float (next_data[1])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (next_data[2])*1e-9)*stat_reduction
                    unit_powers["control_unit"] = {"static": static_power, "dynamic": dynamic_power}

            unit_powers_total["z_correction_module"] = unit_powers["z_corr_table"]
            unit_powers_total["nco"] = unit_powers["nco"]
            unit_powers_total["other_inside_bank"] = {"static": unit_powers["calibration_unit"]["static"] + unit_powers["polar_modulation_unit"]["static"] \
                                                        + unit_powers["nco_mux"]["static"] + unit_powers["inst_table_mux"]["static"], \
                                                        "dynamic": unit_powers["calibration_unit"]["dynamic"] + unit_powers["polar_modulation_unit"]["dynamic"] \
                                                        + unit_powers["nco_mux"]["dynamic"] + unit_powers["inst_table_mux"]["dynamic"]}
            unit_powers_total["other_outside_bank"] = {"static": unit_powers["pc"]["static"] + unit_powers["control_unit"]["static"], \
                                                        "dynamic": unit_powers["pc"]["dynamic"] + unit_powers["control_unit"]["dynamic"]}
            unit_powers_total["analog"] = {"static":0, "dynamic":1.68e-3*32/2.5e9*2.011348*power_scaling_factor}

            unit_powers_total["inst_table"] = parse_cacti (run_cacti ("drive-inst-table.cfg", 4352, vdd, vth), power_scaling_factor)
            unit_powers_total["gate_table"] = parse_cacti (run_cacti ("drive-gate-table.cfg", 544, vdd, vth), power_scaling_factor)
            unit_powers_total["wave_table"] = parse_cacti (run_cacti ("drive-wave-table.cfg", 92160, vdd, vth), power_scaling_factor)
            
            z_corr_table = parse_cacti (run_cacti ("drive-zcorrection-table.cfg", 1536, vdd, vth), power_scaling_factor)
            unit_powers_total["z_correction_module"]["static"] += z_corr_table["static"]
            unit_powers_total["z_correction_module"]["dynamic"] += z_corr_table["dynamic"]
            
            lut = parse_cacti (run_cacti ("drive-lut.cfg", 1024, vdd, vth), power_scaling_factor)
            unit_powers_total["other_inside_bank"]["static"] += 2*lut["static"]
            unit_powers_total["other_inside_bank"]["dynamic"] += 2*lut["dynamic"]
            print (pd.DataFrame.from_dict (unit_powers_total))
            final_powers["drive_circuit"] = unit_powers_total

        elif design_name == "pulse_circuit":
            unit_powers = dict ()
            for n, line in enumerate (lines):
                data = line.split ()
                if len (data) < 1:
                    continue
                elif ("pulse_circuit" in data[0]) and (len (data) == 6):
                    dynamic_power = (float (data[1])*1e-6 + float (data[2])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (data[3])*1e-9)*stat_reduction
                    unit_powers["pulse_circuit"] = {"static": static_power, "dynamic": dynamic_power}
                
                elif "pulse_length_counter_instance" in data[0]:
                    next_data = lines[n+1].split ()
                    dynamic_power = (float (next_data[0])*1e-6 + float (next_data[1])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (next_data[2])*1e-9)*stat_reduction
                    unit_powers["len_counter"] = {"static": static_power, "dynamic": dynamic_power}

                elif "pulse_amp_memory_addr_generator_instance" in data[0]:
                    next_data = lines[n+1].split ()
                    dynamic_power = (float (next_data[0])*1e-6 + float (next_data[1])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (next_data[2])*1e-9)*stat_reduction
                    unit_powers["addr_generator"] = {"static": static_power, "dynamic": dynamic_power}

                elif "glb_counter_comparator" in data[0]:
                    next_data = lines[n+1].split ()
                    dynamic_power = (float (next_data[0])*1e-6 + float (next_data[1])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (next_data[2])*1e-9)*stat_reduction
                    unit_powers["glb_counter_comparator"] = {"static": static_power, "dynamic": dynamic_power}

            unit_powers_total["several"] = {"static": unit_powers["len_counter"]["static"] + unit_powers["addr_generator"]["static"] + unit_powers["glb_counter_comparator"]["static"], \
                                            "dynamic": unit_powers["len_counter"]["dynamic"] + unit_powers["addr_generator"]["dynamic"] + unit_powers["glb_counter_comparator"]["dynamic"]}
            unit_powers_total["once"] = {"static": unit_powers["pulse_circuit"]["static"] - unit_powers_total["several"]["static"], \
                                         "dynamic": unit_powers["pulse_circuit"]["dynamic"] - unit_powers_total["several"]["dynamic"]}
            unit_powers_total["analog"] = {"static":0, "dynamic":2.3e-3/2.5e9*2.011348*power_scaling_factor}

            unit_powers_total["inst_table"] = parse_cacti (run_cacti ("pulse-inst-table.cfg", 108, vdd, vth), power_scaling_factor)
            unit_powers_total["amp_table"] = parse_cacti (run_cacti ("pulse-amp-table.cfg", 2000, vdd, vth), power_scaling_factor)
            print (pd.DataFrame.from_dict (unit_powers_total))
            final_powers["pulse_circuit"] = unit_powers_total

        elif design_name == "readout_tx_circuit":
            unit_powers = dict ()
            for n, line in enumerate (lines):
                data = line.split ()
                if len (data) < 1:
                    continue
                elif "genblk_tx_signal_gen[5]" in data[0]:
                    next_data = lines[n+1].split ()
                    dynamic_power = (float (next_data[0])*1e-6 + float (next_data[1])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (next_data[2])*1e-9)*stat_reduction
                    unit_powers["signal_gen"] = {"static": static_power, "dynamic": dynamic_power}

            unit_powers_total["signal_gen"] = unit_powers["signal_gen"]
            unit_powers_total["inst_table"] = parse_cacti (run_cacti ("tx-inst-table.cfg", 304, vdd, vth), power_scaling_factor)
            unit_powers_total["lut"] = parse_cacti (run_cacti ("tx-lut.cfg", 1024, vdd, vth), power_scaling_factor)
            unit_powers_total["analog"] = {"static":0, "dynamic": 1.61e-3*32/2.5e9*2.011348*power_scaling_factor}
            print (pd.DataFrame.from_dict (unit_powers_total))
            final_powers["readout_tx_circuit"] = unit_powers_total

        elif design_name == "readout_rx_circuit":
            unit_powers = dict ()
            for n, line in enumerate (lines):
                data = line.split ()
                if len (data) < 1:
                    continue
                
                elif "readout_rx_calibration_unit_instance" in data[0]:
                    next_data = lines[n+1].split ()
                    dynamic_power = (float (next_data[0])*1e-6 + float (next_data[1])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (next_data[2])*1e-9)*stat_reduction
                    unit_powers["other_digital"] = {"static": static_power, "dynamic": dynamic_power}

                elif "genblk_rx_signal_decode[5]" in data[0]:
                    next_data = lines[n+1].split ()
                    dynamic_power = (float (next_data[0])*1e-6 + float (next_data[1])*1e-6)*dyn_reduction*power_scaling_factor/2.5e9
                    static_power = (float (next_data[2])*1e-9)*stat_reduction
                    unit_powers["digital_per_qubit"] = {"static": static_power, "dynamic": dynamic_power}

            unit_powers_total["digital_per_qubit"] = unit_powers["digital_per_qubit"]
            unit_powers_total["other_digital"] = unit_powers["other_digital"]

            unit_powers_total["inst_table"] = parse_cacti (run_cacti ("rx-inst-table.cfg", 332, vdd, vth), power_scaling_factor)
            iqplain = parse_cacti (run_cacti ("rx-iqplain.cfg", 32768, vdd, vth), power_scaling_factor, True)
            lut = parse_cacti (run_cacti ("rx-lut.cfg", 1024, vdd, vth), power_scaling_factor)
            unit_powers_total["digital_per_qubit"]["static"] += (iqplain["static"] + 2*lut["static"])
            unit_powers_total["digital_per_qubit"]["dynamic"] += (iqplain["dynamic"] + 2*lut["dynamic"])
            unit_powers_total["analog"] = {"static":0, "dynamic":0.89e-3*32/2.5e9*2.011348*power_scaling_factor}
            print (pd.DataFrame.from_dict (unit_powers_total))
            final_powers["readout_rx_circuit"] = unit_powers_total

    with open ("cmos_results/{}k_{}nm_{}v_{}v.json".format (temperature, node, vdd, vth), "w") as f:
        json.dump (final_powers, f, indent=4)


def clean_up ():
    os.system ("make clean")


def main ():

    args = arg_parse ()
    temperature = args.temperature
    node = args.node
    vdd = args.vdd if args.vdd > 0 else 1.1     # Vdd of 45nm ITRS
    vth = args.vth if args.vth > 0 else 0.46893 # Vth of 45nm ITRS
    design_names = ["drive_circuit", "pulse_circuit", "readout_tx_circuit", "readout_rx_circuit"]

    # Input-requirement checking.
    if node not in [45, 22, 14, 7]:
        print ("Currently, CryoPipeline only supports 45nm, 22nm, 14nm, and 7nm.")
        exit ()
    if not any ((temperature == key_) for key_ in [300, 77, 4]):
        print ("Currently, CryoPipeline only supports 300K, 77K, and 4K.")
        exit ()

    run_synthesis ()
    report_perf_power (design_names, temperature, node, vdd, vth)

    
if __name__ == "__main__":
    main ()
