/*****************************************************************************
 *                                CACTI 7.0
 *                      SOFTWARE LICENSE AGREEMENT
 *            Copyright 2015 Hewlett-Packard Development Company, L.P.
 *                          All Rights Reserved
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.

 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.¡±
 *
 ***************************************************************************/

#include <iostream>
#include <iomanip>
#include <string>
#include <cstring>
#include <cassert>

#include "device_type.h"
#include "cacti_interface.pb.h"
#include "io.h"
#include "input_parameter.h"
#include "technology_parameter.h"
#include "basic_circuit.h"

using namespace std;

void DeviceType::assign(const string& in_file, int tech_flavor, unsigned int temperature)
{
    FILE* fp = fopen(in_file.c_str(), "r");
    char  line[5000];
    // char temp_var[5000];

    // double temp[5];
    // unsigned int thermal_temp;

    double nmos_effective_resistance_multiplier;

    if (!fp) {
        cout << in_file << " is missing!\n";
        exit(-1);
    }

    while (fscanf(fp, "%[^\n]\n", line) != EOF) {
        if (!strncmp("-C_g_ideal", line, strlen("-C_g_ideal"))) {
            C_g_ideal = scan_five_input_double(line, "-C_g_ideal", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-C_fringe", line, strlen("-C_fringe"))) {
            C_fringe = scan_five_input_double(line, "-C_fringe", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-C_junc_sw", line, strlen("-C_junc_sw"))) {
            C_junc_sidewall = scan_five_input_double(line, "-C_junc_sw", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-C_junc", line, strlen("-C_junc"))) {
            C_junc = scan_five_input_double(line, "-C_junc", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }

        if (!strncmp("-l_phy", line, strlen("-l_phy"))) {
            l_phy = scan_five_input_double(line, "-l_phy", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-l_elec", line, strlen("-l_elec"))) {
            l_elec = scan_five_input_double(line, "-l_elec", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-nmos_effective_resistance_multiplier", line, strlen("-nmos_effective_resistance_multiplier"))) {
            nmos_effective_resistance_multiplier
                = scan_five_input_double(line, "-nmos_effective_resistance_multiplier", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-Vdd", line, strlen("-Vdd"))) {
            Vdd = scan_five_input_double(line, "-Vdd", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-Vth", line, strlen("-Vth"))) {
            Vth = scan_five_input_double(line, "-Vth", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-Vdsat", line, strlen("-Vdsat"))) {
            Vdsat = scan_five_input_double(line, "-Vdsat", "V", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-I_on_n", line, strlen("-I_on_n"))) {
            I_on_n = scan_five_input_double(line, "-I_on_n", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-I_on_p", line, strlen("-I_on_p"))) {
            I_on_p = scan_five_input_double(line, "-I_on_p", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-I_off_n", line, strlen("-I_off_n"))) {
            scan_five_input_double_temperature(line, "-I_off_n", "F/um", tech_flavor, temperature, g_ip->print_detail_debug, I_off_n);
            continue;
        }
        if (!strncmp("-I_g_on_n", line, strlen("-I_g_on_n"))) {
            scan_five_input_double_temperature(line, "-I_g_on_n", "F/um", tech_flavor, temperature, g_ip->print_detail_debug, I_g_on_n);
            continue;
        }
        if (!strncmp("-C_ox", line, strlen("-C_ox"))) {
            C_ox = scan_five_input_double(line, "-C_ox", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-t_ox", line, strlen("-t_ox"))) {
            t_ox = scan_five_input_double(line, "-t_ox", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-n2p_drv_rt", line, strlen("-n2p_drv_rt"))) {
            n_to_p_eff_curr_drv_ratio = scan_five_input_double(line, "-n2p_drv_rt", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-lch_lk_rdc", line, strlen("-lch_lk_rdc"))) {
            long_channel_leakage_reduction = scan_five_input_double(line, "-lch_lk_rdc", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-Mobility_n", line, strlen("-Mobility_n"))) {
            Mobility_n = scan_five_input_double(line, "-Mobility_n", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-gmp_to_gmn_multiplier", line, strlen("-gmp_to_gmn_multiplier"))) {
            gmp_to_gmn_multiplier = scan_five_input_double(line, "-gmp_to_gmn_multiplier", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-n_to_p_eff_curr_drv_ratio", line, strlen("-n_to_p_eff_curr_drv_ratio"))) {
            n_to_p_eff_curr_drv_ratio = scan_five_input_double(line, "-n_to_p_eff_curr_drv_ratio", "F/um", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
    }

    C_overlap = 0.2 * C_g_ideal;
    if (tech_flavor >= 3)
        R_nch_on = nmos_effective_resistance_multiplier * g_tp.vpp / I_on_n;  // ohm-micron
    else
        R_nch_on = nmos_effective_resistance_multiplier * Vdd / I_on_n;  // ohm-micron
    R_pch_on     = n_to_p_eff_curr_drv_ratio * R_nch_on;                 // ohm-micron
    I_off_p      = I_off_n;
    I_g_on_p     = I_g_on_n;
    if (g_ip->print_detail_debug) {
        /// cout << nmos_effective_resistance_multiplier << " -- " << Vdd << " -- " << I_on_n << " -- " << n_to_p_eff_curr_drv_ratio << endl;
        cout << "C_overlap: " << C_overlap << " F/um" << endl;
        cout << "R_nch_on: " << R_nch_on << " ohm-micron" << endl;
        cout << "R_pch_on: " << R_pch_on << " ohm-micron" << endl;
    }

    fclose(fp);
}

void DeviceType::interpolate(double alpha, const DeviceType& dev1, const DeviceType& dev2)
{
    C_g_ideal                      = alpha * dev1.C_g_ideal + (1 - alpha) * dev2.C_g_ideal;
    C_fringe                       = alpha * dev1.C_fringe + (1 - alpha) * dev2.C_fringe;
    C_overlap                      = alpha * dev1.C_overlap + (1 - alpha) * dev2.C_overlap;
    C_junc                         = alpha * dev1.C_junc + (1 - alpha) * dev2.C_junc;
    l_phy                          = alpha * dev1.l_phy + (1 - alpha) * dev2.l_phy;
    l_elec                         = alpha * dev1.l_elec + (1 - alpha) * dev2.l_elec;
    R_nch_on                       = alpha * dev1.R_nch_on + (1 - alpha) * dev2.R_nch_on;
    R_pch_on                       = alpha * dev1.R_pch_on + (1 - alpha) * dev2.R_pch_on;
    Vdd                            = alpha * dev1.Vdd + (1 - alpha) * dev2.Vdd;
    Vth                            = alpha * dev1.Vth + (1 - alpha) * dev2.Vth;
    Vcc_min                        = alpha * dev1.Vcc_min + (1 - alpha) * dev2.Vcc_min;
    I_on_n                         = alpha * dev1.I_on_n + (1 - alpha) * dev2.I_on_n;
    I_on_p                         = alpha * dev1.I_on_p + (1 - alpha) * dev2.I_on_p;
    I_off_n                        = alpha * dev1.I_off_n + (1 - alpha) * dev2.I_off_n;
    I_off_p                        = alpha * dev1.I_off_p + (1 - alpha) * dev2.I_off_p;
    I_g_on_n                       = alpha * dev1.I_g_on_n + (1 - alpha) * dev2.I_g_on_n;
    I_g_on_p                       = alpha * dev1.I_g_on_p + (1 - alpha) * dev2.I_g_on_p;
    C_ox                           = alpha * dev1.C_ox + (1 - alpha) * dev2.C_ox;
    t_ox                           = alpha * dev1.t_ox + (1 - alpha) * dev2.t_ox;
    n_to_p_eff_curr_drv_ratio      = alpha * dev1.n_to_p_eff_curr_drv_ratio + (1 - alpha) * dev2.n_to_p_eff_curr_drv_ratio;
    long_channel_leakage_reduction = alpha * dev1.long_channel_leakage_reduction + (1 - alpha) * dev2.long_channel_leakage_reduction;
    Mobility_n                     = alpha * dev1.Mobility_n + (1 - alpha) * dev2.Mobility_n;
    Vdsat                          = alpha * dev1.Vdsat + (1 - alpha) * dev2.Vdsat;
    gmp_to_gmn_multiplier          = alpha * dev1.gmp_to_gmn_multiplier + (1 - alpha) * dev2.gmp_to_gmn_multiplier;
    n_to_p_eff_curr_drv_ratio      = alpha * dev1.n_to_p_eff_curr_drv_ratio + (1 - alpha) * dev2.n_to_p_eff_curr_drv_ratio;

    C_junc_sidewall = dev1.C_junc_sidewall;
}

void DeviceType::overriding(const CactiInput::TechnologyParameter::DeviceType &device_type){
    if (device_type.has_r_nch_on()) R_nch_on = device_type.r_nch_on();
    if (device_type.has_r_pch_on()) R_pch_on = device_type.r_pch_on();
    if (device_type.has_vdd())      Vdd = device_type.vdd();
    if (device_type.has_vth())      Vth = device_type.vth();
    if (device_type.has_vcc_min())  Vcc_min = device_type.vcc_min();
    if (device_type.has_i_on_n())   I_on_n = device_type.i_on_n();
    if (device_type.has_i_on_p())   I_on_p = device_type.i_on_p();
    if (device_type.has_i_off_n())  I_off_n = device_type.i_off_n();
    if (device_type.has_i_off_p())  I_off_p = device_type.i_off_p();
    if (device_type.has_i_g_on_n()) I_g_on_n = device_type.i_g_on_n();
    if (device_type.has_i_g_on_p()) I_g_on_p = device_type.i_g_on_p();
    if (device_type.has_n_to_p_eff_curr_drv_ratio()) n_to_p_eff_curr_drv_ratio = device_type.n_to_p_eff_curr_drv_ratio();
}

void /*TechnologyParameter::*/ DeviceType::display(uint32_t indent) const
{
    string indent_str(indent, ' ');

    cout << indent_str << "C_g_ideal = " << setw(12) << C_g_ideal << " F/um" << endl;
    cout << indent_str << "C_fringe  = " << setw(12) << C_fringe << " F/um" << endl;
    cout << indent_str << "C_overlap = " << setw(12) << C_overlap << " F/um" << endl;
    cout << indent_str << "C_junc    = " << setw(12) << C_junc << " F/um^2" << endl;
    cout << indent_str << "C_junc_sidewall= " << setw(12) << C_junc_sidewall << " F/um^2" << endl;
    cout << indent_str << "l_phy     = " << setw(12) << l_phy << " um" << endl;
    cout << indent_str << "l_elec    = " << setw(12) << l_elec << " um" << endl;
    cout << indent_str << "R_nch_on  = " << setw(12) << R_nch_on << " ohm-um" << endl;
    cout << indent_str << "R_pch_on  = " << setw(12) << R_pch_on << " ohm-um" << endl;
    cout << indent_str << "Vdd       = " << setw(12) << Vdd << " V" << endl;
    cout << indent_str << "Vth       = " << setw(12) << Vth << " V" << endl;
    cout << indent_str << "Vcc_min   = " << setw(12) << Vcc_min << " V" << endl;
    cout << indent_str << "I_on_n    = " << setw(12) << I_on_n << " A/um" << endl;
    cout << indent_str << "I_on_p    = " << setw(12) << I_on_p << " A/um" << endl;
    cout << indent_str << "I_off_n   = " << setw(12) << I_off_n << " A/um" << endl;
    cout << indent_str << "I_off_p   = " << setw(12) << I_off_p << " A/um" << endl;
    cout << indent_str << "I_g_on_n   = " << setw(12) << I_g_on_n << " A/um" << endl;
    cout << indent_str << "I_g_on_p   = " << setw(12) << I_g_on_p << " A/um" << endl;
    cout << indent_str << "C_ox      = " << setw(12) << C_ox << " F/um^2" << endl;
    cout << indent_str << "t_ox      = " << setw(12) << t_ox << " um" << endl;
    cout << indent_str << "n_to_p_eff_curr_drv_ratio = " << n_to_p_eff_curr_drv_ratio << endl;
    cout << indent_str << "long_channel_leakage_reduction = " << long_channel_leakage_reduction << endl;
    cout << indent_str << "Mobility_n = " << Mobility_n << endl;
}

/**
void DeviceType::display(uint32_t indent) const
{
  string indent_str(indent, ' ');

  cout << indent_str << "C_g_ideal = " << setw(12) << C_g_ideal << " F/um" << endl;
  cout << indent_str << "C_fringe  = " << setw(12) << C_fringe  << " F/um" << endl;
  cout << indent_str << "C_overlap = " << setw(12) << C_overlap << " F/um" << endl;
  cout << indent_str << "C_junc    = " << setw(12) << C_junc    << " F/um^2" << endl;
  cout << indent_str << "C_junc_sw    = " << setw(12) << C_junc_sidewall    << " F/um^2" << endl;
  cout << indent_str << "l_phy     = " << setw(12) << l_phy     << " um" << endl;
  cout << indent_str << "l_elec    = " << setw(12) << l_elec    << " um" << endl;
  cout << indent_str << "R_nch_on  = " << setw(12) << R_nch_on  << " ohm-um" << endl;
  cout << indent_str << "R_pch_on  = " << setw(12) << R_pch_on  << " ohm-um" << endl;
  cout << indent_str << "Vdd       = " << setw(12) << Vdd       << " V" << endl;
  cout << indent_str << "Vth       = " << setw(12) << Vth       << " V" << endl;
  cout << indent_str << "I_on_n    = " << setw(12) << I_on_n    << " A/um" << endl;
  cout << indent_str << "I_on_p    = " << setw(12) << I_on_p    << " A/um" << endl;
  cout << indent_str << "I_off_n   = " << setw(12) << I_off_n   << " A/um" << endl;
  cout << indent_str << "I_off_p   = " << setw(12) << I_off_p   << " A/um" << endl;
  cout << indent_str << "C_ox      = " << setw(12) << C_ox      << " F/um^2" << endl;
  cout << indent_str << "t_ox      = " << setw(12) << t_ox      << " um" << endl;
  cout << indent_str << "n_to_p_eff_curr_drv_ratio = " << n_to_p_eff_curr_drv_ratio << endl;
}
**/

bool DeviceType::isEqual(const DeviceType& dev)
{
    if (!is_equal(C_g_ideal, dev.C_g_ideal)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(C_fringe, dev.C_fringe)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }

    if (!is_equal(C_overlap, dev.C_overlap)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(C_junc, dev.C_junc)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(C_junc_sidewall, dev.C_junc_sidewall)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(l_phy, dev.l_phy)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(l_elec, dev.l_elec)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(R_nch_on, dev.R_nch_on)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(R_pch_on, dev.R_pch_on)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(Vdd, dev.Vdd)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(Vth, dev.Vth)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    ////	if( !is_equal(Vcc_min , dev.Vcc_min)) {display(0); cout << "\n\n\n"; dev.display(0);assert(false);}
    if (!is_equal(I_on_n, dev.I_on_n)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(I_on_p, dev.I_on_p)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(I_off_n, dev.I_off_n)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(I_off_p, dev.I_off_p)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(I_g_on_n, dev.I_g_on_n)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(I_g_on_p, dev.I_g_on_p)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(C_ox, dev.C_ox)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(t_ox, dev.t_ox)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(n_to_p_eff_curr_drv_ratio, dev.n_to_p_eff_curr_drv_ratio)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(long_channel_leakage_reduction, dev.long_channel_leakage_reduction)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }
    if (!is_equal(Mobility_n, dev.Mobility_n)) {
        display(0);
        cout << "\n\n\n";
        dev.display(0);
        assert(false);
    }

    // auxilary parameters
    /// if( !is_equal(Vdsat , dev.Vdsat)) {display(0); cout << "\n\n\n"; dev.display(0); assert(false);}
    /// if( !is_equal(gmp_to_gmn_multiplier , dev.gmp_to_gmn_multiplier)) {display(0); cout << "\n\n\n"; dev.display(0); assert(false);}

    return true;
}
