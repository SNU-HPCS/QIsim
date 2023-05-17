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

#ifndef __RESULTS_MEM_ARRAY_H__
#define __RESULTS_MEM_ARRAY_H__

#include "power_def.h"

typedef struct
{
    int      Ndwl;
    int      Ndbl;
    double   Nspd;
    int      deg_bl_muxing;
    int      Ndsam_lev_1;
    int      Ndsam_lev_2;
    int      number_activated_mats_horizontal_direction;
    int      number_subbanks;
    int      page_size_in_bits;
    double   delay_route_to_bank;
    double   delay_crossbar;
    double   delay_addr_din_horizontal_htree;
    double   delay_addr_din_vertical_htree;
    double   delay_row_predecode_driver_and_block;
    double   delay_row_decoder;
    double   delay_bitlines;
    double   delay_sense_amp;
    double   delay_subarray_output_driver;
    double   delay_bit_mux_predecode_driver_and_block;
    double   delay_bit_mux_decoder;
    double   delay_senseamp_mux_lev_1_predecode_driver_and_block;
    double   delay_senseamp_mux_lev_1_decoder;
    double   delay_senseamp_mux_lev_2_predecode_driver_and_block;
    double   delay_senseamp_mux_lev_2_decoder;
    double   delay_input_htree;
    double   delay_output_htree;
    double   delay_dout_vertical_htree;
    double   delay_dout_horizontal_htree;
    double   delay_comparator;
    double   access_time;
    double   cycle_time;
    double   multisubbank_interleave_cycle_time;
    double   delay_request_network;
    double   delay_inside_mat;
    double   delay_reply_network;
    double   trcd;
    double   cas_latency;
    double   precharge_delay;
    powerDef power_routing_to_bank;
    powerDef power_addr_input_htree;
    powerDef power_data_input_htree;
    powerDef power_data_output_htree;
    powerDef power_addr_horizontal_htree;
    powerDef power_datain_horizontal_htree;
    powerDef power_dataout_horizontal_htree;
    powerDef power_addr_vertical_htree;
    powerDef power_datain_vertical_htree;
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
    powerDef power_crossbar;
    powerDef total_power;
    double   area;
    double   all_banks_height;
    double   all_banks_width;
    double   bank_height;
    double   bank_width;
    double   subarray_memory_cell_area_height;
    double   subarray_memory_cell_area_width;
    double   mat_height;
    double   mat_width;
    double   routing_area_height_within_bank;
    double   routing_area_width_within_bank;
    double   area_efficiency;
    //  double perc_power_dyn_routing_to_bank;
    //  double perc_power_dyn_addr_horizontal_htree;
    //  double perc_power_dyn_datain_horizontal_htree;
    //  double perc_power_dyn_dataout_horizontal_htree;
    //  double perc_power_dyn_addr_vertical_htree;
    //  double perc_power_dyn_datain_vertical_htree;
    //  double perc_power_dyn_row_predecoder_drivers;
    //  double perc_power_dyn_row_predecoder_blocks;
    //  double perc_power_dyn_row_decoders;
    //  double perc_power_dyn_bit_mux_predecoder_drivers;
    //  double perc_power_dyn_bit_mux_predecoder_blocks;
    //  double perc_power_dyn_bit_mux_decoders;
    //  double perc_power_dyn_senseamp_mux_lev_1_predecoder_drivers;
    //  double perc_power_dyn_senseamp_mux_lev_1_predecoder_blocks;
    //  double perc_power_dyn_senseamp_mux_lev_1_decoders;
    //  double perc_power_dyn_senseamp_mux_lev_2_predecoder_drivers;
    //  double perc_power_dyn_senseamp_mux_lev_2_predecoder_blocks;
    //  double perc_power_dyn_senseamp_mux_lev_2_decoders;
    //  double perc_power_dyn_bitlines;
    //  double perc_power_dyn_sense_amps;
    //  double perc_power_dyn_prechg_eq_drivers;
    //  double perc_power_dyn_subarray_output_drivers;
    //  double perc_power_dyn_dataout_vertical_htree;
    //  double perc_power_dyn_comparators;
    //  double perc_power_dyn_crossbar;
    //  double perc_power_dyn_spent_outside_mats;
    //  double perc_power_leak_routing_to_bank;
    //  double perc_power_leak_addr_horizontal_htree;
    //  double perc_power_leak_datain_horizontal_htree;
    //  double perc_power_leak_dataout_horizontal_htree;
    //  double perc_power_leak_addr_vertical_htree;
    //  double perc_power_leak_datain_vertical_htree;
    //  double perc_power_leak_row_predecoder_drivers;
    //  double perc_power_leak_row_predecoder_blocks;
    //  double perc_power_leak_row_decoders;
    //  double perc_power_leak_bit_mux_predecoder_drivers;
    //  double perc_power_leak_bit_mux_predecoder_blocks;
    //  double perc_power_leak_bit_mux_decoders;
    //  double perc_power_leak_senseamp_mux_lev_1_predecoder_drivers;
    //  double perc_power_leak_senseamp_mux_lev_1_predecoder_blocks;
    //  double perc_power_leak_senseamp_mux_lev_1_decoders;
    //  double perc_power_leak_senseamp_mux_lev_2_predecoder_drivers;
    //  double perc_power_leak_senseamp_mux_lev_2_predecoder_blocks;
    //  double perc_power_leak_senseamp_mux_lev_2_decoders;
    //  double perc_power_leak_bitlines;
    //  double perc_power_leak_sense_amps;
    //  double perc_power_leak_prechg_eq_drivers;
    //  double perc_power_leak_subarray_output_drivers;
    //  double perc_power_leak_dataout_vertical_htree;
    //  double perc_power_leak_comparators;
    //  double perc_power_leak_crossbar;
    //  double perc_leak_mats;
    //  double perc_active_mats;
    double refresh_power;
    double dram_refresh_period;
    double dram_array_availability;
    double dyn_read_energy_from_closed_page;
    double dyn_read_energy_from_open_page;
    double leak_power_subbank_closed_page;
    double leak_power_subbank_open_page;
    double leak_power_request_and_reply_networks;
    double activate_energy;
    double read_energy;
    double write_energy;
    double precharge_energy;
} results_mem_array;

#endif