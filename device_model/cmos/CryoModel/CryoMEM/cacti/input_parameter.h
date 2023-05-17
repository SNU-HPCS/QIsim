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

#ifndef __INPUT_PARAMETER_H__
#define __INPUT_PARAMETER_H__

#include <string>

#include "enum/wire_type.h"
#include "enum/mem_state.h"
#include "enum/mem_ecc.h"
#include "enum/mem_io_type.h"
#include "enum/mem_dimm.h"
#include "enum/mem_cad_metrics.h"
#include "enum/dimm_model.h"

class InputParameter
{
   public:
    InputParameter();
    void parse_cfg(const std::string& infile);

    bool error_checking();  // return false if the input parameters are problematic
    void display_ip();

    unsigned int cache_sz;  // in bytes
    unsigned int line_sz;
    unsigned int assoc;
    unsigned int nbanks;
    unsigned int out_w;  // == nr_bits_out
    bool         specific_tag;
    unsigned int tag_w;
    unsigned int access_mode;
    unsigned int obj_func_dyn_energy;
    unsigned int obj_func_dyn_power;
    unsigned int obj_func_leak_power;
    unsigned int obj_func_cycle_t;

    double       F_sz_nm;  // feature size in nm
    double       F_sz_um;  // feature size in um
    unsigned int num_rw_ports;
    unsigned int num_rd_ports;
    unsigned int num_wr_ports;
    unsigned int num_se_rd_ports;   // number of single ended read ports
    unsigned int num_search_ports;  // : number of search ports for CAM
    bool         is_main_mem;
    bool         is_3d_mem;
    bool         is_eDRAM;
    bool         print_detail_debug;
    bool         is_cache;
    bool         pure_ram;
    bool         pure_cam;
    bool         rpters_in_htree;  // if there are repeaters in htree segment
    unsigned int ver_htree_wires_over_array;
    unsigned int broadcast_addr_din_over_ver_htrees;
    unsigned int temp;

    unsigned int ram_cell_tech_type;
    unsigned int peri_global_tech_type;
    unsigned int data_arr_ram_cell_tech_type;
    unsigned int data_arr_peri_global_tech_type;
    unsigned int tag_arr_ram_cell_tech_type;
    unsigned int tag_arr_peri_global_tech_type;

    unsigned int burst_len;
    unsigned int int_prefetch_w;
    unsigned int page_sz_bits;

    unsigned int num_die_3d;
    unsigned int burst_depth;
    unsigned int io_width;
    unsigned int sys_freq_MHz;

    unsigned int tsv_is_subarray_type;
    unsigned int tsv_os_bank_type;
    unsigned int TSV_proj_type;

    int          partition_gran;
    unsigned int num_tier_row_sprd;
    unsigned int num_tier_col_sprd;
    bool         fine_gran_bank_lvl;

    unsigned int   ic_proj_type;      // interconnect_projection_type
    unsigned int   wire_is_mat_type;  // wire_inside_mat_type
    unsigned int   wire_os_mat_type;  // wire_outside_mat_type
    enum Wire_type wt;
    int            force_wiretype;
    bool           print_input_args;
    unsigned int   nuca_cache_sz;  // TODO
    int            ndbl, ndwl, ndsam1, ndsam2, ndcm;
    double         nspd;
    bool           force_cache_config;

    int cache_level;
    int cores;
    int nuca_bank_count;
    int force_nuca_bank;

    int delay_wt, dynamic_power_wt, leakage_power_wt, cycle_time_wt, area_wt;
    int delay_wt_nuca, dynamic_power_wt_nuca, leakage_power_wt_nuca, cycle_time_wt_nuca, area_wt_nuca;

    int delay_dev, dynamic_power_dev, leakage_power_dev, cycle_time_dev, area_dev;
    int delay_dev_nuca, dynamic_power_dev_nuca, leakage_power_dev_nuca, cycle_time_dev_nuca, area_dev_nuca;
    int ed;  // ED or ED2 optimization
    int nuca;

    bool         fast_access;
    unsigned int block_sz;  // bytes
    unsigned int tag_assoc;
    unsigned int data_assoc;
    bool         is_seq_acc;
    bool         fully_assoc;
    unsigned int nsets;  // == number_of_sets
    int          print_detail;

    bool add_ecc_b_;
    // parameters for design constraint
    double throughput;
    double latency;
    bool   pipelinable;
    int    pipeline_stages;
    int    per_stage_vector;
    bool   with_clock_grid;

    bool array_power_gated;
    bool bitline_floating;
    bool wl_power_gated;
    bool cl_power_gated;
    bool interconect_power_gated;
    bool power_gating;

    double perfloss;

    bool cl_vertical;

    // Parameters related to off-chip I/O

    double addr_timing, duty_cycle, mem_density, bus_bw, activity_dq, activity_ca, bus_freq;
    int    mem_data_width, num_mem_dq, num_clk, num_ca, num_dqs, num_dq;

    double rtt_value, ron_value, tflight_value;  // FIXME

    Mem_state iostate;

    /// char iostate, dram_ecc, io_type;

    Mem_ECC     dram_ecc;
    Mem_IO_type io_type;
    Mem_DIMM    dram_dimm;

    int num_bobs;  // BoB is buffer-on-board such as Intel SMB c102

    int capacity;  // in GB

    int num_channels_per_bob;  // 1 means no bob

    MemCad_metrics first_metric;

    MemCad_metrics second_metric;

    MemCad_metrics third_metric;

    DIMM_Model dimm_model;

    bool low_power_permitted;  // Not yet implemented. It determines acceptable VDDs.

    double load;  // between 0 to 1

    double row_buffer_hit_rate;

    double rd_2_wr_ratio;

    bool same_bw_in_bob;  // true if all the channels in the bob have the same bandwidth.

    bool mirror_in_bob;  // true if all the channels in the bob have the same configs

    bool total_power;  // false means just considering I/O Power

    bool verbose;
};

extern InputParameter* g_ip;

#endif
