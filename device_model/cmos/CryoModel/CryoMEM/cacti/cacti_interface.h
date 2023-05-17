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
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.”
 *
 ***************************************************************************/

#ifndef __CACTI_INTERFACE_H__
#define __CACTI_INTERFACE_H__

#include <string>

#include "uca_org_t.h"

class CactiInput;
class InputParameter;

void reconfigure(InputParameter *local_interface, uca_org_t *fin_res);

uca_org_t cacti_interface();
// McPAT's plain interface, please keep !!!
uca_org_t cacti_interface(InputParameter *const local_interface);
// McPAT's plain interface, please keep !!!
uca_org_t init_interface(InputParameter *const local_interface);
// McPAT's plain interface, please keep !!!
uca_org_t cacti_interface(
    int    cache_size,
    int    line_size,
    int    associativity,
    int    rw_ports,
    int    excl_read_ports,
    int    excl_write_ports,
    int    single_ended_read_ports,
    int    search_ports,
    int    banks,
    double tech_node,
    int    output_width,
    int    specific_tag,
    int    tag_width,
    int    access_mode,
    int    cache,
    int    main_mem,
    int    obj_func_delay,
    int    obj_func_dynamic_power,
    int    obj_func_leakage_power,
    int    obj_func_cycle_time,
    int    obj_func_area,
    int    dev_func_delay,
    int    dev_func_dynamic_power,
    int    dev_func_leakage_power,
    int    dev_func_area,
    int    dev_func_cycle_time,
    int    ed_ed2_none,  // 0 - ED, 1 - ED^2, 2 - use weight and deviate
    int    temp,
    int    wt,  // 0 - default(search across everything), 1 - global, 2 - 5% delay penalty, 3 - 10%, 4 - 20 %, 5 - 30%, 6 - low-swing
    int    data_arr_ram_cell_tech_flavor_in,
    int    data_arr_peri_global_tech_flavor_in,
    int    tag_arr_ram_cell_tech_flavor_in,
    int    tag_arr_peri_global_tech_flavor_in,
    int    interconnect_projection_type_in,
    int    wire_inside_mat_type_in,
    int    wire_outside_mat_type_in,
    int    REPEATERS_IN_HTREE_SEGMENTS_in,
    int    VERTICAL_HTREE_WIRES_OVER_THE_ARRAY_in,
    int    BROADCAST_ADDR_DATAIN_OVER_VERTICAL_HTREES_in,
    int    PAGE_SIZE_BITS_in,
    int    BURST_LENGTH_in,
    int    INTERNAL_PREFETCH_WIDTH_in,
    int    force_wiretype,
    int    wiretype,
    int    force_config,
    int    ndwl,
    int    ndbl,
    int    nspd,
    int    ndcm,
    int    ndsam1,
    int    ndsam2,
    int    ecc);
//    int cache_size,
//    int line_size,
//    int associativity,
//    int rw_ports,
//    int excl_read_ports,
//    int excl_write_ports,
//    int single_ended_read_ports,
//    int banks,
//    double tech_node,
//    int output_width,
//    int specific_tag,
//    int tag_width,
//    int access_mode,
//    int cache,
//    int main_mem,
//    int obj_func_delay,
//    int obj_func_dynamic_power,
//    int obj_func_leakage_power,
//    int obj_func_area,
//    int obj_func_cycle_time,
//    int dev_func_delay,
//    int dev_func_dynamic_power,
//    int dev_func_leakage_power,
//    int dev_func_area,
//    int dev_func_cycle_time,
//    int temp,
//    int data_arr_ram_cell_tech_flavor_in,
//    int data_arr_peri_global_tech_flavor_in,
//    int tag_arr_ram_cell_tech_flavor_in,
//    int tag_arr_peri_global_tech_flavor_in,
//    int interconnect_projection_type_in,
//    int wire_inside_mat_type_in,
//    int wire_outside_mat_type_in,
//    int REPEATERS_IN_HTREE_SEGMENTS_in,
//    int VERTICAL_HTREE_WIRES_OVER_THE_ARRAY_in,
//    int BROADCAST_ADDR_DATAIN_OVER_VERTICAL_HTREES_in,
////    double MAXAREACONSTRAINT_PERC_in,
////    double MAXACCTIMECONSTRAINT_PERC_in,
////    double MAX_PERC_DIFF_IN_DELAY_FROM_BEST_DELAY_REPEATER_SOLUTION_in,
//    int PAGE_SIZE_BITS_in,
//    int BURST_LENGTH_in,
//    int INTERNAL_PREFETCH_WIDTH_in);

// Naveen's interface
uca_org_t cacti_interface(
    int    cache_size,
    int    line_size,
    int    associativity,
    int    rw_ports,
    int    excl_read_ports,
    int    excl_write_ports,
    int    single_ended_read_ports,
    int    banks,
    double tech_node,
    int    page_sz,
    int    burst_length,
    int    pre_width,
    int    output_width,
    int    specific_tag,
    int    tag_width,
    int    access_mode,  // 0 normal, 1 seq, 2 fast
    int    cache,        // scratch ram or cache
    int    main_mem,
    int    obj_func_delay,
    int    obj_func_dynamic_power,
    int    obj_func_leakage_power,
    int    obj_func_area,
    int    obj_func_cycle_time,
    int    dev_func_delay,
    int    dev_func_dynamic_power,
    int    dev_func_leakage_power,
    int    dev_func_area,
    int    dev_func_cycle_time,
    int    ed_ed2_none,  // 0 - ED, 1 - ED^2, 2 - use weight and deviate
    int    temp,
    int    wt,  // 0 - default(search across everything), 1 - global, 2 - 5% delay penalty, 3 - 10%, 4 - 20 %, 5 - 30%, 6 - low-swing
    int    data_arr_ram_cell_tech_flavor_in,
    int    data_arr_peri_global_tech_flavor_in,
    int    tag_arr_ram_cell_tech_flavor_in,
    int    tag_arr_peri_global_tech_flavor_in,
    int    interconnect_projection_type_in,  // 0 - aggressive, 1 - normal
    int    wire_inside_mat_type_in,
    int    wire_outside_mat_type_in,
    int    is_nuca,  // 0 - UCA, 1 - NUCA
    int    core_count,
    int    cache_level,  // 0 - L2, 1 - L3
    int    nuca_bank_count,
    int    nuca_obj_func_delay,
    int    nuca_obj_func_dynamic_power,
    int    nuca_obj_func_leakage_power,
    int    nuca_obj_func_area,
    int    nuca_obj_func_cycle_time,
    int    nuca_dev_func_delay,
    int    nuca_dev_func_dynamic_power,
    int    nuca_dev_func_leakage_power,
    int    nuca_dev_func_area,
    int    nuca_dev_func_cycle_time,
    int    REPEATERS_IN_HTREE_SEGMENTS_in,  // TODO for now only wires with repeaters are supported
    int    p_input);

// CACTI3DD interface
uca_org_t cacti_interface(
    int    cache_size,
    int    line_size,
    int    associativity,
    int    rw_ports,
    int    excl_read_ports,  // para5
    int    excl_write_ports,
    int    single_ended_read_ports,
    int    search_ports,
    int    banks,
    double tech_node,  // para10
    int    output_width,
    int    specific_tag,
    int    tag_width,
    int    access_mode,
    int    cache,  // para15
    int    main_mem,
    int    obj_func_delay,
    int    obj_func_dynamic_power,
    int    obj_func_leakage_power,
    int    obj_func_cycle_time,  // para20
    int    obj_func_area,
    int    dev_func_delay,
    int    dev_func_dynamic_power,
    int    dev_func_leakage_power,
    int    dev_func_area,  // para25
    int    dev_func_cycle_time,
    int    ed_ed2_none,  // 0 - ED, 1 - ED^2, 2 - use weight and deviate
    int    temp,
    int    wt,  // 0 - default(search across everything), 1 - global, 2 - 5% delay penalty, 3 - 10%, 4 - 20 %, 5 - 30%, 6 - low-swing
    int    data_arr_ram_cell_tech_flavor_in,  // para30
    int    data_arr_peri_global_tech_flavor_in,
    int    tag_arr_ram_cell_tech_flavor_in,
    int    tag_arr_peri_global_tech_flavor_in,
    int    interconnect_projection_type_in,
    int    wire_inside_mat_type_in,  // para35
    int    wire_outside_mat_type_in,
    int    REPEATERS_IN_HTREE_SEGMENTS_in,
    int    VERTICAL_HTREE_WIRES_OVER_THE_ARRAY_in,
    int    BROADCAST_ADDR_DATAIN_OVER_VERTICAL_HTREES_in,
    int    PAGE_SIZE_BITS_in,  // para40
    int    BURST_LENGTH_in,
    int    INTERNAL_PREFETCH_WIDTH_in,
    int    force_wiretype,
    int    wiretype,
    int    force_config,  // para45
    int    ndwl,
    int    ndbl,
    int    nspd,
    int    ndcm,
    int    ndsam1,  // para50
    int    ndsam2,
    int    ecc,
    int    is_3d_dram,
    int    burst_depth,
    int    IO_width,
    int    sys_freq,
    int    debug_detail,
    int    num_dies,
    int    tsv_gran_is_subarray,
    int    tsv_gran_os_bank,
    int    num_tier_row_sprd,
    int    num_tier_col_sprd,
    int    partition_level);

#endif
