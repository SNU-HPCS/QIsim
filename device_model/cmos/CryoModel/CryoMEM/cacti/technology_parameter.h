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

#ifndef __TECHNOLOGY_PARAMETER_H__
#define __TECHNOLOGY_PARAMETER_H__

#include <string>
#include <cstdint>

#include "device_type.h"
#include "interconnect_type.h"
#include "scaling_factor.h"
#include "memory_type.h"

class CactiInput_TechnologyParameter;

// parameters which are functions of certain device technology
class TechnologyParameter
{
   public:
    double ram_wl_stitching_overhead_;  // fs
    double min_w_nmos_;                 // fs
    double max_w_nmos_;                 // fs
    double max_w_nmos_dec;              // fs+ ram_cell_tech_type
    double unit_len_wire_del;           // wire_inside_mat
    double FO4;                         // fs
    double kinv;                        // fs
    double vpp;                         // input
    double w_sense_en;                  // fs
    double w_sense_n;                   // fs
    double w_sense_p;                   // fs
    double sense_delay;                 // input
    double sense_dy_power;              // input
    double w_iso;                       // fs
    double w_poly_contact;              // fs
    double spacing_poly_to_poly;        // fs
    double spacing_poly_to_contact;     // fs

    // CACTI3D auxilary variables
    double tsv_pitch;
    double tsv_diameter;
    double tsv_length;
    double tsv_dielec_thickness;
    double tsv_contact_resistance;
    double tsv_depletion_width;
    double tsv_liner_dielectric_constant;

    // CACTI3DD TSV params

    double tsv_parasitic_capacitance_fine;
    double tsv_parasitic_resistance_fine;
    double tsv_minimum_area_fine;

    double tsv_parasitic_capacitance_coarse;
    double tsv_parasitic_resistance_coarse;
    double tsv_minimum_area_coarse;

    // fs
    double w_comp_inv_p1;
    double w_comp_inv_p2;
    double w_comp_inv_p3;
    double w_comp_inv_n1;
    double w_comp_inv_n2;
    double w_comp_inv_n3;
    double w_eval_inv_p;
    double w_eval_inv_n;
    double w_comp_n;
    double w_comp_p;

    double dram_cell_I_on;  // ram_cell_tech_type
    double dram_cell_Vdd;
    double dram_cell_I_off_worst_case_len_temp;
    double dram_cell_C;
    double gm_sense_amp_latch;  // depends on many things

    double w_nmos_b_mux;                 // fs
    double w_nmos_sa_mux;                // fs
    double w_pmos_bl_precharge;          // fs
    double w_pmos_bl_eq;                 // fs
    double MIN_GAP_BET_P_AND_N_DIFFS;    // fs
    double MIN_GAP_BET_SAME_TYPE_DIFFS;  // fs
    double HPOWERRAIL;                   // fs
    double cell_h_def;                   // fs

    double chip_layout_overhead;  // input
    double macro_layout_overhead;
    double sckt_co_eff;

    double fringe_cap;  // input

    std::uint64_t h_dec;  // ram_cell_tech_type

    DeviceType sram_cell;    // SRAM cell transistor
    DeviceType dram_acc;     // DRAM access transistor
    DeviceType dram_wl;      // DRAM wordline transistor
    DeviceType peri_global;  // peripheral global
    DeviceType cam_cell;     // SRAM cell transistor

    DeviceType sleep_tx;  // Sleep transistor cell transistor

    InterconnectType wire_local;
    InterconnectType wire_inside_mat;
    InterconnectType wire_outside_mat;

    ScalingFactor scaling_factor;

    MemoryType sram;
    MemoryType dram;
    MemoryType cam;

    void display(std::uint32_t indent = 0);
    bool isEqual(const TechnologyParameter& tech);

    void find_upper_and_lower_tech(double technology, int& tech_lo, std::string& in_file_lo, int& tech_hi, std::string& in_file_hi);
    void assign_tsv(const std::string& in_file);
    void init(double technology, bool is_tag);
    void overriding(const CactiInput_TechnologyParameter &tech_param);
    TechnologyParameter() { reset(); }
    void reset()
    {
        ram_wl_stitching_overhead_ = 0;  // fs
        min_w_nmos_                = 0;  // fs
        max_w_nmos_                = 0;  // fs
        max_w_nmos_dec             = 0;  // fs+ ram_cell_tech_type
        unit_len_wire_del          = 0;  // wire_inside_mat
        FO4                        = 0;  // fs
        kinv                       = 0;  // fs
        vpp                        = 0;  // input
        w_sense_en                 = 0;  // fs
        w_sense_n                  = 0;  // fs
        w_sense_p                  = 0;  // fs
        sense_delay                = 0;  // input
        sense_dy_power             = 0;  // input
        w_iso                      = 0;  // fs
        w_poly_contact             = 0;  // fs
        spacing_poly_to_poly       = 0;  // fs
        spacing_poly_to_contact    = 0;  // fs

        // CACTI3D auxilary variables
        tsv_pitch                     = 0;
        tsv_diameter                  = 0;
        tsv_length                    = 0;
        tsv_dielec_thickness          = 0;
        tsv_contact_resistance        = 0;
        tsv_depletion_width           = 0;
        tsv_liner_dielectric_constant = 0;

        // CACTI3DD TSV params

        tsv_parasitic_capacitance_fine = 0;
        tsv_parasitic_resistance_fine  = 0;
        tsv_minimum_area_fine          = 0;

        tsv_parasitic_capacitance_coarse = 0;
        tsv_parasitic_resistance_coarse  = 0;
        tsv_minimum_area_coarse          = 0;

        // fs
        w_comp_inv_p1 = 0;
        w_comp_inv_p2 = 0;
        w_comp_inv_p3 = 0;
        w_comp_inv_n1 = 0;
        w_comp_inv_n2 = 0;
        w_comp_inv_n3 = 0;
        w_eval_inv_p  = 0;
        w_eval_inv_n  = 0;
        w_comp_n      = 0;
        w_comp_p      = 0;

        dram_cell_I_on                      = 0;  // ram_cell_tech_type
        dram_cell_Vdd                       = 0;
        dram_cell_I_off_worst_case_len_temp = 0;
        dram_cell_C                         = 0;
        gm_sense_amp_latch                  = 0;  // depends on many things

        w_nmos_b_mux                = 0;  // fs
        w_nmos_sa_mux               = 0;  // fs
        w_pmos_bl_precharge         = 0;  // fs
        w_pmos_bl_eq                = 0;  // fs
        MIN_GAP_BET_P_AND_N_DIFFS   = 0;  // fs
        MIN_GAP_BET_SAME_TYPE_DIFFS = 0;  // fs
        HPOWERRAIL                  = 0;  // fs
        cell_h_def                  = 0;  // fs

        chip_layout_overhead  = 0;
        macro_layout_overhead = 0;
        sckt_co_eff           = 0;

        fringe_cap = 0;  // input

        h_dec = 0;  // ram_cell_tech_type

        sram_cell.reset();
        dram_acc.reset();
        dram_wl.reset();
        peri_global.reset();
        cam_cell.reset();
        sleep_tx.reset();

        scaling_factor.reset();

        wire_local.reset();
        wire_inside_mat.reset();
        wire_outside_mat.reset();

        sram.reset();
        dram.reset();
        cam.reset();
    }
};

void init_tech_params(double technology, bool is_tag);
void print_g_tp();

extern TechnologyParameter g_tp;

#endif
