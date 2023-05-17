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

#ifndef __MEM_ARRAY_H__
#define __MEM_ARRAY_H__

#include <memory>

#include "power_def.h"
#include "enum/wire_type.h"

class min_values_t;
class DynamicParameter;

class mem_array
{
   public:
    int      Ndcm;
    int      Ndwl;
    int      Ndbl;
    double   Nspd;
    int      deg_bl_muxing;
    int      Ndsam_lev_1;
    int      Ndsam_lev_2;
    double   access_time;
    double   cycle_time;
    double   multisubbank_interleave_cycle_time;
    double   area_ram_cells;
    double   area;
    powerDef power;
    double   delay_senseamp_mux_decoder;
    double   delay_before_subarray_output_driver;
    double   delay_from_subarray_output_driver_to_output;
    double   height;
    double   width;

    double bank_length;
    double bank_height;
    double mat_length;
    double mat_height;
    double subarray_length;
    double subarray_height;
    double area_per_bank;

    double delay_route_to_bank, delay_input_htree, delay_row_predecode_driver_and_block, delay_row_decoder, delay_bitlines, delay_sense_amp,
        delay_subarray_output_driver, delay_dout_htree, delay_comparator, delay_matchlines;
    // CACTI3DD 3d stats
    double delay_row_activate_net, delay_local_wordline,

        delay_column_access_net, delay_column_predecoder, delay_column_decoder, delay_column_selectline, delay_datapath_net, delay_global_data,
        delay_local_data_and_drv, delay_data_buffer;

    double energy_row_activate_net, energy_row_predecode_driver_and_block, energy_row_decoder, energy_local_wordline, energy_bitlines, energy_sense_amp,
        energy_column_access_net, energy_column_predecoder, energy_column_decoder, energy_column_selectline, energy_datapath_net, energy_global_data,
        energy_local_data_and_drv, energy_data_buffer, energy_subarray_output_driver;

    double all_banks_height, all_banks_width, area_efficiency;

    powerDef power_routing_to_bank;
    powerDef power_addr_input_htree;
    powerDef power_data_input_htree;
    powerDef power_data_output_htree;
    powerDef power_htree_in_search;
    powerDef power_htree_out_search;
    powerDef power_row_predecoder_drivers;
    powerDef power_row_predecoder_blocks;
    powerDef power_row_decoders;
    powerDef power_bit_mux_predecoder_drivers;
    powerDef power_bit_mux_predecoder_blocks;
    powerDef power_bit_mux_decoders;
    powerDef power_senseamp_mux_lev_1_predecoder_drivers;
    powerDef power_senseamp_mux_lev_1_predecoder_blocks;
    powerDef power_senseamp_mux_lev_1_decoders;
    powerDef power_senseamp_mux_lev_2_predecoder_drivers;
    powerDef power_senseamp_mux_lev_2_predecoder_blocks;
    powerDef power_senseamp_mux_lev_2_decoders;
    powerDef power_bitlines;
    powerDef power_sense_amps;
    powerDef power_prechg_eq_drivers;
    powerDef power_output_drivers_at_subarray;
    powerDef power_dataout_vertical_htree;
    powerDef power_comparators;

    powerDef power_cam_bitline_precharge_eq_drv;
    powerDef power_searchline;
    powerDef power_searchline_precharge;
    powerDef power_matchlines;
    powerDef power_matchline_precharge;
    powerDef power_matchline_to_wordline_drv;

    min_values_t * arr_min;
    enum Wire_type wt;

    // dram stats
    double activate_energy, read_energy, write_energy, precharge_energy, refresh_power, leak_power_subbank_closed_page, leak_power_subbank_open_page,
        leak_power_request_and_reply_networks;

    double precharge_delay;

    // Power-gating stats
    double array_leakage;
    double wl_leakage;
    double cl_leakage;

    double sram_sleep_tx_width, wl_sleep_tx_width, cl_sleep_tx_width;
    double sram_sleep_tx_area, wl_sleep_tx_area, cl_sleep_tx_area;
    double sram_sleep_wakeup_latency, wl_sleep_wakeup_latency, cl_sleep_wakeup_latency, bl_floating_wakeup_latency;
    double sram_sleep_wakeup_energy, wl_sleep_wakeup_energy, cl_sleep_wakeup_energy, bl_floating_wakeup_energy;

    int num_active_mats;
    int num_submarray_mats;

    // GH
    // static bool lt(const mem_array *m1, const mem_array *m2);
    class lt{
    public:
        bool operator()(const mem_array *m1, const mem_array *m2) const noexcept;
    };

    // CACTI3DD 3d dram stats
    double       t_RCD, t_RAS, t_RC, t_CAS, t_RP, t_RRD;
    double       activate_power, read_power, write_power, peak_read_power;
    int          num_row_subarray, num_col_subarray;
    double       delay_TSV_tot, area_TSV_tot, dyn_pow_TSV_tot, dyn_pow_TSV_per_access;
    unsigned int num_TSV_tot;
    double       area_lwl_drv, area_row_predec_dec, area_col_predec_dec, area_subarray, area_bus, area_address_bus, area_data_bus, area_data_drv, area_IOSA,
        area_sense_amp;

    // GH
    std::unique_ptr<DynamicParameter> dp;
};

#endif
