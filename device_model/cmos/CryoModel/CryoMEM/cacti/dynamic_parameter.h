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

#ifndef __DYNAMIC_PARAMETER_H__
#define __DYNAMIC_PARAMETER_H__

#include <cstdint>
#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>

#include "enum/wire_type.h"
#include "area.h"

class DynamicParameter
{
   public:
    bool      is_tag;
    bool      pure_ram;
    bool      pure_cam;
    bool      fully_assoc;
    int       tagbits;
    int       num_subarrays;  // only for leakage computation  -- the number of subarrays per bank
    int       num_mats;       // only for leakage computation  -- the number of mats per bank
    double    Nspd;
    int       Ndwl;
    int       Ndbl;
    int       Ndcm;
    int       deg_bl_muxing;
    int       deg_senseamp_muxing_non_associativity;
    int       Ndsam_lev_1;
    int       Ndsam_lev_2;
    Wire_type wtype;  // merge from cacti-7 code to cacti3d code.

    int number_addr_bits_mat;    // per port
    int number_subbanks_decode;  // per_port
    int num_di_b_bank_per_port;
    int num_do_b_bank_per_port;
    int num_di_b_mat;
    int num_do_b_mat;
    int num_di_b_subbank;
    int num_do_b_subbank;

    int num_si_b_mat;
    int num_so_b_mat;
    int num_si_b_subbank;
    int num_so_b_subbank;
    int num_si_b_bank_per_port;
    int num_so_b_bank_per_port;

    int number_way_select_signals_mat;
    int num_act_mats_hor_dir;

    int           num_act_mats_hor_dir_sl;
    bool          is_dram;
    double        V_b_sense;
    unsigned int  num_r_subarray;
    unsigned int  num_c_subarray;
    int           tag_num_r_subarray;  //: fully associative cache tag and data must be computed together, data and tag must be separate
    int           tag_num_c_subarray;
    int           data_num_r_subarray;
    int           data_num_c_subarray;
    int           num_mats_h_dir;
    int           num_mats_v_dir;
    std::uint32_t ram_cell_tech_type;
    double        dram_refresh_period;

    DynamicParameter();
    DynamicParameter(
        bool         is_tag_,
        int          pure_ram_,
        int          pure_cam_,
        double       Nspd_,
        unsigned int Ndwl_,
        unsigned int Ndbl_,
        unsigned int Ndcm_,
        unsigned int Ndsam_lev_1_,
        unsigned int Ndsam_lev_2_,
        Wire_type    wt,  // merged from cacti-7 to cacti3d
        bool         is_main_mem_);

    int          use_inp_params;
    unsigned int num_rw_ports;
    unsigned int num_rd_ports;
    unsigned int num_wr_ports;
    unsigned int num_se_rd_ports;  // number of single ended read ports
    unsigned int num_search_ports;
    unsigned int out_w;  // == nr_bits_out
    bool         is_main_mem;
    Area         cell, cam_cell;  // cell is the sram_cell in both nomal cache/ram and FA.
    bool         is_valid;

   private:
    void ECC_adjustment();
    void init_CAM();
    void init_FA();
    bool calc_subarr_rc(unsigned int cap);  // to calculate and check subarray rows and columns

    // GH
    friend class boost::serialization::access;

    template<typename Archive>
    void serialize(Archive &ar, const unsigned int version){
        ar & is_tag;
        ar & pure_ram;
        ar & pure_cam;
        ar & fully_assoc;
        ar & tagbits;
        ar & num_subarrays;
        ar & num_mats;
        ar & Nspd;
        ar & Ndwl;
        ar & Ndbl;
        ar & Ndcm;
        ar & deg_bl_muxing;
        ar & deg_senseamp_muxing_non_associativity;
        ar & Ndsam_lev_1;
        ar & Ndsam_lev_2;
        ar & wtype;
        ar & number_addr_bits_mat;
        ar & number_subbanks_decode;
        ar & num_di_b_bank_per_port;
        ar & num_do_b_bank_per_port;
        ar & num_di_b_mat;
        ar & num_do_b_mat;
        ar & num_di_b_subbank;
        ar & num_do_b_subbank;
        ar & num_si_b_mat;
        ar & num_so_b_mat;
        ar & num_si_b_subbank;
        ar & num_so_b_subbank;
        ar & num_si_b_bank_per_port;
        ar & num_so_b_bank_per_port;
        ar & number_way_select_signals_mat;
        ar & num_act_mats_hor_dir;
        ar & num_act_mats_hor_dir_sl;
        ar & is_dram;
        ar & V_b_sense;
        ar & num_r_subarray;
        ar & num_c_subarray;
        ar & tag_num_r_subarray;
        ar & tag_num_c_subarray;
        ar & data_num_r_subarray;
        ar & data_num_c_subarray;
        ar & num_mats_h_dir;
        ar & num_mats_v_dir;
        ar & ram_cell_tech_type;
        ar & dram_refresh_period;
        ar & use_inp_params;
        ar & num_rw_ports;
        ar & num_rd_ports;
        ar & num_wr_ports;
        ar & num_se_rd_ports;
        ar & num_search_ports;
        ar & out_w;
        ar & is_main_mem;
        ar & cell;
        ar & cam_cell;
        ar & is_valid;
    }
   public:
    void print_args(void) const;
};

#endif
