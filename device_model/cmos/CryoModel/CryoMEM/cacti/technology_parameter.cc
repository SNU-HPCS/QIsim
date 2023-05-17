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
#include <cstdint>
#include <cstring>
#include <cassert>

#include "basic_circuit.h"
#include "input_parameter.h"
#include "technology_parameter.h"
#include "global_cacti_input.h"
#include "cacti_interface.pb.h"
#include "io.h"
#include "tsv.h"
#include "enum/ram_cell_tech_type_num.h"

using namespace std;

TechnologyParameter g_tp;

void TechnologyParameter::display(uint32_t indent)
{
    string indent_str(indent, ' ');

    cout << indent_str << "ram_wl_stitching_overhead_ = " << setw(12) << ram_wl_stitching_overhead_ << " um" << endl;
    cout << indent_str << "min_w_nmos_                = " << setw(12) << min_w_nmos_ << " um" << endl;
    cout << indent_str << "max_w_nmos_                = " << setw(12) << max_w_nmos_ << " um" << endl;
    cout << indent_str << "max_w_nmos_dec             = " << setw(12) << max_w_nmos_dec << " um" << endl;
    cout << indent_str << "unit_len_wire_del          = " << setw(12) << unit_len_wire_del << " s/um^2" << endl;
    cout << indent_str << "FO4                        = " << setw(12) << FO4 << " s" << endl;
    cout << indent_str << "kinv                       = " << setw(12) << kinv << " s" << endl;
    cout << indent_str << "vpp                        = " << setw(12) << vpp << " V" << endl;
    cout << indent_str << "w_sense_en                 = " << setw(12) << w_sense_en << " um" << endl;
    cout << indent_str << "w_sense_n                  = " << setw(12) << w_sense_n << " um" << endl;
    cout << indent_str << "w_sense_p                  = " << setw(12) << w_sense_p << " um" << endl;
    cout << indent_str << "sense_delay                = " << setw(12) << sense_delay << " um" << endl;
    cout << indent_str << "sense_dy_power             = " << setw(12) << sense_dy_power << " um" << endl;
    cout << indent_str << "w_iso                      = " << setw(12) << w_iso << " um" << endl;
    cout << indent_str << "w_poly_contact             = " << setw(12) << w_poly_contact << " um" << endl;
    cout << indent_str << "spacing_poly_to_poly       = " << setw(12) << spacing_poly_to_poly << " um" << endl;
    cout << indent_str << "spacing_poly_to_contact    = " << setw(12) << spacing_poly_to_contact << " um" << endl;
    cout << endl;
    cout << indent_str << "tsv_pitch                  = " << setw(12) << tsv_pitch << " um" << endl;
    cout << indent_str << "tsv_diameter               = " << setw(12) << tsv_diameter << " um" << endl;
    cout << indent_str << "tsv_length                 = " << setw(12) << tsv_length << " um" << endl;
    cout << indent_str << "tsv_dielec_thickness       = " << setw(12) << tsv_dielec_thickness << " um" << endl;
    cout << indent_str << "tsv_contact_resistance     = " << setw(12) << tsv_contact_resistance << " um" << endl;
    cout << indent_str << "tsv_depletion_width        = " << setw(12) << tsv_depletion_width << " um" << endl;
    cout << indent_str << "tsv_liner_dielectric_constant= " << setw(12) << tsv_liner_dielectric_constant << " um" << endl;
    cout << endl;
    cout << indent_str << "tsv_parasitic_capacitance_fine= " << setw(12) << tsv_parasitic_capacitance_fine << " um" << endl;
    cout << indent_str << "tsv_parasitic_resistance_fine = " << setw(12) << tsv_parasitic_resistance_fine << " um" << endl;
    cout << indent_str << "tsv_minimum_area_fine         = " << setw(12) << tsv_minimum_area_fine << " um" << endl;
    cout << indent_str << "tsv_parasitic_capacitance_coarse= " << setw(12) << tsv_parasitic_capacitance_coarse << " um" << endl;
    cout << indent_str << "tsv_parasitic_resistance_coarse = " << setw(12) << tsv_parasitic_resistance_coarse << " um" << endl;
    cout << indent_str << "tsv_minimum_area_coarse         = " << setw(12) << tsv_minimum_area_coarse << " um" << endl;
    cout << endl;
    cout << indent_str << "w_comp_inv_p1              = " << setw(12) << w_comp_inv_p1 << " um" << endl;
    cout << indent_str << "w_comp_inv_p2              = " << setw(12) << w_comp_inv_p2 << " um" << endl;
    cout << indent_str << "w_comp_inv_p3              = " << setw(12) << w_comp_inv_p3 << " um" << endl;
    cout << indent_str << "w_comp_inv_n1              = " << setw(12) << w_comp_inv_n1 << " um" << endl;
    cout << indent_str << "w_comp_inv_n2              = " << setw(12) << w_comp_inv_n2 << " um" << endl;
    cout << indent_str << "w_comp_inv_n3              = " << setw(12) << w_comp_inv_n3 << " um" << endl;
    cout << indent_str << "w_eval_inv_p               = " << setw(12) << w_eval_inv_p << " um" << endl;
    cout << indent_str << "w_eval_inv_n               = " << setw(12) << w_eval_inv_n << " um" << endl;
    cout << indent_str << "w_comp_n                   = " << setw(12) << w_comp_n << " um" << endl;
    cout << indent_str << "w_comp_p                   = " << setw(12) << w_comp_p << " um" << endl;
    cout << endl;
    cout << indent_str << "dram_cell_I_on             = " << setw(12) << dram_cell_I_on << " A/um" << endl;
    cout << indent_str << "dram_cell_Vdd              = " << setw(12) << dram_cell_Vdd << " V" << endl;
    cout << indent_str << "dram_cell_I_off_worst_case_len_temp = " << setw(12) << dram_cell_I_off_worst_case_len_temp << " A/um" << endl;
    cout << indent_str << "dram_cell_C                = " << setw(12) << dram_cell_C << " F" << endl;
    cout << indent_str << "gm_sense_amp_latch         = " << setw(12) << gm_sense_amp_latch << " F/s" << endl;
    cout << endl;
    cout << indent_str << "w_nmos_b_mux               = " << setw(12) << w_nmos_b_mux << " um" << endl;
    cout << indent_str << "w_nmos_sa_mux              = " << setw(12) << w_nmos_sa_mux << " um" << endl;
    cout << indent_str << "w_pmos_bl_precharge        = " << setw(12) << w_pmos_bl_precharge << " um" << endl;
    cout << indent_str << "w_pmos_bl_eq               = " << setw(12) << w_pmos_bl_eq << " um" << endl;
    cout << indent_str << "MIN_GAP_BET_P_AND_N_DIFFS  = " << setw(12) << MIN_GAP_BET_P_AND_N_DIFFS << " um" << endl;
    cout << indent_str << "MIN_GAP_BET_SAME_TYPE_DIFFS= " << setw(12) << MIN_GAP_BET_SAME_TYPE_DIFFS << " um" << endl;
    cout << indent_str << "HPOWERRAIL                 = " << setw(12) << HPOWERRAIL << " um" << endl;
    cout << indent_str << "cell_h_def                 = " << setw(12) << cell_h_def << " um" << endl;
    cout << endl;
    cout << indent_str << "chip_layout_overhead       = " << setw(12) << chip_layout_overhead << " um" << endl;
    cout << indent_str << "macro_layout_overhead      = " << setw(12) << macro_layout_overhead << " um" << endl;
    cout << indent_str << "sckt_co_eff                = " << setw(12) << sckt_co_eff << " um" << endl;
    cout << indent_str << "fringe_cap                 = " << setw(12) << fringe_cap << " um" << endl;
    cout << indent_str << "h_dec                      = " << setw(12) << h_dec << " um" << endl;
    cout << endl;
    cout << indent_str << "SRAM cell transistor: " << endl;
    sram_cell.display(indent + 2);

    cout << endl;
    cout << indent_str << "DRAM access transistor: " << endl;
    dram_acc.display(indent + 2);

    cout << endl;
    cout << indent_str << "DRAM wordline transistor: " << endl;
    dram_wl.display(indent + 2);

    cout << endl;
    cout << indent_str << "peripheral global transistor: " << endl;
    peri_global.display(indent + 2);

    cout << endl;
    cout << indent_str << "wire local" << endl;
    wire_local.display(indent + 2);

    cout << endl;
    cout << indent_str << "wire inside mat" << endl;
    wire_inside_mat.display(indent + 2);

    cout << endl;
    cout << indent_str << "wire outside mat" << endl;
    wire_outside_mat.display(indent + 2);

    cout << endl;
    cout << indent_str << "SRAM" << endl;
    sram.display(indent + 2);

    cout << endl;
    cout << indent_str << "DRAM" << endl;
    dram.display(indent + 2);
}

#define PRINT(A, X) cout << A << ": " << X << " , " << tech.X << endl

bool TechnologyParameter::isEqual(const TechnologyParameter& tech)
{
    if (!is_equal(ram_wl_stitching_overhead_, tech.ram_wl_stitching_overhead_)) {
        assert(false);
    }  // fs
    if (!is_equal(min_w_nmos_, tech.min_w_nmos_)) {
        assert(false);
    }  // fs
    if (!is_equal(max_w_nmos_, tech.max_w_nmos_)) {
        assert(false);
    }  // fs
    if (!is_equal(max_w_nmos_dec, tech.max_w_nmos_dec)) {
        assert(false);
    }  // fs+ ram_cell_tech_type
    if (!is_equal(unit_len_wire_del, tech.unit_len_wire_del)) {
        assert(false);
    }  // wire_inside_mat
    if (!is_equal(FO4, tech.FO4)) {
        assert(false);
    }  // fs
    if (!is_equal(kinv, tech.kinv)) {
        assert(false);
    }  // fs
    if (!is_equal(vpp, tech.vpp)) {
        assert(false);
    }  // input
    if (!is_equal(w_sense_en, tech.w_sense_en)) {
        assert(false);
    }  // fs
    if (!is_equal(w_sense_n, tech.w_sense_n)) {
        assert(false);
    }  // fs
    if (!is_equal(w_sense_p, tech.w_sense_p)) {
        assert(false);
    }  // fs
    if (!is_equal(sense_delay, tech.sense_delay)) {
        PRINT("sense_delay", sense_delay);
        assert(false);
    }  // input
    if (!is_equal(sense_dy_power, tech.sense_dy_power)) {
        assert(false);
    }  // input
    if (!is_equal(w_iso, tech.w_iso)) {
        assert(false);
    }  // fs
    if (!is_equal(w_poly_contact, tech.w_poly_contact)) {
        assert(false);
    }  // fs
    if (!is_equal(spacing_poly_to_poly, tech.spacing_poly_to_poly)) {
        assert(false);
    }  // fs
    if (!is_equal(spacing_poly_to_contact, tech.spacing_poly_to_contact)) {
        assert(false);
    }  // fs

    // CACTI3D auxilary variables
    /// if(!is_equal(tsv_pitch,tech.tsv_pitch)) {assert(false);}
    /// if(!is_equal(tsv_diameter,tech.tsv_diameter)) {assert(false);}
    /// if(!is_equal(tsv_length,tech.tsv_length)) {assert(false);}
    /// if(!is_equal(tsv_dielec_thickness,tech.tsv_dielec_thickness)) {assert(false);}
    /// if(!is_equal(tsv_contact_resistance,tech.tsv_contact_resistance)) {assert(false);}
    /// if(!is_equal(tsv_depletion_width,tech.tsv_depletion_width)) {assert(false);}
    /// if(!is_equal(tsv_liner_dielectric_constant,tech.tsv_liner_dielectric_constant)) {assert(false);}

    // CACTI3DD TSV params

    if (!is_equal(tsv_parasitic_capacitance_fine, tech.tsv_parasitic_capacitance_fine)) {
        PRINT("tsv_parasitic_capacitance_fine", tsv_parasitic_capacitance_fine);
        assert(false);
    }
    if (!is_equal(tsv_parasitic_resistance_fine, tech.tsv_parasitic_resistance_fine)) {
        assert(false);
    }
    if (!is_equal(tsv_minimum_area_fine, tech.tsv_minimum_area_fine)) {
        assert(false);
    }

    if (!is_equal(tsv_parasitic_capacitance_coarse, tech.tsv_parasitic_capacitance_coarse)) {
        assert(false);
    }
    if (!is_equal(tsv_parasitic_resistance_coarse, tech.tsv_parasitic_resistance_coarse)) {
        assert(false);
    }
    if (!is_equal(tsv_minimum_area_coarse, tech.tsv_minimum_area_coarse)) {
        assert(false);
    }

    // fs
    if (!is_equal(w_comp_inv_p1, tech.w_comp_inv_p1)) {
        assert(false);
    }
    if (!is_equal(w_comp_inv_p2, tech.w_comp_inv_p2)) {
        assert(false);
    }
    if (!is_equal(w_comp_inv_p3, tech.w_comp_inv_p3)) {
        assert(false);
    }
    if (!is_equal(w_comp_inv_n1, tech.w_comp_inv_n1)) {
        assert(false);
    }
    if (!is_equal(w_comp_inv_n2, tech.w_comp_inv_n2)) {
        assert(false);
    }
    if (!is_equal(w_comp_inv_n3, tech.w_comp_inv_n3)) {
        assert(false);
    }
    if (!is_equal(w_eval_inv_p, tech.w_eval_inv_p)) {
        assert(false);
    }
    if (!is_equal(w_eval_inv_n, tech.w_eval_inv_n)) {
        assert(false);
    }
    if (!is_equal(w_comp_n, tech.w_comp_n)) {
        assert(false);
    }
    if (!is_equal(w_comp_p, tech.w_comp_p)) {
        assert(false);
    }

    if (!is_equal(dram_cell_I_on, tech.dram_cell_I_on)) {
        assert(false);
    }  // ram_cell_tech_type
    if (!is_equal(dram_cell_Vdd, tech.dram_cell_Vdd)) {
        assert(false);
    }
    if (!is_equal(dram_cell_I_off_worst_case_len_temp, tech.dram_cell_I_off_worst_case_len_temp)) {
        assert(false);
    }
    if (!is_equal(dram_cell_C, tech.dram_cell_C)) {
        assert(false);
    }
    if (!is_equal(gm_sense_amp_latch, tech.gm_sense_amp_latch)) {
        assert(false);
    }  // depends on many things

    if (!is_equal(w_nmos_b_mux, tech.w_nmos_b_mux)) {
        assert(false);
    }  // fs
    if (!is_equal(w_nmos_sa_mux, tech.w_nmos_sa_mux)) {
        assert(false);
    }  // fs
    if (!is_equal(w_pmos_bl_precharge, tech.w_pmos_bl_precharge)) {
        PRINT("w_pmos_bl_precharge", w_pmos_bl_precharge);
        assert(false);
    }  // fs
    if (!is_equal(w_pmos_bl_eq, tech.w_pmos_bl_eq)) {
        assert(false);
    }  // fs
    if (!is_equal(MIN_GAP_BET_P_AND_N_DIFFS, tech.MIN_GAP_BET_P_AND_N_DIFFS)) {
        assert(false);
    }  // fs
    if (!is_equal(MIN_GAP_BET_SAME_TYPE_DIFFS, tech.MIN_GAP_BET_SAME_TYPE_DIFFS)) {
        assert(false);
    }  // fs
    if (!is_equal(HPOWERRAIL, tech.HPOWERRAIL)) {
        assert(false);
    }  // fs
    if (!is_equal(cell_h_def, tech.cell_h_def)) {
        assert(false);
    }  // fs

    if (!is_equal(chip_layout_overhead, tech.chip_layout_overhead)) {
        assert(false);
    }  // input
    if (!is_equal(macro_layout_overhead, tech.macro_layout_overhead)) {
        cout << macro_layout_overhead << " vs. " << tech.macro_layout_overhead << endl;
        assert(false);
    }
    if (!is_equal(sckt_co_eff, tech.sckt_co_eff)) {
        assert(false);
    }

    if (!is_equal(fringe_cap, tech.fringe_cap)) {
        PRINT("fringe_cap", fringe_cap);
        assert(false);
    }  // input

    if (h_dec != tech.h_dec) {
        assert(false);
    }  // ram_cell_tech_type

    cout << "sram_cell \n";
    sram_cell.isEqual(tech.sram_cell);  // SRAM cell transistor
    cout << "dram_acc \n";
    dram_acc.isEqual(tech.dram_acc);  // DRAM access transistor
    cout << "dram_wl \n";
    dram_wl.isEqual(tech.dram_wl);  // DRAM wordline transistor
    cout << "peri_global \n";
    peri_global.isEqual(tech.peri_global);  // peripheral global
    cout << "cam_cell \n";
    cam_cell.isEqual(tech.cam_cell);  // SRAM cell transistor

    cout << "sleep_tx \n";
    sleep_tx.isEqual(tech.sleep_tx);  // Sleep transistor cell transistor

    cout << "wire_local \n";
    wire_local.isEqual(tech.wire_local);
    cout << "wire_inside_mat \n";
    wire_inside_mat.isEqual(tech.wire_inside_mat);
    cout << "wire_outside_mat \n";
    wire_outside_mat.isEqual(tech.wire_outside_mat);

    cout << "scaling_factor \n";
    scaling_factor.isEqual(tech.scaling_factor);
    cout << "sram: \n";
    sram.isEqual(tech.sram);
    cout << "dram: \n";
    dram.isEqual(tech.dram);
    cout << "cam: \n";
    cam.isEqual(tech.cam);

    return true;
}

void TechnologyParameter::find_upper_and_lower_tech(double technology, int& tech_lo, string& in_file_lo, int& tech_hi, string& in_file_hi)
{
    if (technology < 181 && technology > 179) {
        tech_lo    = 180;
        in_file_lo = "tech_params/180nm.dat";
        tech_hi    = 180;
        in_file_hi = "tech_params/180nm.dat";
    }
    else if (technology < 91 && technology > 89)
    {
        tech_lo    = 90;
        in_file_lo = "tech_params/90nm.dat";
        tech_hi    = 90;
        in_file_hi = "tech_params/90nm.dat";
    }
    else if (technology < 66 && technology > 64)
    {
        tech_lo    = 65;
        in_file_lo = "tech_params/65nm.dat";
        tech_hi    = 65;
        in_file_hi = "tech_params/65nm.dat";
    }
    else if (technology < 46 && technology > 44)
    {
        tech_lo    = 45;
        in_file_lo = "tech_params/45nm.dat";
        tech_hi    = 45;
        in_file_hi = "tech_params/45nm.dat";
    }
    else if (technology < 33 && technology > 31)
    {
        tech_lo    = 32;
        in_file_lo = "tech_params/32nm.dat";
        tech_hi    = 32;
        in_file_hi = "tech_params/32nm.dat";
    }
    else if (technology < 23 && technology > 21)
    {
        tech_lo    = 22;
        in_file_lo = "tech_params/22nm.dat";
        tech_hi    = 22;
        in_file_hi = "tech_params/22nm.dat";
    }
    else if (technology < 180 && technology > 90)
    {
        tech_lo    = 180;
        in_file_lo = "tech_params/180nm.dat";
        tech_hi    = 90;
        in_file_hi = "tech_params/90nm.dat";
    }
    else if (technology < 90 && technology > 65)
    {
        tech_lo    = 90;
        in_file_lo = "tech_params/90nm.dat";
        tech_hi    = 65;
        in_file_hi = "tech_params/65nm.dat";
    }
    else if (technology < 65 && technology > 45)
    {
        tech_lo    = 65;
        in_file_lo = "tech_params/65nm.dat";
        tech_hi    = 45;
        in_file_hi = "tech_params/45nm.dat";
    }
    else if (technology < 45 && technology > 32)
    {
        tech_lo    = 45;
        in_file_lo = "tech_params/45nm.dat";
        tech_hi    = 32;
        in_file_hi = "tech_params/32nm.dat";
    }
    else if (technology < 32 && technology > 22)
    {
        tech_lo    = 32;
        in_file_lo = "tech_params/32nm.dat";
        tech_hi    = 22;
        in_file_hi = "tech_params/22nm.dat";
    }
    /**
    else if (technology < 22 && technology > 16)
    {
        tech_lo = 22;
        in_file_lo = "tech_params/22nm.dat";
        tech_hi = 16;
        in_file_hi = "tech_params/16nm.dat";
    }
    **/
    else
    {
        cout << "Invalid technology nodes" << endl;
        exit(0);
    }
}

void TechnologyParameter::assign_tsv(const string& in_file)
{
    FILE* fp;
    char  line[5000];
    for (int iter = 0; iter < 2; iter++)  // 0:fine 1:coarse
    {
        int tsv_type;
        if (iter == 0) {
            tsv_type = g_ip->tsv_is_subarray_type;
        }
        else
        {
            tsv_type = g_ip->tsv_os_bank_type;
        }
        fp = fopen(in_file.c_str(), "r");
        while (fscanf(fp, "%[^\n]\n", line) != EOF) {
            if (!strncmp("-tsv_pitch", line, strlen("-tsv_pitch"))) {
                tsv_pitch = scan_input_double_tsv_type(line, "-tsv_pitch", "F/um", g_ip->ic_proj_type, tsv_type, g_ip->print_detail_debug);
                continue;
            }
            if (!strncmp("-tsv_diameter", line, strlen("-tsv_diameter"))) {
                tsv_diameter = scan_input_double_tsv_type(line, "-tsv_diameter", "F/um", g_ip->ic_proj_type, tsv_type, g_ip->print_detail_debug);
                continue;
            }
            if (!strncmp("-tsv_length", line, strlen("-tsv_length"))) {
                tsv_length = scan_input_double_tsv_type(line, "-tsv_length", "F/um", g_ip->ic_proj_type, tsv_type, g_ip->print_detail_debug);
                continue;
            }
            if (!strncmp("-tsv_dielec_thickness", line, strlen("-tsv_dielec_thickness"))) {
                tsv_dielec_thickness
                    = scan_input_double_tsv_type(line, "-tsv_dielec_thickness", "F/um", g_ip->ic_proj_type, tsv_type, g_ip->print_detail_debug);
                continue;
            }
            if (!strncmp("-tsv_contact_resistance", line, strlen("-tsv_contact_resistance"))) {
                tsv_contact_resistance
                    = scan_input_double_tsv_type(line, "-tsv_contact_resistance", "F/um", g_ip->ic_proj_type, tsv_type, g_ip->print_detail_debug);
                continue;
            }
            if (!strncmp("-tsv_depletion_width", line, strlen("-tsv_depletion_width"))) {
                tsv_depletion_width = scan_input_double_tsv_type(line, "-tsv_depletion_width", "F/um", g_ip->ic_proj_type, tsv_type, g_ip->print_detail_debug);
                continue;
            }
            if (!strncmp("-tsv_liner_dielectric_cons", line, strlen("-tsv_liner_dielectric_cons"))) {
                tsv_liner_dielectric_constant
                    = scan_input_double_tsv_type(line, "-tsv_liner_dielectric_cons", "F/um", g_ip->ic_proj_type, tsv_type, g_ip->print_detail_debug);
                continue;
            }

            tsv_length *= g_ip->num_die_3d;
            if (iter == 0) {
                tsv_parasitic_resistance_fine = tsv_resistance(BULK_CU_RESISTIVITY, tsv_length, tsv_diameter, tsv_contact_resistance);
                tsv_parasitic_capacitance_fine
                    = tsv_capacitance(tsv_length, tsv_diameter, tsv_pitch, tsv_dielec_thickness, tsv_liner_dielectric_constant, tsv_depletion_width);
                tsv_minimum_area_fine = tsv_area(tsv_pitch);
            }
            else
            {
                tsv_parasitic_resistance_coarse = tsv_resistance(BULK_CU_RESISTIVITY, tsv_length, tsv_diameter, tsv_contact_resistance);
                tsv_parasitic_capacitance_coarse
                    = tsv_capacitance(tsv_length, tsv_diameter, tsv_pitch, tsv_dielec_thickness, tsv_liner_dielectric_constant, tsv_depletion_width);
                tsv_minimum_area_coarse = tsv_area(tsv_pitch);
            }
        }

        fclose(fp);
    }
}

void TechnologyParameter::init(double technology, bool is_tag)
{
    FILE* fp;
    reset();
    char line[5000];
    // char temp_var[5000];

    uint32_t ram_cell_tech_type    = (is_tag) ? g_ip->tag_arr_ram_cell_tech_type : g_ip->data_arr_ram_cell_tech_type;
    uint32_t peri_global_tech_type = (is_tag) ? g_ip->tag_arr_peri_global_tech_type : g_ip->data_arr_peri_global_tech_type;

    int    tech_lo, tech_hi;
    string in_file_lo, in_file_hi;

    double alpha;  // used for technology interpolation

    technology = technology * 1000.0;  // in the unit of nm

    find_upper_and_lower_tech(technology, tech_lo, in_file_lo, tech_hi, in_file_hi);
    // excluding some cases.
    if ((tech_lo == 22) && (tech_hi == 22)) {
        if (ram_cell_tech_type == 3) {
            cout << "current version does not support eDRAM technologies at 22nm" << endl;
            exit(0);
        }
    }

    if (tech_lo == tech_hi) {
        alpha = 1;
    }
    else
    {
        alpha = (technology - tech_hi) / (tech_lo - tech_hi);
    }

    fp                                  = fopen(in_file_lo.c_str(), "r");
    dram_cell_I_on                      = 0;
    dram_cell_Vdd                       = 0;
    dram_cell_C                         = 0;
    dram_cell_I_off_worst_case_len_temp = 0;
    vpp                                 = 0;
    macro_layout_overhead               = 0;
    chip_layout_overhead                = 0;
    sckt_co_eff                         = 0;
    while (fscanf(fp, "%[^\n]\n", line) != EOF) {
        if (!strncmp("-dram_cell_I_on", line, strlen("-dram_cell_I_on"))) {
            dram_cell_I_on += alpha * scan_five_input_double(line, "-dram_cell_I_on", "F/um", ram_cell_tech_type, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-dram_cell_Vdd", line, strlen("-dram_cell_Vdd"))) {
            dram_cell_Vdd += alpha * scan_five_input_double(line, "-dram_cell_Vdd", "F/um", ram_cell_tech_type, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-dram_cell_C", line, strlen("-dram_cell_C"))) {
            dram_cell_C += alpha * scan_five_input_double(line, "-dram_cell_C", "F/um", ram_cell_tech_type, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-dram_cell_I_off_worst_case_len_temp", line, strlen("-dram_cell_I_off_worst_case_len_temp"))) {
            dram_cell_I_off_worst_case_len_temp
                += alpha * scan_five_input_double(line, "-dram_cell_I_off_worst_case_len_temp", "F/um", ram_cell_tech_type, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-vpp", line, strlen("-vpp"))) {
            vpp += alpha * scan_five_input_double(line, "-vpp", "F/um", ram_cell_tech_type, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-sckt_co_eff", line, strlen("-sckt_co_eff"))) {
            sckt_co_eff += alpha * scan_single_input_double(line, "-sckt_co_eff", "F/um", g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-chip_layout_overhead", line, strlen("-chip_layout_overhead"))) {
            chip_layout_overhead += alpha * scan_single_input_double(line, "-chip_layout_overhead", "F/um", g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-macro_layout_overhead", line, strlen("-macro_layout_overhead"))) {
            macro_layout_overhead += alpha * scan_single_input_double(line, "-macro_layout_overhead", "F/um", g_ip->print_detail_debug);
            continue;
        }
    }
    fclose(fp);

    DeviceType peri_global_lo, peri_global_hi;
    peri_global_lo.assign(in_file_lo, peri_global_tech_type, g_ip->temp);
    peri_global_hi.assign(in_file_hi, peri_global_tech_type, g_ip->temp);
    peri_global.interpolate(alpha, peri_global_lo, peri_global_hi);
    // in the original code some field of this devide has not been initialized/
    // I make them 0 for compatibility.
    /// peri_global.I_on_p = 0.0;

    DeviceType sleep_tx_lo, sleep_tx_hi;
    sleep_tx_lo.assign(in_file_lo, 1, g_ip->temp);
    sleep_tx_hi.assign(in_file_hi, 1, g_ip->temp);
    sleep_tx.interpolate(alpha, sleep_tx_lo, sleep_tx_hi);

    DeviceType sram_cell_lo, sram_cell_hi;
    sram_cell_lo.assign(in_file_lo, ram_cell_tech_type, g_ip->temp);
    sram_cell_hi.assign(in_file_hi, ram_cell_tech_type, g_ip->temp);
    sram_cell.interpolate(alpha, sram_cell_lo, sram_cell_hi);
    // in the original code some field of this devide has not been initialized/
    // I make them 0 for compatibility.
    // sram_cell.Vdd=0.0;
    /// sram_cell.I_on_p=0.0;
    /// sram_cell.C_ox=0.0;

    DeviceType dram_acc_lo, dram_acc_hi;
    dram_acc_lo.assign(in_file_lo, (ram_cell_tech_type == comm_dram ? ram_cell_tech_type : dram_cell_tech_flavor), g_ip->temp);
    dram_acc_hi.assign(in_file_hi, (ram_cell_tech_type == comm_dram ? ram_cell_tech_type : dram_cell_tech_flavor), g_ip->temp);
    dram_acc.interpolate(alpha, dram_acc_lo, dram_acc_hi);
    // dram_acc exceptions
    // dram_acc.R_nch_on = g_tp.dram_cell_Vdd / g_tp.dram_acc.I_on_n;
    // dram_acc.R_pch_on = 0;
    if (tech_lo <= 22) {
    }
    else if (tech_lo <= 32)
    {
        if (ram_cell_tech_type == lp_dram)
            dram_acc.Vth = 0.44129;
        else
            dram_acc.Vth = 1.0;
    }
    else if (tech_lo <= 45)
    {
        if (ram_cell_tech_type == lp_dram)
            dram_acc.Vth = 0.44559;
        else
            dram_acc.Vth = 1.0;
    }
    else if (tech_lo <= 65)
    {
        if (ram_cell_tech_type == lp_dram)
            dram_acc.Vth = 0.43806;
        else
            dram_acc.Vth = 1.0;
    }
    else if (tech_lo <= 90)
    {
        if (ram_cell_tech_type == lp_dram)
            dram_acc.Vth = 0.4545;
        else
            dram_acc.Vth = 1.0;
    }
    // in the original code some field of this devide has not been initialized/
    // I make them 0 for compatibility.
    dram_acc.Vdd                       = 0.0;
    dram_acc.I_on_p                    = 0.0;
    dram_acc.I_off_n                   = 0.0;
    dram_acc.I_off_p                   = 0.0;
    dram_acc.C_ox                      = 0.0;
    dram_acc.t_ox                      = 0.0;
    dram_acc.n_to_p_eff_curr_drv_ratio = 0.0;

    DeviceType dram_wl_lo, dram_wl_hi;
    dram_wl_lo.assign(in_file_lo, (ram_cell_tech_type == comm_dram ? ram_cell_tech_type : dram_cell_tech_flavor), g_ip->temp);
    dram_wl_hi.assign(in_file_hi, (ram_cell_tech_type == comm_dram ? ram_cell_tech_type : dram_cell_tech_flavor), g_ip->temp);
    dram_wl.interpolate(alpha, dram_wl_lo, dram_wl_hi);
    // in the original code some field of this devide has not been initialized/
    // I make them 0 for compatibility.
    dram_wl.Vdd    = 0.0;
    dram_wl.Vth    = 0.0;
    dram_wl.I_on_p = 0.0;
    dram_wl.C_ox   = 0.0;
    dram_wl.t_ox   = 0.0;

    // if ram_cell_tech_type is not 3 or 4 ( which means edram and comm-dram)
    // then reset dram_wl dram_acc

    if (ram_cell_tech_type < 3) {
        dram_acc.reset();
        dram_wl.reset();
    }

    DeviceType cam_cell_lo, cam_cell_hi;
    cam_cell_lo.assign(in_file_lo, ram_cell_tech_type, g_ip->temp);
    cam_cell_hi.assign(in_file_hi, ram_cell_tech_type, g_ip->temp);
    cam_cell.interpolate(alpha, cam_cell_lo, cam_cell_hi);

    MemoryType dram_lo, dram_hi;
    dram_lo.assign(in_file_lo, ram_cell_tech_type, 2);  // cell_type = dram(2)
    dram_hi.assign(in_file_hi, ram_cell_tech_type, 2);
    dram.interpolate(alpha, dram_lo, dram_hi);

    MemoryType sram_lo, sram_hi;
    sram_lo.assign(in_file_lo, ram_cell_tech_type, 0);  // cell_type = sram(0)
    sram_hi.assign(in_file_hi, ram_cell_tech_type, 0);
    sram.interpolate(alpha, sram_lo, sram_hi);
    // sram cell execptions
    /*sram_lo.assign(in_file_lo, 0, g_ip->temp);
    sram.cell_a_w =sram_lo.cell_a_w;
    sram.b_h = sram_lo.b_h;
    sram.b_w = sram_lo.b_w;
*/
    MemoryType cam_lo, cam_hi;
    cam_lo.assign(in_file_lo, ram_cell_tech_type, 1);  // cell_type = sram(0)
    cam_hi.assign(in_file_hi, ram_cell_tech_type, 1);
    cam.interpolate(alpha, cam_lo, cam_hi);

    ScalingFactor scaling_factor_lo, scaling_factor_hi;
    scaling_factor_lo.assign(in_file_lo);
    scaling_factor_hi.assign(in_file_hi);
    scaling_factor.interpolate(alpha, scaling_factor_lo, scaling_factor_hi);

    // vcc_min
    peri_global.Vcc_min += (alpha * peri_global_lo.Vdd + (1 - alpha) * peri_global_hi.Vdd) * 0.35;
    sleep_tx.Vcc_min += (alpha * sleep_tx_lo.Vdd + (1 - alpha) * sleep_tx_hi.Vdd);
    sram_cell.Vcc_min += (alpha * sram_cell_lo.Vdd + (1 - alpha) * sram_cell_hi.Vdd) * 0.65;

    fp = fopen(in_file_hi.c_str(), "r");

    while (fscanf(fp, "%[^\n]\n", line) != EOF) {
        if (!strncmp("-sense_delay", line, strlen("-sense_delay"))) {
            sense_delay = scan_single_input_double(line, "-sense_delay", "F/um", g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-sense_dy_power", line, strlen("-sense_dy_power"))) {
            sense_dy_power = scan_single_input_double(line, "-sense_dy_power", "F/um", g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-sckt_co_eff", line, strlen("-sckt_co_eff"))) {
            sckt_co_eff += (1 - alpha) * scan_single_input_double(line, "-sckt_co_eff", "F/um", g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-chip_layout_overhead", line, strlen("-chip_layout_overhead"))) {
            chip_layout_overhead += (1 - alpha) * scan_single_input_double(line, "-chip_layout_overhead", "F/um", g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-macro_layout_overhead", line, strlen("-macro_layout_overhead"))) {
            macro_layout_overhead += (1 - alpha) * scan_single_input_double(line, "-macro_layout_overhead", "F/um", g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-dram_cell_I_on", line, strlen("-dram_cell_I_on"))) {
            dram_cell_I_on += (1 - alpha) * scan_five_input_double(line, "-dram_cell_I_on", "F/um", ram_cell_tech_type, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-dram_cell_Vdd", line, strlen("-dram_cell_Vdd"))) {
            dram_cell_Vdd += (1 - alpha) * scan_five_input_double(line, "-dram_cell_Vdd", "F/um", ram_cell_tech_type, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-dram_cell_C", line, strlen("-dram_cell_C"))) {
            dram_cell_C += (1 - alpha) * scan_five_input_double(line, "-dram_cell_C", "F/um", ram_cell_tech_type, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-dram_cell_I_off_worst_case_len_temp", line, strlen("-dram_cell_I_off_worst_case_len_temp"))) {
            dram_cell_I_off_worst_case_len_temp
                += (1 - alpha) * scan_five_input_double(line, "-dram_cell_I_off_worst_case_len_temp", "F/um", ram_cell_tech_type, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-vpp", line, strlen("-vpp"))) {
            vpp += (1 - alpha) * scan_five_input_double(line, "-vpp", "F/um", ram_cell_tech_type, g_ip->print_detail_debug);
            continue;
        }
    }
    fclose(fp);

    // Currently we are not modeling the resistance/capacitance of poly anywhere.
    // Continuous function (or date have been processed) does not need linear interpolation
    w_comp_inv_p1 = 12.5 * g_ip->F_sz_um;  // this was 10 micron for the 0.8 micron process
    w_comp_inv_n1 = 7.5 * g_ip->F_sz_um;   // this was  6 micron for the 0.8 micron process
    w_comp_inv_p2 = 25 * g_ip->F_sz_um;    // this was 20 micron for the 0.8 micron process
    w_comp_inv_n2 = 15 * g_ip->F_sz_um;    // this was 12 micron for the 0.8 micron process
    w_comp_inv_p3 = 50 * g_ip->F_sz_um;    // this was 40 micron for the 0.8 micron process
    w_comp_inv_n3 = 30 * g_ip->F_sz_um;    // this was 24 micron for the 0.8 micron process
    w_eval_inv_p  = 100 * g_ip->F_sz_um;   // this was 80 micron for the 0.8 micron process
    w_eval_inv_n  = 50 * g_ip->F_sz_um;    // this was 40 micron for the 0.8 micron process
    w_comp_n      = 12.5 * g_ip->F_sz_um;  // this was 10 micron for the 0.8 micron process
    w_comp_p      = 37.5 * g_ip->F_sz_um;  // this was 30 micron for the 0.8 micron process

    MIN_GAP_BET_P_AND_N_DIFFS   = 5 * g_ip->F_sz_um;
    MIN_GAP_BET_SAME_TYPE_DIFFS = 1.5 * g_ip->F_sz_um;
    HPOWERRAIL                  = 2 * g_ip->F_sz_um;
    cell_h_def                  = 50 * g_ip->F_sz_um;
    w_poly_contact              = g_ip->F_sz_um;
    spacing_poly_to_contact     = g_ip->F_sz_um;
    spacing_poly_to_poly        = 1.5 * g_ip->F_sz_um;
    ram_wl_stitching_overhead_  = 7.5 * g_ip->F_sz_um;

    min_w_nmos_   = 3 * g_ip->F_sz_um / 2;
    max_w_nmos_   = 100 * g_ip->F_sz_um;
    w_iso         = 12.5 * g_ip->F_sz_um;  // was 10 micron for the 0.8 micron process
    w_sense_n     = 3.75 * g_ip->F_sz_um;  // sense amplifier N-trans; was 3 micron for the 0.8 micron process
    w_sense_p     = 7.5 * g_ip->F_sz_um;   // sense amplifier P-trans; was 6 micron for the 0.8 micron process
    w_sense_en    = 5 * g_ip->F_sz_um;     // Sense enable transistor of the sense amplifier; was 4 micron for the 0.8 micron process
    w_nmos_b_mux  = 6 * min_w_nmos_;
    w_nmos_sa_mux = 6 * min_w_nmos_;

    w_pmos_bl_precharge = 6 * pmos_to_nmos_sz_ratio() * min_w_nmos_;
    w_pmos_bl_eq        = pmos_to_nmos_sz_ratio() * min_w_nmos_;

    if (ram_cell_tech_type == comm_dram) {
        max_w_nmos_dec = 8 * g_ip->F_sz_um;
        h_dec          = 8;  // in the unit of memory cell height
    }
    else
    {
        max_w_nmos_dec = g_tp.max_w_nmos_;
        h_dec          = 4;  // in the unit of memory cell height
    }

    double gmn_sense_amp_latch = (peri_global.Mobility_n / 2) * peri_global.C_ox * (w_sense_n / peri_global.l_elec) * peri_global.Vdsat;
    double gmp_sense_amp_latch = peri_global.gmp_to_gmn_multiplier * gmn_sense_amp_latch;
    gm_sense_amp_latch         = gmn_sense_amp_latch + gmp_sense_amp_latch;

    /// cout << "wire_local " << g_ip->ic_proj_type << " " << ((ram_cell_tech_type == comm_dram)?3:0) << endl;
    InterconnectType wire_local_lo, wire_local_hi;
    wire_local_lo.assign(in_file_lo, g_ip->ic_proj_type, (ram_cell_tech_type == comm_dram) ? 3 : 0);
    wire_local_hi.assign(in_file_hi, g_ip->ic_proj_type, (ram_cell_tech_type == comm_dram) ? 3 : 0);
    wire_local.interpolate(alpha, wire_local_lo, wire_local_hi);

    /// cout << "wire_inside_mat " << g_ip->ic_proj_type << " " << g_ip->wire_is_mat_type << endl;
    InterconnectType wire_inside_mat_lo, wire_inside_mat_hi;
    wire_inside_mat_lo.assign(in_file_lo, g_ip->ic_proj_type, g_ip->wire_is_mat_type);
    wire_inside_mat_hi.assign(in_file_hi, g_ip->ic_proj_type, g_ip->wire_is_mat_type);
    wire_inside_mat.interpolate(alpha, wire_inside_mat_lo, wire_inside_mat_hi);

    /// cout << "wire_outside_mat " << g_ip->ic_proj_type << " " << g_ip->wire_os_mat_type << endl;
    InterconnectType wire_outside_mat_lo, wire_outside_mat_hi;
    wire_outside_mat_lo.assign(in_file_lo, g_ip->ic_proj_type, g_ip->wire_os_mat_type);
    wire_outside_mat_hi.assign(in_file_hi, g_ip->ic_proj_type, g_ip->wire_os_mat_type);
    wire_outside_mat.interpolate(alpha, wire_outside_mat_lo, wire_outside_mat_hi);

    unit_len_wire_del = wire_inside_mat.R_per_um * wire_inside_mat.C_per_um / 2;

    // assign value for TSV parameters

    assign_tsv(in_file_hi);

    fringe_cap = wire_local_hi.fringe_cap;  // fringe_cap is similar for all wire types.

    double rd              = tr_R_on(min_w_nmos_, NCH, 1);
    double p_to_n_sizing_r = pmos_to_nmos_sz_ratio();
    double c_load          = gate_C(min_w_nmos_ * (1 + p_to_n_sizing_r), 0.0);
    double tf              = rd * c_load;
    kinv                   = horowitz(0, tf, 0.5, 0.5, RISE);
    double KLOAD           = 1;
    c_load                 = KLOAD * (drain_C_(min_w_nmos_, NCH, 1, 1, cell_h_def) + drain_C_(min_w_nmos_ * p_to_n_sizing_r, PCH, 1, 1, cell_h_def)
                      + gate_C(min_w_nmos_ * 4 * (1 + p_to_n_sizing_r), 0.0));
    tf  = rd * c_load;
    FO4 = horowitz(0, tf, 0.5, 0.5, RISE);
}

void TechnologyParameter::overriding(const CactiInput::TechnologyParameter &tech_param){
    if (tech_param.has_sram_cell())   sram_cell.overriding(tech_param.sram_cell());
    if (tech_param.has_dram_acc())    dram_acc.overriding(tech_param.dram_acc());
    if (tech_param.has_dram_wl())     dram_wl.overriding(tech_param.dram_wl());
    if (tech_param.has_peri_global()) peri_global.overriding(tech_param.peri_global());

    if (tech_param.has_wire_local())       wire_local.overriding(tech_param.wire_local());
    if (tech_param.has_wire_inside_mat())  wire_inside_mat.overriding(tech_param.wire_inside_mat());
    if (tech_param.has_wire_outside_mat()) wire_outside_mat.overriding(tech_param.wire_outside_mat());

    if (tech_param.has_vpp())            vpp = tech_param.vpp();
    if (tech_param.has_dram_cell_i_on()) dram_cell_I_on = tech_param.dram_cell_i_on();
    if (tech_param.has_dram_cell_vdd())  dram_cell_Vdd = tech_param.dram_cell_vdd();

    if (tech_param.has_cache_sz())       g_ip->cache_sz = tech_param.cache_sz();
}

static void printing(const char* name, double value);
static void printing_int(const char* name, uint64_t value);

void init_tech_params(double technology, bool is_tag) {
    g_tp.init(technology, is_tag);
    if(GlobalCactiInput::get().has_tech_param())
        g_tp.overriding(GlobalCactiInput::get().tech_param());
}
void print_g_tp()
{
    printing("g_tp.peri_global.Vdd", g_tp.peri_global.Vdd);
    printing("g_tp.peri_global.Vcc_min", g_tp.peri_global.Vcc_min);
    printing("g_tp.peri_global.t_ox", g_tp.peri_global.t_ox);
    printing("g_tp.peri_global.Vth", g_tp.peri_global.Vth);
    printing("g_tp.peri_global.C_ox", g_tp.peri_global.C_ox);
    printing("g_tp.peri_global.C_g_ideal", g_tp.peri_global.C_g_ideal);
    printing("g_tp.peri_global.C_fringe", g_tp.peri_global.C_fringe);
    printing("g_tp.peri_global.C_junc", g_tp.peri_global.C_junc);
    printing("g_tp.peri_global.C_junc_sidewall", g_tp.peri_global.C_junc_sidewall);
    printing("g_tp.peri_global.l_phy", g_tp.peri_global.l_phy);
    printing("g_tp.peri_global.l_elec", g_tp.peri_global.l_elec);
    printing("g_tp.peri_global.I_on_n", g_tp.peri_global.I_on_n);
    printing("g_tp.peri_global.R_nch_on", g_tp.peri_global.R_nch_on);
    printing("g_tp.peri_global.R_pch_on", g_tp.peri_global.R_pch_on);
    printing("g_tp.peri_global.n_to_p_eff_curr_drv_ratio", g_tp.peri_global.n_to_p_eff_curr_drv_ratio);
    printing("g_tp.peri_global.long_channel_leakage_reduction", g_tp.peri_global.long_channel_leakage_reduction);
    printing("g_tp.peri_global.I_off_n", g_tp.peri_global.I_off_n);
    printing("g_tp.peri_global.I_off_p", g_tp.peri_global.I_off_p);
    printing("g_tp.peri_global.I_g_on_n", g_tp.peri_global.I_g_on_n);
    printing("g_tp.peri_global.I_g_on_p", g_tp.peri_global.I_g_on_p);

    printing("g_tp.peri_global.Mobility_n", g_tp.peri_global.Mobility_n);

    printing("g_tp.sleep_tx.Vdd", g_tp.sleep_tx.Vdd);
    printing("g_tp.sleep_tx.Vcc_min", g_tp.sleep_tx.Vcc_min);
    printing("g_tp.sleep_tx.t_ox", g_tp.sleep_tx.t_ox);
    printing("g_tp.sleep_tx.Vth", g_tp.sleep_tx.Vth);
    printing("g_tp.sleep_tx.C_ox", g_tp.sleep_tx.C_ox);
    printing("g_tp.sleep_tx.C_g_ideal", g_tp.sleep_tx.C_g_ideal);
    printing("g_tp.sleep_tx.C_fringe", g_tp.sleep_tx.C_fringe);
    printing("g_tp.sleep_tx.C_junc", g_tp.sleep_tx.C_junc);
    printing("g_tp.sleep_tx.C_junc_sidewall", g_tp.sleep_tx.C_junc_sidewall);
    printing("g_tp.sleep_tx.l_phy", g_tp.sleep_tx.l_phy);
    printing("g_tp.sleep_tx.l_elec", g_tp.sleep_tx.l_elec);
    printing("g_tp.sleep_tx.I_on_n", g_tp.sleep_tx.I_on_n);
    printing("g_tp.sleep_tx.R_nch_on", g_tp.sleep_tx.R_nch_on);
    printing("g_tp.sleep_tx.R_pch_on", g_tp.sleep_tx.R_pch_on);
    printing("g_tp.sleep_tx.n_to_p_eff_curr_drv_ratio", g_tp.sleep_tx.n_to_p_eff_curr_drv_ratio);
    printing("g_tp.sleep_tx.long_channel_leakage_reduction", g_tp.sleep_tx.long_channel_leakage_reduction);
    printing("g_tp.sleep_tx.I_off_n", g_tp.sleep_tx.I_off_n);
    printing("g_tp.sleep_tx.I_off_p", g_tp.sleep_tx.I_off_p);
    printing("g_tp.sleep_tx.I_g_on_n", g_tp.sleep_tx.I_g_on_n);
    printing("g_tp.sleep_tx.I_g_on_p", g_tp.sleep_tx.I_g_on_p);
    printing("g_tp.sleep_tx.Mobility_n", g_tp.sleep_tx.Mobility_n);

    printing("g_tp.sram_cell.Vdd", g_tp.sram_cell.Vdd);
    printing("g_tp.sram_cell.Vcc_min", g_tp.sram_cell.Vcc_min);
    printing("g_tp.sram_cell.l_phy", g_tp.sram_cell.l_phy);
    printing("g_tp.sram_cell.l_elec", g_tp.sram_cell.l_elec);
    printing("g_tp.sram_cell.t_ox", g_tp.sram_cell.t_ox);
    printing("g_tp.sram_cell.Vth", g_tp.sram_cell.Vth);
    printing("g_tp.sram_cell.C_g_ideal", g_tp.sram_cell.C_g_ideal);
    printing("g_tp.sram_cell.C_fringe", g_tp.sram_cell.C_fringe);
    printing("g_tp.sram_cell.C_junc", g_tp.sram_cell.C_junc);
    printing("g_tp.sram_cell.C_junc_sidewall", g_tp.sram_cell.C_junc_sidewall);
    printing("g_tp.sram_cell.I_on_n", g_tp.sram_cell.I_on_n);
    printing("g_tp.sram_cell.R_nch_on", g_tp.sram_cell.R_nch_on);
    printing("g_tp.sram_cell.R_pch_on", g_tp.sram_cell.R_pch_on);
    printing("g_tp.sram_cell.n_to_p_eff_curr_drv_ratio", g_tp.sram_cell.n_to_p_eff_curr_drv_ratio);
    printing("g_tp.sram_cell.long_channel_leakage_reduction", g_tp.sram_cell.long_channel_leakage_reduction);
    printing("g_tp.sram_cell.I_off_n", g_tp.sram_cell.I_off_n);
    printing("g_tp.sram_cell.I_off_p", g_tp.sram_cell.I_off_p);
    printing("g_tp.sram_cell.I_g_on_n", g_tp.sram_cell.I_g_on_n);
    printing("g_tp.sram_cell.I_g_on_p", g_tp.sram_cell.I_g_on_p);

    printing("g_tp.dram_cell_Vdd", g_tp.dram_cell_Vdd);
    printing("g_tp.dram_acc.Vth", g_tp.dram_acc.Vth);
    printing("g_tp.dram_acc.l_phy", g_tp.dram_acc.l_phy);
    printing("g_tp.dram_acc.l_elec", g_tp.dram_acc.l_elec);
    printing("g_tp.dram_acc.C_g_ideal", g_tp.dram_acc.C_g_ideal);
    printing("g_tp.dram_acc.C_fringe", g_tp.dram_acc.C_fringe);
    printing("g_tp.dram_acc.C_junc", g_tp.dram_acc.C_junc);
    printing("g_tp.dram_acc.C_junc_sidewall", g_tp.dram_acc.C_junc_sidewall);
    printing("g_tp.dram_cell_I_on", g_tp.dram_cell_I_on);
    printing("g_tp.dram_cell_I_off_worst_case_len_temp", g_tp.dram_cell_I_off_worst_case_len_temp);
    printing("g_tp.dram_acc.I_on_n", g_tp.dram_acc.I_on_n);
    printing("g_tp.dram_cell_C", g_tp.dram_cell_C);
    printing("g_tp.vpp", g_tp.vpp);
    printing("g_tp.dram_wl.l_phy", g_tp.dram_wl.l_phy);
    printing("g_tp.dram_wl.l_elec", g_tp.dram_wl.l_elec);
    printing("g_tp.dram_wl.C_g_ideal", g_tp.dram_wl.C_g_ideal);
    printing("g_tp.dram_wl.C_fringe", g_tp.dram_wl.C_fringe);
    printing("g_tp.dram_wl.C_junc", g_tp.dram_wl.C_junc);
    printing("g_tp.dram_wl.C_junc_sidewall", g_tp.dram_wl.C_junc_sidewall);
    printing("g_tp.dram_wl.I_on_n", g_tp.dram_wl.I_on_n);
    printing("g_tp.dram_wl.R_nch_on", g_tp.dram_wl.R_nch_on);
    printing("g_tp.dram_wl.R_pch_on", g_tp.dram_wl.R_pch_on);
    printing("g_tp.dram_wl.n_to_p_eff_curr_drv_ratio", g_tp.dram_wl.n_to_p_eff_curr_drv_ratio);
    printing("g_tp.dram_wl.long_channel_leakage_reduction", g_tp.dram_wl.long_channel_leakage_reduction);
    printing("g_tp.dram_wl.I_off_n", g_tp.dram_wl.I_off_n);
    printing("g_tp.dram_wl.I_off_p", g_tp.dram_wl.I_off_p);

    printing("g_tp.cam_cell.Vdd", g_tp.cam_cell.Vdd);
    printing("g_tp.cam_cell.l_phy", g_tp.cam_cell.l_phy);
    printing("g_tp.cam_cell.l_elec", g_tp.cam_cell.l_elec);
    printing("g_tp.cam_cell.t_ox", g_tp.cam_cell.t_ox);
    printing("g_tp.cam_cell.Vth", g_tp.cam_cell.Vth);
    printing("g_tp.cam_cell.C_g_ideal", g_tp.cam_cell.C_g_ideal);
    printing("g_tp.cam_cell.C_fringe", g_tp.cam_cell.C_fringe);
    printing("g_tp.cam_cell.C_junc", g_tp.cam_cell.C_junc);
    printing("g_tp.cam_cell.C_junc_sidewall", g_tp.cam_cell.C_junc_sidewall);
    printing("g_tp.cam_cell.I_on_n", g_tp.cam_cell.I_on_n);
    printing("g_tp.cam_cell.R_nch_on", g_tp.cam_cell.R_nch_on);
    printing("g_tp.cam_cell.R_pch_on", g_tp.cam_cell.R_pch_on);
    printing("g_tp.cam_cell.n_to_p_eff_curr_drv_ratio", g_tp.cam_cell.n_to_p_eff_curr_drv_ratio);
    printing("g_tp.cam_cell.long_channel_leakage_reduction", g_tp.cam_cell.long_channel_leakage_reduction);
    printing("g_tp.cam_cell.I_off_n", g_tp.cam_cell.I_off_n);
    printing("g_tp.cam_cell.I_off_p", g_tp.cam_cell.I_off_p);
    printing("g_tp.cam_cell.I_g_on_n", g_tp.cam_cell.I_g_on_n);
    printing("g_tp.cam_cell.I_g_on_p", g_tp.cam_cell.I_g_on_p);

    printing("g_tp.dram.cell_a_w", g_tp.dram.cell_a_w);
    printing("g_tp.dram.cell_pmos_w", g_tp.dram.cell_pmos_w);
    printing("g_tp.dram.cell_nmos_w", g_tp.dram.cell_nmos_w);

    printing("g_tp.sram.cell_a_w", g_tp.sram.cell_a_w);
    printing("g_tp.sram.cell_pmos_w", g_tp.sram.cell_pmos_w);
    printing("g_tp.sram.cell_nmos_w", g_tp.sram.cell_nmos_w);

    printing("g_tp.cam.cell_a_w", g_tp.cam.cell_a_w);
    printing("g_tp.cam.cell_pmos_w", g_tp.cam.cell_pmos_w);
    printing("g_tp.cam.cell_nmos_w", g_tp.cam.cell_nmos_w);

    printing("g_tp.scaling_factor.logic_scaling_co_eff", g_tp.scaling_factor.logic_scaling_co_eff);
    printing("g_tp.scaling_factor.core_tx_density", g_tp.scaling_factor.core_tx_density);
    printing("g_tp.chip_layout_overhead", g_tp.chip_layout_overhead);
    printing("g_tp.macro_layout_overhead", g_tp.macro_layout_overhead);
    printing("g_tp.sckt_co_eff", g_tp.sckt_co_eff);

    printing("g_tp.w_comp_inv_p1", g_tp.w_comp_inv_p1);
    printing("g_tp.w_comp_inv_n1", g_tp.w_comp_inv_n1);
    printing("g_tp.w_comp_inv_p2", g_tp.w_comp_inv_p2);
    printing("g_tp.w_comp_inv_n2", g_tp.w_comp_inv_n2);
    printing("g_tp.w_comp_inv_p3", g_tp.w_comp_inv_p3);
    printing("g_tp.w_comp_inv_n3", g_tp.w_comp_inv_n3);
    printing("g_tp.w_eval_inv_p", g_tp.w_eval_inv_p);
    printing("g_tp.w_eval_inv_n", g_tp.w_eval_inv_n);
    printing("g_tp.w_comp_n", g_tp.w_comp_n);
    printing("g_tp.w_comp_p", g_tp.w_comp_p);

    printing("g_tp.MIN_GAP_BET_P_AND_N_DIFFS", g_tp.MIN_GAP_BET_P_AND_N_DIFFS);
    printing("g_tp.MIN_GAP_BET_SAME_TYPE_DIFFS", g_tp.MIN_GAP_BET_SAME_TYPE_DIFFS);
    printing("g_tp.HPOWERRAIL", g_tp.HPOWERRAIL);
    printing("g_tp.cell_h_def", g_tp.cell_h_def);
    printing("g_tp.w_poly_contact", g_tp.w_poly_contact);
    printing("g_tp.spacing_poly_to_contact", g_tp.spacing_poly_to_contact);
    printing("g_tp.spacing_poly_to_poly", g_tp.spacing_poly_to_poly);
    printing("g_tp.ram_wl_stitching_overhead_", g_tp.ram_wl_stitching_overhead_);

    printing("g_tp.min_w_nmos_", g_tp.min_w_nmos_);
    printing("g_tp.max_w_nmos_", g_tp.max_w_nmos_);
    printing("g_tp.w_iso", g_tp.w_iso);
    printing("g_tp.w_sense_n", g_tp.w_sense_n);
    printing("g_tp.w_sense_p", g_tp.w_sense_p);
    printing("g_tp.w_sense_en", g_tp.w_sense_en);
    printing("g_tp.w_nmos_b_mux", g_tp.w_nmos_b_mux);
    printing("g_tp.w_nmos_sa_mux", g_tp.w_nmos_sa_mux);

    printing("g_tp.max_w_nmos_dec", g_tp.max_w_nmos_dec);
    printing_int("g_tp.h_dec", g_tp.h_dec);

    printing("g_tp.peri_global.C_overlap", g_tp.peri_global.C_overlap);
    printing("g_tp.sram_cell.C_overlap", g_tp.sram_cell.C_overlap);
    printing("g_tp.cam_cell.C_overlap", g_tp.cam_cell.C_overlap);

    printing("g_tp.dram_acc.C_overlap", g_tp.dram_acc.C_overlap);
    printing("g_tp.dram_acc.R_nch_on", g_tp.dram_acc.R_nch_on);

    printing("g_tp.dram_wl.C_overlap", g_tp.dram_wl.C_overlap);

    printing("g_tp.gm_sense_amp_latch", g_tp.gm_sense_amp_latch);

    printing("g_tp.dram.b_w", g_tp.dram.b_w);
    printing("g_tp.dram.b_h", g_tp.dram.b_h);
    printing("g_tp.sram.b_w", g_tp.sram.b_w);
    printing("g_tp.sram.b_h", g_tp.sram.b_h);
    printing("g_tp.cam.b_w", g_tp.cam.b_w);
    printing("g_tp.cam.b_h", g_tp.cam.b_h);

    printing("g_tp.dram.Vbitpre", g_tp.dram.Vbitpre);
    printing("g_tp.sram.Vbitpre", g_tp.sram.Vbitpre);
    printing("g_tp.sram.Vbitfloating", g_tp.sram.Vbitfloating);
    printing("g_tp.cam.Vbitpre", g_tp.cam.Vbitpre);

    printing("g_tp.w_pmos_bl_precharge", g_tp.w_pmos_bl_precharge);
    printing("g_tp.w_pmos_bl_eq", g_tp.w_pmos_bl_eq);

    printing("g_tp.wire_local.pitch", g_tp.wire_local.pitch);
    printing("g_tp.wire_local.R_per_um", g_tp.wire_local.R_per_um);
    printing("g_tp.wire_local.C_per_um", g_tp.wire_local.C_per_um);
    printing("g_tp.wire_local.aspect_ratio", g_tp.wire_local.aspect_ratio);
    printing("g_tp.wire_local.ild_thickness", g_tp.wire_local.ild_thickness);
    printing("g_tp.wire_local.miller_value", g_tp.wire_local.miller_value);
    printing("g_tp.wire_local.horiz_dielectric_constant", g_tp.wire_local.horiz_dielectric_constant);
    printing("g_tp.wire_local.vert_dielectric_constant", g_tp.wire_local.vert_dielectric_constant);

    printing("g_tp.wire_inside_mat.pitch", g_tp.wire_inside_mat.pitch);
    printing("g_tp.wire_inside_mat.R_per_um", g_tp.wire_inside_mat.R_per_um);
    printing("g_tp.wire_inside_mat.C_per_um", g_tp.wire_inside_mat.C_per_um);
    printing("g_tp.wire_inside_mat.aspect_ratio", g_tp.wire_inside_mat.aspect_ratio);
    printing("g_tp.wire_inside_mat.ild_thickness", g_tp.wire_inside_mat.ild_thickness);
    printing("g_tp.wire_inside_mat.miller_value", g_tp.wire_inside_mat.miller_value);
    printing("g_tp.wire_inside_mat.horiz_dielectric_constant", g_tp.wire_inside_mat.horiz_dielectric_constant);
    printing("g_tp.wire_inside_mat.vert_dielectric_constant", g_tp.wire_inside_mat.vert_dielectric_constant);

    printing("g_tp.wire_outside_mat.pitch", g_tp.wire_outside_mat.pitch);
    printing("g_tp.wire_outside_mat.R_per_um", g_tp.wire_outside_mat.R_per_um);
    printing("g_tp.wire_outside_mat.C_per_um", g_tp.wire_outside_mat.C_per_um);
    printing("g_tp.wire_outside_mat.aspect_ratio", g_tp.wire_outside_mat.aspect_ratio);
    printing("g_tp.wire_outside_mat.ild_thickness", g_tp.wire_outside_mat.ild_thickness);
    printing("g_tp.wire_outside_mat.miller_value", g_tp.wire_outside_mat.miller_value);
    printing("g_tp.wire_outside_mat.horiz_dielectric_constant", g_tp.wire_outside_mat.horiz_dielectric_constant);
    printing("g_tp.wire_outside_mat.vert_dielectric_constant", g_tp.wire_outside_mat.vert_dielectric_constant);

    printing("g_tp.unit_len_wire_del", g_tp.unit_len_wire_del);

    printing("g_tp.sense_delay", g_tp.sense_delay);
    printing("g_tp.sense_dy_power", g_tp.sense_dy_power);

    printing("g_tp.tsv_parasitic_resistance_fine", g_tp.tsv_parasitic_resistance_fine);
    printing("g_tp.tsv_parasitic_capacitance_fine", g_tp.tsv_parasitic_capacitance_fine);
    printing("g_tp.tsv_minimum_area_fine", g_tp.tsv_minimum_area_fine);

    printing("g_tp.tsv_parasitic_resistance_coarse", g_tp.tsv_parasitic_resistance_coarse);
    printing("g_tp.tsv_parasitic_capacitance_coarse", g_tp.tsv_parasitic_capacitance_coarse);
    printing("g_tp.tsv_minimum_area_coarse", g_tp.tsv_minimum_area_coarse);

    printing("g_tp.tsv_minimum_area_coarse", g_tp.tsv_minimum_area_coarse);
    printing("g_tp.fringe_cap", g_tp.fringe_cap);
    printing("g_tp.kinv", g_tp.kinv);
    printing("g_tp.FO4", g_tp.FO4);
}

void printing(const char* name, double value) { cout << "tech " << name << " " << value << endl; }
void printing_int(const char* name, uint64_t value) { cout << "tech " << name << " " << value << endl; }
