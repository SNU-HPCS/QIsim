#!/usr/bin/env python3.8

from argparse import ArgumentParser
import os, pgen
from cacti import cacti
from cacti.cacti_interface_pb2 import CactiInput

def model_cache(cacti_config_file, capacity, pgen_output):
    cacti_input = CactiInput ()
    cacti_input.config_file = os.path.abspath(cacti_config_file)
    cacti_input.tech_param.cache_sz = capacity

    # change sram_cell transistor values.
    cacti_input.tech_param.sram_cell.R_nch_on = 1.45*pgen_output.user_input.Vdd / pgen_output.output_parameter.nmos.Ion
    cacti_input.tech_param.sram_cell.R_pch_on = 1.45*pgen_output.user_input.Vdd / pgen_output.output_parameter.pmos.Ion
    cacti_input.tech_param.sram_cell.Vdd = pgen_output.user_input.Vdd
    cacti_input.tech_param.sram_cell.Vth = pgen_output.output_parameter.nmos.Vth_on
    cacti_input.tech_param.sram_cell.I_on_n = pgen_output.output_parameter.nmos.Ion
    cacti_input.tech_param.sram_cell.I_on_p = pgen_output.output_parameter.pmos.Ion
    if pgen_output.output_parameter.nmos.Isub == 0.0:
        cacti_input.tech_param.sram_cell.I_off_n = 1e-20
    else:
        cacti_input.tech_param.sram_cell.I_off_n = pgen_output.output_parameter.nmos.Isub
    if pgen_output.output_parameter.pmos.Isub == 0.0:
        cacti_input.tech_param.sram_cell.I_off_p = 1e-20
    else:
        cacti_input.tech_param.sram_cell.I_off_p = pgen_output.output_parameter.pmos.Isub
    cacti_input.tech_param.sram_cell.I_g_on_n = pgen_output.output_parameter.nmos.Igate
    cacti_input.tech_param.sram_cell.I_g_on_p = pgen_output.output_parameter.pmos.Igate
    cacti_input.tech_param.sram_cell.n_to_p_eff_curr_drv_ratio = pgen_output.output_parameter.nmos.Ion / pgen_output.output_parameter.pmos.Ion
    # change peri_global transistor values (repeater/decoder/SA...).
    cacti_input.tech_param.peri_global.R_nch_on = 1.45*pgen_output.user_input.Vdd / pgen_output.output_parameter.nmos.Ion
    cacti_input.tech_param.peri_global.R_pch_on = 1.45*pgen_output.user_input.Vdd / pgen_output.output_parameter.pmos.Ion
    cacti_input.tech_param.peri_global.Vdd = pgen_output.user_input.Vdd
    cacti_input.tech_param.peri_global.Vth = pgen_output.output_parameter.nmos.Vth_on
    cacti_input.tech_param.peri_global.I_on_n = pgen_output.output_parameter.nmos.Ion
    cacti_input.tech_param.peri_global.I_on_p = pgen_output.output_parameter.pmos.Ion
    if pgen_output.output_parameter.nmos.Isub == 0.0:
        cacti_input.tech_param.peri_global.I_off_n = 1e-20
    else:
        cacti_input.tech_param.peri_global.I_off_n = pgen_output.output_parameter.nmos.Isub
    if pgen_output.output_parameter.pmos.Isub == 0.0:
        cacti_input.tech_param.peri_global.I_off_p = 1e-20
    else:
        cacti_input.tech_param.peri_global.I_off_p = pgen_output.output_parameter.pmos.Isub
    cacti_input.tech_param.peri_global.I_g_on_n = pgen_output.output_parameter.nmos.Igate
    cacti_input.tech_param.peri_global.I_g_on_p = pgen_output.output_parameter.pmos.Igate
    cacti_input.tech_param.peri_global.n_to_p_eff_curr_drv_ratio = pgen_output.output_parameter.nmos.Ion / pgen_output.output_parameter.pmos.Ion
    # change wire values.
    cacti_input.tech_param.wire_local.R_per_um_mult = (pgen_output.output_parameter.wire.Resistivity / pgen_output.output_parameter.wire_ref.Resistivity)
    cacti_input.tech_param.wire_inside_mat.R_per_um_mult = (pgen_output.output_parameter.wire.Resistivity / pgen_output.output_parameter.wire_ref.Resistivity)
    cacti_input.tech_param.wire_outside_mat.R_per_um_mult = (pgen_output.output_parameter.wire.Resistivity / pgen_output.output_parameter.wire_ref.Resistivity)
    cacti_input.tech_param.vpp = pgen_output.user_input.Vdd + pgen_output.user_input.Vth0
    cacti_input.tech_param.dram_cell_Vdd = pgen_output.user_input.Vdd
    cacti_input.const_param.CU_RESISTIVITY = pgen_output.output_parameter.wire.Resistivity*1e-2*(0.022/0.018)
    cacti_input.const_param.BULK_CU_RESISTIVITY = pgen_output.output_parameter.wire.Resistivity*1e-2
    cacti_print_stderr = True

    # cacti exec
    cacti_output_ = cacti (proto=cacti_input, print_stderr=cacti_print_stderr)
    print(cacti_output_)

def model_dram(cacti_config_file, pgen_output, mode=0):
    cacti_input = CactiInput ()
    cacti_input.config_file = os.path.abspath(cacti_config_file)

    cacti_input.tech_param.dram_acc.R_nch_on = 1.69*(pgen_output["wl"].user_input.Vdd + pgen_output["wl"].output_parameter.nmos.Vth0+0.5) / pgen_output["wl"].output_parameter.nmos.Ion
    cacti_input.tech_param.dram_acc.R_pch_on = 1.69*(pgen_output["wl"].user_input.Vdd + pgen_output["wl"].output_parameter.nmos.Vth0+0.5) / pgen_output["wl"].output_parameter.pmos.Ion
    cacti_input.tech_param.dram_acc.Vdd =  pgen_output["wl"].user_input.Vdd
    cacti_input.tech_param.dram_acc.Vth =  pgen_output["wl"].output_parameter.nmos.Vth0
    cacti_input.tech_param.dram_acc.I_on_n = pgen_output["wl"].output_parameter.nmos.Ion
    cacti_input.tech_param.dram_acc.I_on_p = pgen_output["wl"].output_parameter.pmos.Ion
    if pgen_output["wl"].output_parameter.nmos.Isub == 0.0:
        cacti_input.tech_param.dram_acc.I_off_n = 1e-20
    else:
        cacti_input.tech_param.dram_acc.I_off_n = pgen_output["wl"].output_parameter.nmos.Isub
    if pgen_output["wl"].output_parameter.pmos.Isub == 0.0:
        cacti_input.tech_param.dram_acc.I_off_p = 1e-20
    else:
        cacti_input.tech_param.dram_acc.I_off_p = pgen_output["wl"].output_parameter.pmos.Isub
    cacti_input.tech_param.dram_acc.I_g_on_n = pgen_output["wl"].output_parameter.nmos.Igate
    cacti_input.tech_param.dram_acc.I_g_on_p = pgen_output["wl"].output_parameter.pmos.Igate
    cacti_input.tech_param.dram_acc.n_to_p_eff_curr_drv_ratio = pgen_output["wl"].output_parameter.nmos.Ion / pgen_output["wl"].output_parameter.pmos.Ion

    cacti_input.tech_param.dram_wl.R_nch_on = 1.69*(pgen_output["wl"].user_input.Vdd + pgen_output["wl"].output_parameter.nmos.Vth0 +0.5) / pgen_output["wl"].output_parameter.nmos.Ion
    cacti_input.tech_param.dram_wl.R_pch_on = 1.69*(pgen_output["wl"].user_input.Vdd + pgen_output["wl"].output_parameter.nmos.Vth0 +0.5) / pgen_output["wl"].output_parameter.pmos.Ion
    cacti_input.tech_param.dram_wl.Vdd = pgen_output["wl"].user_input.Vdd
    cacti_input.tech_param.dram_wl.Vth = pgen_output["wl"].output_parameter.nmos.Vth0
    cacti_input.tech_param.dram_wl.I_on_n = pgen_output["wl"].output_parameter.nmos.Ion
    cacti_input.tech_param.dram_wl.I_on_p = pgen_output["wl"].output_parameter.pmos.Ion
    if pgen_output["wl"].output_parameter.nmos.Isub == 0.0:
        cacti_input.tech_param.dram_wl.I_off_n = 1e-20
    else:
        cacti_input.tech_param.dram_wl.I_off_n = pgen_output["wl"].output_parameter.nmos.Isub
    if pgen_output["wl"].output_parameter.pmos.Isub == 0.0:
        cacti_input.tech_param.dram_wl.I_off_p = 1e-20
    else:
        cacti_input.tech_param.dram_wl.I_off_p = pgen_output["wl"].output_parameter.pmos.Isub
    cacti_input.tech_param.dram_wl.I_g_on_n = pgen_output["wl"].output_parameter.nmos.Igate
    cacti_input.tech_param.dram_wl.I_g_on_p = pgen_output["wl"].output_parameter.pmos.Igate
    cacti_input.tech_param.dram_wl.n_to_p_eff_curr_drv_ratio = pgen_output["wl"].output_parameter.nmos.Ion / pgen_output["wl"].output_parameter.pmos.Ion

    cacti_input.tech_param.peri_global.R_nch_on = 1.49*pgen_output["hp"].user_input.Vdd / pgen_output["hp"].output_parameter.nmos.Ion
    cacti_input.tech_param.peri_global.R_pch_on = 1.49*pgen_output["hp"].user_input.Vdd / pgen_output["hp"].output_parameter.pmos.Ion
    cacti_input.tech_param.peri_global.Vdd = pgen_output["hp"].user_input.Vdd
    cacti_input.tech_param.peri_global.Vth = pgen_output["hp"].output_parameter.nmos.Vth_on
    cacti_input.tech_param.peri_global.I_on_n = pgen_output["hp"].output_parameter.nmos.Ion
    cacti_input.tech_param.peri_global.I_on_p = pgen_output["hp"].output_parameter.pmos.Ion
    if pgen_output["hp"].output_parameter.nmos.Isub == 0.0:
        cacti_input.tech_param.peri_global.I_off_n = 1e-20
    else:
        cacti_input.tech_param.peri_global.I_off_n = pgen_output["hp"].output_parameter.nmos.Isub
    if pgen_output["hp"].output_parameter.pmos.Isub == 0.0:
        cacti_input.tech_param.peri_global.I_off_p = 1e-20
    else:
        cacti_input.tech_param.peri_global.I_off_p = pgen_output["hp"].output_parameter.pmos.Isub
    cacti_input.tech_param.peri_global.I_g_on_n = pgen_output["hp"].output_parameter.nmos.Igate
    cacti_input.tech_param.peri_global.I_g_on_p = pgen_output["hp"].output_parameter.pmos.Igate
    cacti_input.tech_param.peri_global.n_to_p_eff_curr_drv_ratio = pgen_output["hp"].output_parameter.nmos.Ion / pgen_output["hp"].output_parameter.pmos.Ion

    cacti_input.tech_param.wire_local.R_per_um_mult = (pgen_output["hp"].output_parameter.wire.Resistivity / pgen_output["hp"].output_parameter.wire_ref.Resistivity)
    cacti_input.tech_param.wire_inside_mat.R_per_um_mult = (pgen_output["hp"].output_parameter.wire.Resistivity / pgen_output["hp"].output_parameter.wire_ref.Resistivity)
    cacti_input.tech_param.wire_outside_mat.R_per_um_mult = (pgen_output["hp"].output_parameter.wire.Resistivity / pgen_output["hp"].output_parameter.wire_ref.Resistivity) 
    cacti_input.tech_param.vpp = pgen_output["wl"].user_input.Vdd + pgen_output["wl"].user_input.Vth0
    cacti_input.tech_param.dram_cell_Vdd = pgen_output["wl"].user_input.Vdd
    
    cacti_input.const_param.CU_RESISTIVITY = pgen_output["hp"].output_parameter.wire.Resistivity*1e-2*(0.022/0.018)
    cacti_input.const_param.BULK_CU_RESISTIVITY = pgen_output["hp"].output_parameter.wire.Resistivity*1e-2
    
    if mode == 1 or mode == 2:
        cacti_input.dyn_param_prefix = current_path () + ("/circuit_configs/%.2f%.2f%.2f%.2f" % (pgen_output["hp"].user_input.Vdd, pgen_output["hp"].user_input.Vth0, pgen_output["wl"].user_input.Vdd, pgen_output["wl"].user_input.Vth0))
        cacti_input.wire_config = current_path () + ("/circuit_configs/%.2f%.2f%.2f%.2f_wire.txt" % (pgen_output["hp"].user_input.Vdd, pgen_output["hp"].user_input.Vth0, pgen_output["wl"].user_input.Vdd, pgen_output["wl"].user_input.Vth0))

    
    # cacti exec
    if mode == 0 or mode == 1:
        cacti_output = cacti (proto=cacti_input, print_stderr=True)
    elif mode == 2:
        cacti_output = cacti (proto=cacti_input, print_stderr=True, reproduce=True)
    print(cacti_output)

def parse_arguments():
    parser = ArgumentParser()

    parser.add_argument('cacti_config_file', help='Config file for cacti')

    parser.add_argument('--pgen', help='Path for pgen', default='./CryoMOSFET_77K/pgen.py')

    parser.add_argument('temperature', help='Target operating temperature (77-300 [K])', type=int)
    parser.add_argument('node', help='Technology node size [nm]', type=int)
    parser.add_argument('vdd', help='Supply voltage [V]', type=float)
    parser.add_argument('vth', help='Threshold voltage at 300K (i.e., Vth_300k) [V]', type=float)
    parser.add_argument('capacity', help='Size of the cache/memory [Bytes]', type=int)

    subparsers = parser.add_subparsers(help='Cell types')

    parser_dram = subparsers.add_parser('dram', help='DRAM memory')
    parser_dram.set_defaults(cell_type='dram')
    parser_dram.add_argument('acc_vdd', help='Supply voltage for access transistors [V]', type=float)
    parser_dram.add_argument('acc_vth', help='Threshold voltage for access transistors at 300K [V]', type=float)

    parser_sram = subparsers.add_parser('cache', help='cache')
    parser_sram.set_defaults(cell_type='cache')

    return parser.parse_args()

def main():
    args = parse_arguments()

    # Code to support 4K
    pgen_path = None
    if args.temperature >= 77:
        #pgen_path = args.pgen
        pgen_path = '../CryoMOSFET/CryoMOSFET_77K/pgen.py'
    elif args.temperature == 4:
        pgen_path = '../CryoMOSFET/CryoMOSFET_4K/pgen.py'
    else:
        print ("Current version of CryoMEM does not support {}K.".format (args.temperature))
        exit ()

    hp_results = pgen.run(pgen_path, pgen.mosfet_mode.HP, args.temperature, args.node, args.vdd, args.vth)
    if args.cell_type == 'dram':
        acc_results = pgen.run(pgen_path, pgen.mosfet_mode.ACC, args.temperature, args.node, args.acc_vdd, args.acc_vth)
        model_dram(args.cacti_config_file, {'hp': hp_results, 'wl': acc_results})
    else:
        model_cache(args.cacti_config_file, args.capacity, hp_results)

if __name__ == '__main__':
    main()
