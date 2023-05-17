#!/usr/bin/env python3.8

from mosfet import *
from wire import *
from itrs import *
import argparse
import numpy as np


def printer_mosfet (mosfet_, is_ref_):
    mos_type_str = "NMOS" if mosfet_.mos_type == 1 else "PMOS"
    is_ref_str = "Reference" if is_ref_ == True else "Target"
    print ("%s running at %dK (%s)" % (mos_type_str, mosfet_.temperature, is_ref_str))
    print ("Vdd:\t\t%f [V]" % (mosfet_.Vdd))
    print ("Vth0:\t\t%f [V]" % (mosfet_.Vth0))
    print ("Vth_on:\t\t%f [V]" % (mosfet_.Vth_on))
    print ("Vth_off:\t%f [V]" % (mosfet_.Vth_off))
    print ("Ion:\t\t%.3f [uA/um]" % (mosfet_.Ion * 1e6))
    print ("Isub:\t\t%f [uA/um]" % (mosfet_.Isub * 1e6))
    print ("Igate:\t\t%f [uA/um]" % (mosfet_.Igate * 1e6))
    print ("")
    print ("V/I:\t\t%.3f" % (mosfet_.Ion * 1e6 / mosfet_.Vdd / 1600))
    print ("Static:\t\t%f [uA/um]" % (mosfet_.Isub * 1e6 / 0.02135))
    print ("")


def printer_wire (wire_, is_ref_):
    wire_type_str = "Bulk wire" if wire_.wire_mode == 1 else ("Narrow wire (%d * %d)" % (wire_.width, wire_.height))
    is_ref_str = "Reference" if is_ref_ == True else "Target"
    print ("%s at %dK (%s)" % (wire_type_str, wire_.temperature, is_ref_str))
    print ("Rwire:\t\t%.12f [uOhm*cm]" % (wire_.Rwire))
    print ("")


def arg_parse ():
    parser = argparse.ArgumentParser ()
    parser.add_argument ("--mosfet_mode", "-mm", help="1:HP transistor, 2:DRAM access transistor", type=int, default=1)
    parser.add_argument ("--temperature", "-t", help="Target operating temperature (77-300 [K])", type=int, default=300)
    parser.add_argument ("--node", "-n", help="Technology node (16,22,32,45,65,90,130 [nm])", type=int, default=22)
    parser.add_argument ("--vdd", "-d", help="Supply voltage", type=float, default=0)
    parser.add_argument ("--vth", "-r", help="Threshold voltage at 300K (i.e., Vth_300k)", type=float, default=0)

    parser.add_argument ("--wire_mode", "-wm", help="1:Bulk wire, 2:Narrow wire (need the wire width and height)", type=int, default=1)
    parser.add_argument ("--width", "-w", help="Wire width [nm]", type=int, default=0)
    parser.add_argument ("--height", "-hi", help="Wire height [nm]", type=int, default=0)
    args = parser.parse_args ()
    return args


def main ():
    args = arg_parse ()
    mosfet_mode = args.mosfet_mode
    temperature = args.temperature
    node = args.node
    Vitrs = itrs (node)
    Vdd = args.vdd if args.vdd > 0 else Vitrs.Vdd
    Vth0_300k = args.vth if args.vth > 0 else Vitrs.Vth_n
    wire_mode = args.wire_mode
    width = args.width
    height = args.height

    # For MOSFET
    nmos_ref = mosfet (300, node, Vitrs.Vdd, Vitrs.Vth_n, 1, mosfet_mode)
    pmos_ref = mosfet (300, node, Vitrs.Vdd, Vitrs.Vth_p, 2, mosfet_mode)
    Ion_ratio_ref = nmos_ref.Ion / pmos_ref.Ion

    nmos_target = mosfet (temperature, node, Vdd, Vth0_300k, 1, mosfet_mode)
    
    # Exception for invalid inputs and outputs
    assert (nmos_target.Vth_on > 0), "Invalid input: Vth0"
    assert (nmos_target.Ion > 0), "Invalid output: NMOS Ion"
    assert (nmos_target.Vgs_on > nmos_target.Vth_on), "Invalid combination of inputs: Vdd and Vth0"


    for Vth0p_300k in np.arange (0, 3, 0.005):
        pmos_target = mosfet (temperature, node, Vdd, Vth0p_300k, 2, mosfet_mode)
        Ion_ratio = nmos_target.Ion / pmos_target.Ion
        if (Ion_ratio > Ion_ratio_ref) or (pmos_target.Vth_on > pmos_target.Vgs_on):
            break

    # For wire
    wire_target = wire (wire_mode, temperature, width, height)
    wire_ref = wire (wire_mode, 300, width, height)

    # Report
    printer_mosfet (nmos_target, False)
    printer_mosfet (nmos_ref, True)
    printer_mosfet (pmos_target, False)
    printer_mosfet (pmos_ref, True)
    printer_wire (wire_target, False)
    printer_wire (wire_ref, True)



if __name__ == "__main__":
    main ()
