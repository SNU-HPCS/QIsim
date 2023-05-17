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
#include <cassert>
#include <cmath>

#include "dynamic_parameter.h"
#include "basic_circuit.h"
#include "const.h"
#include "input_parameter.h"
#include "technology_parameter.h"
#include "enum/ram_cell_tech_type_num.h"

using namespace std;

DynamicParameter::DynamicParameter() : use_inp_params(0), cell(), is_valid(true) {}
DynamicParameter::DynamicParameter(
    bool         is_tag_,
    int          pure_ram_,
    int          pure_cam_,
    double       Nspd_,
    unsigned int Ndwl_,
    unsigned int Ndbl_,
    unsigned int Ndcm_,
    unsigned int Ndsam_lev_1_,
    unsigned int Ndsam_lev_2_,
    Wire_type    wt,
    bool         is_main_mem_)
    : is_tag(is_tag_),
      pure_ram(pure_ram_),
      pure_cam(pure_cam_),
      tagbits(0),
      Nspd(Nspd_),
      Ndwl(Ndwl_),
      Ndbl(Ndbl_),
      Ndcm(Ndcm_),
      Ndsam_lev_1(Ndsam_lev_1_),
      Ndsam_lev_2(Ndsam_lev_2_),
      wtype(wt),
      number_way_select_signals_mat(0),
      V_b_sense(0),
      use_inp_params(0),
      is_main_mem(is_main_mem_),
      cell(),
      is_valid(false)
{
    ram_cell_tech_type = (is_tag) ? g_ip->tag_arr_ram_cell_tech_type : g_ip->data_arr_ram_cell_tech_type;
    is_dram            = ((ram_cell_tech_type == lp_dram) || (ram_cell_tech_type == comm_dram));

    unsigned int            capacity_per_die = g_ip->cache_sz / NUMBER_STACKED_DIE_LAYERS;  // capacity per stacked die layer
    const InterconnectType& wire_local       = g_tp.wire_local;
    fully_assoc                              = (g_ip->fully_assoc) ? true : false;

    if (pure_cam) {
        init_CAM();
        return;
    }

    if (fully_assoc) {
        init_FA();
        return;
    }

    //*** Calculate number of rows and columns in a subarray
    //    Return if their dimensions do not meet the minimum specs
    if (!calc_subarr_rc(capacity_per_die)) return;

    //** Calculate cell dimensions
    if (is_tag) {
        cell.h = g_tp.sram.b_h + 2 * wire_local.pitch * (g_ip->num_rw_ports - 1 + g_ip->num_rd_ports + g_ip->num_wr_ports);
        cell.w = g_tp.sram.b_w + 2 * wire_local.pitch * (g_ip->num_rw_ports - 1 + g_ip->num_wr_ports + (g_ip->num_rd_ports - g_ip->num_se_rd_ports))
                 + wire_local.pitch * g_ip->num_se_rd_ports;
    }
    else
    {
        if (is_dram) {
            cell.h = g_tp.dram.b_h;
            cell.w = g_tp.dram.b_w;
        }
        else
        {
            cell.h = g_tp.sram.b_h + 2 * wire_local.pitch * (g_ip->num_wr_ports + g_ip->num_rw_ports - 1 + g_ip->num_rd_ports);
            cell.w = g_tp.sram.b_w + 2 * wire_local.pitch * (g_ip->num_rw_ports - 1 + (g_ip->num_rd_ports - g_ip->num_se_rd_ports) + g_ip->num_wr_ports)
                     + g_tp.wire_local.pitch * g_ip->num_se_rd_ports;
        }
    }

    double c_b_metal = cell.h * wire_local.C_per_um;
    double C_bl;

    if (is_dram) {
        deg_bl_muxing = 1;
        if (ram_cell_tech_type == comm_dram) {
            double Cbitrow_drain_cap = drain_C_(g_tp.dram.cell_a_w, NCH, 1, 0, cell.w, true, true) / 2.0;
            C_bl                     = num_r_subarray * (Cbitrow_drain_cap + c_b_metal);
            // C_bl  = num_r_subarray * c_b_metal;
            V_b_sense = (g_tp.dram_cell_Vdd / 2) * g_tp.dram_cell_C / (g_tp.dram_cell_C + C_bl);
            if (V_b_sense < VBITSENSEMIN && !(g_ip->is_3d_mem && g_ip->force_cache_config)) {
                return;
            }

            dram_refresh_period = 0.9 * g_tp.dram_cell_C * VDD_STORAGE_LOSS_FRACTION_WORST * g_tp.dram_cell_Vdd / g_tp.dram_acc.I_off_n;
            if (dram_refresh_period > 64e-3) {
                dram_refresh_period = 64e-3;
            }
        }
        else
        {
            double Cbitrow_drain_cap = drain_C_(g_tp.dram.cell_a_w, NCH, 1, 0, cell.w, true, true) / 2.0;
            C_bl                     = num_r_subarray * (Cbitrow_drain_cap + c_b_metal);
            V_b_sense                = (g_tp.dram_cell_Vdd / 2) * g_tp.dram_cell_C / (g_tp.dram_cell_C + C_bl);

            if (V_b_sense < VBITSENSEMIN) {
                return;  // Sense amp input signal is smaller that minimum allowable sense amp input signal
            }
            V_b_sense = VBITSENSEMIN;  // in any case, we fix sense amp input signal to a constant value
            // v_storage_worst = g_tp.dram_cell_Vdd / 2 - VBITSENSEMIN * (g_tp.dram_cell_C + C_bl) / g_tp.dram_cell_C;
            // dram_refresh_period = 1.1 * g_tp.dram_cell_C * v_storage_worst / g_tp.dram_cell_I_off_worst_case_len_temp;
            dram_refresh_period = 0.9 * g_tp.dram_cell_C * VDD_STORAGE_LOSS_FRACTION_WORST * g_tp.dram_cell_Vdd / g_tp.dram_cell_I_off_worst_case_len_temp;
        }
    }
    else
    {  // SRAM
        V_b_sense     = (0.05 * g_tp.sram_cell.Vdd > VBITSENSEMIN) ? 0.05 * g_tp.sram_cell.Vdd : VBITSENSEMIN;
        deg_bl_muxing = Ndcm;
        // "/ 2.0" below is due to the fact that two adjacent access transistors share drain
        // contacts in a physical layout
        double Cbitrow_drain_cap = drain_C_(g_tp.sram.cell_a_w, NCH, 1, 0, cell.w, false, true) / 2.0;
        C_bl                     = num_r_subarray * (Cbitrow_drain_cap + c_b_metal);
        dram_refresh_period      = 0;
    }

    // do/di: data in/out, for fully associative they are the data width for normal read and write
    // so/si: search data in/out, for fully associative they are the data width for the search ops
    // for CAM, si=di, but so = matching address. do = data out = di (for normal read/write)
    // so/si needs broadcase while do/di do not

    num_mats_h_dir = MAX(Ndwl / 2, 1);
    num_mats_v_dir = MAX(Ndbl / 2, 1);
    num_mats       = num_mats_h_dir * num_mats_v_dir;
    num_do_b_mat   = MAX((num_subarrays / num_mats) * num_c_subarray / (deg_bl_muxing * Ndsam_lev_1 * Ndsam_lev_2), 1);

    if (!(fully_assoc || pure_cam) && (num_do_b_mat < (num_subarrays / num_mats))) {
        return;
    }

    int deg_sa_mux_l1_non_assoc;
    // TODO:the i/o for subbank is not necessary and should be removed.
    if (!is_tag) {
        if (is_main_mem == true) {
            num_do_b_subbank = g_ip->int_prefetch_w * g_ip->out_w;
            // CACTI3DD DRAM page size
            if (g_ip->is_3d_mem) num_do_b_subbank = g_ip->page_sz_bits;
            deg_sa_mux_l1_non_assoc               = Ndsam_lev_1;
        }
        else
        {
            if (g_ip->fast_access == true) {
                num_do_b_subbank        = g_ip->out_w * g_ip->data_assoc;
                deg_sa_mux_l1_non_assoc = Ndsam_lev_1;
            }
            else
            {
                num_do_b_subbank        = g_ip->out_w;
                deg_sa_mux_l1_non_assoc = Ndsam_lev_1 / g_ip->data_assoc;
                if (deg_sa_mux_l1_non_assoc < 1) {
                    return;
                }
            }
        }
    }
    else
    {
        num_do_b_subbank = tagbits * g_ip->tag_assoc;
        if (num_do_b_mat < tagbits) {
            return;
        }
        deg_sa_mux_l1_non_assoc = Ndsam_lev_1;
        // num_do_b_mat = g_ip->tag_assoc / num_mats_h_dir;
    }

    deg_senseamp_muxing_non_associativity = deg_sa_mux_l1_non_assoc;

    num_act_mats_hor_dir                                                   = num_do_b_subbank / num_do_b_mat;
    if (g_ip->is_3d_mem && num_act_mats_hor_dir == 0) num_act_mats_hor_dir = 1;
    if (num_act_mats_hor_dir == 0) {
        return;
    }

    // compute num_do_mat for tag
    if (is_tag) {
        if (!(fully_assoc || pure_cam)) {
            num_do_b_mat     = g_ip->tag_assoc / num_act_mats_hor_dir;
            num_do_b_subbank = num_act_mats_hor_dir * num_do_b_mat;
        }
    }

    if ((g_ip->is_cache == false && is_main_mem == true) || (PAGE_MODE == 1 && is_dram)) {
        if (num_act_mats_hor_dir * num_do_b_mat * Ndsam_lev_1 * Ndsam_lev_2 != (int)g_ip->page_sz_bits) {
            return;
        }
    }

    //  if (is_tag == false && g_ip->is_cache == true && !fully_assoc && !pure_cam && //TODO: TODO burst transfer should also apply to RAM arrays
    if (is_tag == false && g_ip->is_main_mem == true
        && num_act_mats_hor_dir * num_do_b_mat * Ndsam_lev_1 * Ndsam_lev_2 < ((int)g_ip->out_w * (int)g_ip->burst_len * (int)g_ip->data_assoc))
    {
        return;
    }

    if (num_act_mats_hor_dir > num_mats_h_dir) {
        return;
    }

    // compute di for mat subbank and bank
    if (!is_tag) {
        if (g_ip->fast_access == true) {
            num_di_b_mat = num_do_b_mat / g_ip->data_assoc;
        }
        else
        {
            num_di_b_mat = num_do_b_mat;
        }
    }
    else
    {
        num_di_b_mat = tagbits;
    }

    num_di_b_subbank = num_di_b_mat * num_act_mats_hor_dir;  // normal cache or normal r/w for FA
    num_si_b_subbank = num_si_b_mat;                         //* num_act_mats_hor_dir_sl; inside the data is broadcast

    int num_addr_b_row_dec = _log2(num_r_subarray);
    if ((fully_assoc || pure_cam)) num_addr_b_row_dec += _log2(num_subarrays / num_mats);
    int number_subbanks    = num_mats / num_act_mats_hor_dir;
    number_subbanks_decode = _log2(number_subbanks);  // TODO: add log2(num_subarray_per_bank) to FA/CAM

    num_rw_ports     = g_ip->num_rw_ports;
    num_rd_ports     = g_ip->num_rd_ports;
    num_wr_ports     = g_ip->num_wr_ports;
    num_se_rd_ports  = g_ip->num_se_rd_ports;
    num_search_ports = g_ip->num_search_ports;

    if (is_dram && is_main_mem) {
        number_addr_bits_mat = MAX((unsigned int)num_addr_b_row_dec, _log2(deg_bl_muxing) + _log2(deg_sa_mux_l1_non_assoc) + _log2(Ndsam_lev_2));
        if (g_ip->print_detail_debug) {
            cout << "parameter.cc: number_addr_bits_mat = " << num_addr_b_row_dec << endl;
            cout << "parameter.cc: num_addr_b_row_dec = " << num_addr_b_row_dec << endl;
            cout << "parameter.cc: num_addr_b_mux_sel = " << _log2(deg_bl_muxing) + _log2(deg_sa_mux_l1_non_assoc) + _log2(Ndsam_lev_2) << endl;
        }
    }
    else
    {
        number_addr_bits_mat = num_addr_b_row_dec + _log2(deg_bl_muxing) + _log2(deg_sa_mux_l1_non_assoc) + _log2(Ndsam_lev_2);
    }

    if (is_tag) {
        num_di_b_bank_per_port = tagbits;
        num_do_b_bank_per_port = g_ip->data_assoc;
    }
    else
    {
        num_di_b_bank_per_port = g_ip->out_w + g_ip->data_assoc;
        num_do_b_bank_per_port = g_ip->out_w;
    }

    if ((!is_tag) && (g_ip->data_assoc > 1) && (!g_ip->fast_access)) {
        number_way_select_signals_mat = g_ip->data_assoc;
    }

    // add ECC adjustment to all data signals that traverse on H-trees.
    if (g_ip->add_ecc_b_ == true) ECC_adjustment();

    is_valid = true;
}

void DynamicParameter::ECC_adjustment()
{
    num_do_b_mat += (int)(ceil(num_do_b_mat / num_bits_per_ecc_b_));
    num_di_b_mat += (int)(ceil(num_di_b_mat / num_bits_per_ecc_b_));
    num_di_b_subbank += (int)(ceil(num_di_b_subbank / num_bits_per_ecc_b_));
    num_do_b_subbank += (int)(ceil(num_do_b_subbank / num_bits_per_ecc_b_));
    num_di_b_bank_per_port += (int)(ceil(num_di_b_bank_per_port / num_bits_per_ecc_b_));
    num_do_b_bank_per_port += (int)(ceil(num_do_b_bank_per_port / num_bits_per_ecc_b_));

    num_so_b_mat += (int)(ceil(num_so_b_mat / num_bits_per_ecc_b_));
    num_si_b_mat += (int)(ceil(num_si_b_mat / num_bits_per_ecc_b_));
    num_si_b_subbank += (int)(ceil(num_si_b_subbank / num_bits_per_ecc_b_));
    num_so_b_subbank += (int)(ceil(num_so_b_subbank / num_bits_per_ecc_b_));
    num_si_b_bank_per_port += (int)(ceil(num_si_b_bank_per_port / num_bits_per_ecc_b_));
    num_so_b_bank_per_port += (int)(ceil(num_so_b_bank_per_port / num_bits_per_ecc_b_));
}

void DynamicParameter::init_CAM()
{
    const InterconnectType& wire_local       = g_tp.wire_local;
    unsigned int            capacity_per_die = g_ip->cache_sz / NUMBER_STACKED_DIE_LAYERS;  // capacity per stacked die layer

    if (Ndwl != 1 ||  // Ndwl is fixed to 1 for CAM
        Ndcm != 1
        ||  // Ndcm is fixed to 1 for CAM
        Nspd < 1
        || Nspd > 1
        ||  // Nspd is fixed to 1 for CAM
        Ndsam_lev_1 != 1
        ||  // Ndsam_lev_1 is fixed to one
        Ndsam_lev_2 != 1
        ||         // Ndsam_lev_2 is fixed to one
        Ndbl < 2)  // FIXME: why should Ndbl be >1 for very small CAMs?
    {
        return;
    }

    if (g_ip->specific_tag) {
        tagbits = int(ceil(g_ip->tag_w / 8.0) * 8);
    }
    else
    {
        tagbits = int(ceil((ADDRESS_BITS + EXTRA_TAG_BITS) / 8.0) * 8);
    }

    // computation of no. of rows and cols of a subarray
    tag_num_r_subarray = (int)ceil(
        capacity_per_die / (g_ip->nbanks * tagbits / 8.0
                            * Ndbl));  // TODO: error check input of tagbits and blocksize //TODO: for pure CAM, g_ip->block should be number of entries.
    tag_num_c_subarray = tagbits;

    if (tag_num_r_subarray == 0) return;
    if (tag_num_r_subarray > MAXSUBARRAYROWS) return;
    if (tag_num_c_subarray < MINSUBARRAYCOLS) return;
    if (tag_num_c_subarray > MAXSUBARRAYCOLS) return;
    num_r_subarray = tag_num_r_subarray;  // FIXME: what about num_c_subarray?

    num_subarrays = Ndwl * Ndbl;

    // calculate cell dimensions
    cam_cell.h = g_tp.cam.b_h + 2 * wire_local.pitch * (g_ip->num_rw_ports - 1 + g_ip->num_rd_ports + g_ip->num_wr_ports)
                 + 2 * wire_local.pitch * (g_ip->num_search_ports - 1) + wire_local.pitch * g_ip->num_se_rd_ports;
    cam_cell.w = g_tp.cam.b_w + 2 * wire_local.pitch * (g_ip->num_rw_ports - 1 + g_ip->num_rd_ports + g_ip->num_wr_ports)
                 + 2 * wire_local.pitch * (g_ip->num_search_ports - 1) + wire_local.pitch * g_ip->num_se_rd_ports;

    // FIXME: curious where this is getting used in a CAM
    cell.h = g_tp.sram.b_h + 2 * wire_local.pitch * (g_ip->num_wr_ports + g_ip->num_rw_ports - 1 + g_ip->num_rd_ports)
             + 2 * wire_local.pitch * (g_ip->num_search_ports - 1);
    cell.w = g_tp.sram.b_w + 2 * wire_local.pitch * (g_ip->num_rw_ports - 1 + (g_ip->num_rd_ports - g_ip->num_se_rd_ports) + g_ip->num_wr_ports)
             + g_tp.wire_local.pitch * g_ip->num_se_rd_ports + 2 * wire_local.pitch * (g_ip->num_search_ports - 1);

    // calculate wire parameters

    double c_b_metal = cell.h * wire_local.C_per_um;
    //  double C_bl;

    c_b_metal     = cam_cell.h * wire_local.C_per_um;  // IBM and SUN design, SRAM array uses dummy cells to fill the blank space due to mismatch on CAM-RAM
    V_b_sense     = (0.05 * g_tp.sram_cell.Vdd > VBITSENSEMIN) ? 0.05 * g_tp.sram_cell.Vdd : VBITSENSEMIN;
    deg_bl_muxing = 1;  // FA fix as 1
    // "/ 2.0" below is due to the fact that two adjacent access transistors share drain
    // contacts in a physical layout
    double Cbitrow_drain_cap = drain_C_(g_tp.cam.cell_a_w, NCH, 1, 0, cam_cell.w, false, true) / 2.0;  // TODO: comment out these two lines
    //  C_bl = num_r_subarray * (Cbitrow_drain_cap + c_b_metal);
    dram_refresh_period = 0;

    // do/di: data in/out, for fully associative they are the data width for normal read and write
    // so/si: search data in/out, for fully associative they are the data width for the search ops
    // for CAM, si=di, but so = matching address. do = data out = di (for normal read/write)
    // so/si needs broadcase while do/di do not

    switch (Ndbl)
    {
    case (0):
        cout << "   Invalid Ndbl \n" << endl;
        exit(0);
        break;
    case (1):
        num_mats_h_dir = 1;  // one subarray per mat
        num_mats_v_dir = 1;
        break;
    case (2):
        num_mats_h_dir = 1;  // two subarrays per mat
        num_mats_v_dir = 1;
        break;
    default:
        num_mats_h_dir = int(floor(sqrt(Ndbl / 4.0)));  // 4 subbarrys per mat
        num_mats_v_dir = int(Ndbl / 4.0 / num_mats_h_dir);
        break;
    }
    num_mats = num_mats_h_dir * num_mats_v_dir;

    num_so_b_mat = int(ceil(log2(num_r_subarray)) + ceil(log2(num_subarrays)));  // the address contains the matched data
    num_do_b_mat = tagbits;

    int deg_sa_mux_l1_non_assoc;

    num_so_b_subbank = int(ceil(log2(num_r_subarray)) + ceil(log2(num_subarrays)));  // the address contains the matched data
    num_do_b_subbank = tag_num_c_subarray;

    deg_sa_mux_l1_non_assoc = 1;

    deg_senseamp_muxing_non_associativity = deg_sa_mux_l1_non_assoc;

    num_act_mats_hor_dir    = 1;
    num_act_mats_hor_dir_sl = num_mats_h_dir;  // TODO: this is unnecessary, since search op, num_mats is used

    // compute num_do_mat for tag

    if (num_act_mats_hor_dir > num_mats_h_dir) {
        return;
    }

    num_di_b_mat = tagbits;
    num_si_b_mat = tagbits;  //*num_subarrays/num_mats;

    num_di_b_subbank = num_di_b_mat * num_act_mats_hor_dir;  // normal cache or normal r/w for FA
    num_si_b_subbank = num_si_b_mat;                         //* num_act_mats_hor_dir_sl; inside the data is broadcast

    int num_addr_b_row_dec = _log2(num_r_subarray);
    num_addr_b_row_dec += _log2(num_subarrays / num_mats);
    int number_subbanks    = num_mats / num_act_mats_hor_dir;
    number_subbanks_decode = _log2(number_subbanks);  // TODO: add log2(num_subarray_per_bank) to FA/CAM

    num_rw_ports     = g_ip->num_rw_ports;
    num_rd_ports     = g_ip->num_rd_ports;
    num_wr_ports     = g_ip->num_wr_ports;
    num_se_rd_ports  = g_ip->num_se_rd_ports;
    num_search_ports = g_ip->num_search_ports;

    number_addr_bits_mat = num_addr_b_row_dec + _log2(deg_bl_muxing) + _log2(deg_sa_mux_l1_non_assoc) + _log2(Ndsam_lev_2);

    num_di_b_bank_per_port = tagbits;
    num_si_b_bank_per_port = tagbits;
    num_do_b_bank_per_port = tagbits;
    num_so_b_bank_per_port = int(ceil(log2(num_r_subarray)) + ceil(log2(num_subarrays)));

    if ((!is_tag) && (g_ip->data_assoc > 1) && (!g_ip->fast_access)) {
        number_way_select_signals_mat = g_ip->data_assoc;
    }

    // add ECC adjustment to all data signals that traverse on H-trees.
    if (g_ip->add_ecc_b_ == true) {
        ECC_adjustment();
    }

    is_valid = true;
}

void DynamicParameter::init_FA()
{
    const InterconnectType& wire_local = g_tp.wire_local;
    // Disabling 3D model since a 3D stacked FA is never tested
    assert(NUMBER_STACKED_DIE_LAYERS == 1);
    unsigned int capacity_per_die = g_ip->cache_sz;

    if (Ndwl != 1 ||  // Ndwl is fixed to 1 for FA
        Ndcm != 1
        ||  // Ndcm is fixed to 1 for FA
        Nspd < 1
        || Nspd > 1
        ||  // Nspd is fixed to 1 for FA
        Ndsam_lev_1 != 1
        ||  // Ndsam_lev_1 is fixed to one
        Ndsam_lev_2 != 1
        ||  // Ndsam_lev_2 is fixed to one
        Ndbl < 2)
    {
        return;
    }

    //***********compute row, col of an subarray

    // either fully-asso or cam
    if (g_ip->specific_tag) {
        tagbits = g_ip->tag_w;
    }
    else
    {
        tagbits = ADDRESS_BITS + EXTRA_TAG_BITS - _log2(g_ip->block_sz);
    }
    tagbits = (((tagbits + 3) >> 2) << 2);

    tag_num_r_subarray = (int)(capacity_per_die / (g_ip->nbanks * g_ip->block_sz * Ndbl));
    tag_num_c_subarray = (int)ceil((tagbits * Nspd / Ndwl));  // + EPSILON);
    if (tag_num_r_subarray == 0) return;
    if (tag_num_r_subarray > MAXSUBARRAYROWS) return;
    if (tag_num_c_subarray < MINSUBARRAYCOLS) return;
    if (tag_num_c_subarray > MAXSUBARRAYCOLS) return;

    data_num_r_subarray = tag_num_r_subarray;
    data_num_c_subarray = 8 * g_ip->block_sz;
    if (data_num_r_subarray == 0) return;
    if (data_num_r_subarray > MAXSUBARRAYROWS) return;
    if (data_num_c_subarray < MINSUBARRAYCOLS) return;
    if (data_num_c_subarray > MAXSUBARRAYCOLS) return;
    num_r_subarray = tag_num_r_subarray;

    num_subarrays = Ndwl * Ndbl;
    //****************end of computation of row, col of an subarray

    // calculate wire parameters
    cam_cell.h = g_tp.cam.b_h + 2 * wire_local.pitch * (g_ip->num_rw_ports - 1 + g_ip->num_rd_ports + g_ip->num_wr_ports)
                 + 2 * wire_local.pitch * (g_ip->num_search_ports - 1) + wire_local.pitch * g_ip->num_se_rd_ports;
    cam_cell.w = g_tp.cam.b_w + 2 * wire_local.pitch * (g_ip->num_rw_ports - 1 + g_ip->num_rd_ports + g_ip->num_wr_ports)
                 + 2 * wire_local.pitch * (g_ip->num_search_ports - 1) + wire_local.pitch * g_ip->num_se_rd_ports;

    cell.h = g_tp.sram.b_h + 2 * wire_local.pitch * (g_ip->num_wr_ports + g_ip->num_rw_ports - 1 + g_ip->num_rd_ports)
             + 2 * wire_local.pitch * (g_ip->num_search_ports - 1);
    cell.w = g_tp.sram.b_w + 2 * wire_local.pitch * (g_ip->num_rw_ports - 1 + (g_ip->num_rd_ports - g_ip->num_se_rd_ports) + g_ip->num_wr_ports)
             + g_tp.wire_local.pitch * g_ip->num_se_rd_ports + 2 * wire_local.pitch * (g_ip->num_search_ports - 1);

    double c_b_metal = cell.h * wire_local.C_per_um;
    //  double C_bl;

    c_b_metal     = cam_cell.h * wire_local.C_per_um;  // IBM and SUN design, SRAM array uses dummy cells to fill the blank space due to mismatch on CAM-RAM
    V_b_sense     = (0.05 * g_tp.sram_cell.Vdd > VBITSENSEMIN) ? 0.05 * g_tp.sram_cell.Vdd : VBITSENSEMIN;
    deg_bl_muxing = 1;  // FA fix as 1
    // "/ 2.0" below is due to the fact that two adjacent access transistors share drain
    // contacts in a physical layout
    double Cbitrow_drain_cap = drain_C_(g_tp.cam.cell_a_w, NCH, 1, 0, cam_cell.w, false, true) / 2.0;  // TODO: comment out these two lines
    //	  C_bl = num_r_subarray * (Cbitrow_drain_cap + c_b_metal);
    dram_refresh_period = 0;

    // do/di: data in/out, for fully associative they are the data width for normal read and write
    // so/si: search data in/out, for fully associative they are the data width for the search ops
    // for CAM, si=di, but so = matching address. do = data out = di (for normal read/write)
    // so/si needs broadcase while do/di do not

    switch (Ndbl)
    {
    case (0):
        cout << "   Invalid Ndbl \n" << endl;
        exit(0);
        break;
    case (1):
        num_mats_h_dir = 1;  // one subarray per mat
        num_mats_v_dir = 1;
        break;
    case (2):
        num_mats_h_dir = 1;  // two subarrays per mat
        num_mats_v_dir = 1;
        break;
    default:
        num_mats_h_dir = int(floor(sqrt(Ndbl / 4.0)));  // 4 subbarrys per mat
        num_mats_v_dir = int(Ndbl / 4.0 / num_mats_h_dir);
        break;
    }
    num_mats = num_mats_h_dir * num_mats_v_dir;

    num_so_b_mat = data_num_c_subarray;
    num_do_b_mat = data_num_c_subarray + tagbits;

    int deg_sa_mux_l1_non_assoc;
    num_so_b_subbank = 8 * g_ip->block_sz;  // TODO:internal perfetch should be considered also for fa
    num_do_b_subbank = num_so_b_subbank + tag_num_c_subarray;

    deg_sa_mux_l1_non_assoc = 1;

    deg_senseamp_muxing_non_associativity = deg_sa_mux_l1_non_assoc;

    num_act_mats_hor_dir    = 1;
    num_act_mats_hor_dir_sl = num_mats_h_dir;  // TODO: this is unnecessary, since search op, num_mats is used

    // compute num_do_mat for tag
    if (num_act_mats_hor_dir > num_mats_h_dir) {
        return;
    }

    // compute di for mat subbank and bank
    if (fully_assoc) {
        num_di_b_mat = num_do_b_mat;
        //*num_subarrays/num_mats; bits per mat of CAM/FA is as same as cache,
        // but inside the mat wire tracks need to be reserved for search data bus
        num_si_b_mat = tagbits;
    }
    num_di_b_subbank = num_di_b_mat * num_act_mats_hor_dir;  // normal cache or normal r/w for FA
    num_si_b_subbank = num_si_b_mat;                         //* num_act_mats_hor_dir_sl; inside the data is broadcast

    int num_addr_b_row_dec = _log2(num_r_subarray);
    num_addr_b_row_dec += _log2(num_subarrays / num_mats);
    int number_subbanks    = num_mats / num_act_mats_hor_dir;
    number_subbanks_decode = _log2(number_subbanks);  // TODO: add log2(num_subarray_per_bank) to FA/CAM

    num_rw_ports     = g_ip->num_rw_ports;
    num_rd_ports     = g_ip->num_rd_ports;
    num_wr_ports     = g_ip->num_wr_ports;
    num_se_rd_ports  = g_ip->num_se_rd_ports;
    num_search_ports = g_ip->num_search_ports;

    number_addr_bits_mat = num_addr_b_row_dec + _log2(deg_bl_muxing) + _log2(deg_sa_mux_l1_non_assoc) + _log2(Ndsam_lev_2);

    num_di_b_bank_per_port = g_ip->out_w + tagbits;  // TODO: out_w or block_sz?
    num_si_b_bank_per_port = tagbits;
    num_do_b_bank_per_port = g_ip->out_w + tagbits;
    num_so_b_bank_per_port = g_ip->out_w;

    if ((!is_tag) && (g_ip->data_assoc > 1) && (!g_ip->fast_access)) {
        number_way_select_signals_mat = g_ip->data_assoc;
    }

    // add ECC adjustment to all data signals that traverse on H-trees.
    if (g_ip->add_ecc_b_ == true) {
        ECC_adjustment();
    }

    is_valid = true;
}

//*** Calculate number of rows and columns in a subarray
bool DynamicParameter::calc_subarr_rc(unsigned int capacity_per_die)
{
    // If it's not an FA tag/data array, Ndwl should be at least two and Ndbl should be
    // at least two because an array is assumed to have at least one mat. A mat
    // consists of two rows and two columns of subarrays.
    if (Ndwl < 2 || Ndbl < 2) {
        return false;
    }

    if ((is_dram) && (!is_tag) && (Ndcm > 1)) {
        return false;  // For a DRAM array, each bitline has its own sense-amp
    }

    // if data array, let tagbits = 0
    if (is_tag) {
        if (g_ip->specific_tag) {
            tagbits = g_ip->tag_w;
        }
        else
        {
            tagbits = ADDRESS_BITS + EXTRA_TAG_BITS - _log2(capacity_per_die) + _log2(g_ip->tag_assoc * 2 - 1);
        }
        //    tagbits = (((tagbits + 3) >> 2) << 2); //FIXME: NAV: Why are we doing this?

        num_r_subarray = (int)ceil(capacity_per_die / (g_ip->nbanks * g_ip->block_sz * g_ip->tag_assoc * Ndbl * Nspd));
        num_c_subarray = (int)ceil((tagbits * g_ip->tag_assoc * Nspd / Ndwl));
    }
    else
    {
        num_r_subarray = (int)ceil(capacity_per_die / (g_ip->nbanks * g_ip->block_sz * g_ip->data_assoc * Ndbl * Nspd));
        num_c_subarray = (int)ceil((8 * g_ip->block_sz * g_ip->data_assoc * Nspd / Ndwl));
        if (g_ip->is_3d_mem) {
            double capacity_per_die_double = (double)g_ip->cache_sz / g_ip->num_die_3d;
            // num_c_subarray = 1 << (int)ceil((double)_log2( 8*capacity_per_die / (g_ip->nbanks * Ndbl * Ndwl) )/2 ) ;
            // num_r_subarray = 1 << (int)ceil((double)_log2( 8*capacity_per_die / (g_ip->nbanks * Ndbl * Ndwl * num_c_subarray)	) );
            num_c_subarray = g_ip->page_sz_bits / Ndwl;
            num_r_subarray
                = 1 << (int)floor(_log2((double)g_ip->cache_sz / g_ip->num_die_3d / num_c_subarray / g_ip->nbanks / Ndbl / Ndwl * 1024 * 1024 * 1024) + 0.5);
            if (g_ip->print_detail_debug) {
                cout << "parameter.cc: capacity_per_die_double = " << capacity_per_die_double << " Gbit" << endl;
                cout << "parameter.cc: g_ip->nbanks * Ndbl * Ndwl = " << (g_ip->nbanks * Ndbl * Ndwl) << endl;
                // cout  << "parameter.cc: subarray capacity = " << 8*capacity_per_die / (g_ip->nbanks * Ndbl * Ndwl) << endl;
                // cout  << "parameter.cc: total bit add per subarray = " << _log2( 8*capacity_per_die / (g_ip->nbanks * Ndbl * Ndwl) ) << endl;
                cout << "parameter.cc: num_r_subarray = " << num_r_subarray << endl;
                cout << "parameter.cc: num_c_subarray = " << num_c_subarray << endl;
            }
        }
    }

    if (num_r_subarray < MINSUBARRAYROWS) return false;
    if (num_r_subarray == 0) return false;
    if (num_r_subarray > MAXSUBARRAYROWS) return false;
    if (num_c_subarray < MINSUBARRAYCOLS) return false;
    if (num_c_subarray > MAXSUBARRAYCOLS) return false;

    num_subarrays = Ndwl * Ndbl;
    return true;
}

void DynamicParameter::print_args(void) const{
    cout << "DP(" << wtype << ", " << Ndwl << ", " << Ndbl << ", " << Ndcm << ", " << Nspd << ", " << Ndsam_lev_1 << ", " << Ndsam_lev_2 << ");" << endl;
}

// DynamicParameter::init_Mem()
//{
//}
//
// DynamicParameter::init_3DMem()
//{
//}
