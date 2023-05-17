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
#include <string>
#include <cstdio>
#include <cstring>
#include <cassert>

#include "input_parameter.h"
#include "basic_circuit.h"
#include "enum/ram_cell_tech_type_num.h"

using namespace std;

InputParameter *g_ip;

InputParameter::InputParameter()
    : array_power_gated(false),
      bitline_floating(false),
      wl_power_gated(false),
      cl_power_gated(false),
      interconect_power_gated(false),
      power_gating(false),
      cl_vertical(true),
      is_eDRAM(false)
{
}

/* Parses "cache.cfg" file */
void InputParameter::parse_cfg(const string &in_file)
{
    FILE *fp = fopen(in_file.c_str(), "r");
    char  line[5000];
    char  jk[5000];
    char  temp_var[5000];

    if (!fp) {
        cout << in_file << " is missing!\n";
        exit(-1);
    }

    while (fscanf(fp, "%[^\n]\n", line) != EOF) {
        if (!strncmp("-size", line, strlen("-size"))) {
            sscanf(line, "-size %[(:-~)*]%u", jk, &(cache_sz));
            if (g_ip->print_detail_debug) cout << "cache size: " << g_ip->cache_sz << "GB" << endl;
            continue;
        }

        if (!strncmp("-page size", line, strlen("-page size"))) {
            sscanf(line, "-page size %[(:-~)*]%u", jk, &(page_sz_bits));
            continue;
        }

        if (!strncmp("-burst length", line, strlen("-burst length"))) {
            sscanf(line, "-burst %[(:-~)*]%u", jk, &(burst_len));
            continue;
        }

        if (!strncmp("-internal prefetch width", line, strlen("-internal prefetch width"))) {
            sscanf(line, "-internal prefetch %[(:-~)*]%u", jk, &(int_prefetch_w));
            continue;
        }

        if (!strncmp("-block", line, strlen("-block"))) {
            sscanf(line, "-block size (bytes) %d", &(line_sz));
            continue;
        }

        if (!strncmp("-associativity", line, strlen("-associativity"))) {
            sscanf(line, "-associativity %d", &(assoc));
            continue;
        }

        if (!strncmp("-read-write", line, strlen("-read-write"))) {
            sscanf(line, "-read-write port %d", &(num_rw_ports));
            continue;
        }

        if (!strncmp("-exclusive read", line, strlen("exclusive read"))) {
            sscanf(line, "-exclusive read port %d", &(num_rd_ports));
            continue;
        }

        if (!strncmp("-exclusive write", line, strlen("-exclusive write"))) {
            sscanf(line, "-exclusive write port %d", &(num_wr_ports));
            continue;
        }

        if (!strncmp("-single ended", line, strlen("-single ended"))) {
            sscanf(line, "-single %[(:-~)*]%d", jk, &(num_se_rd_ports));
            continue;
        }

        if (!strncmp("-search", line, strlen("-search"))) {
            sscanf(line, "-search port %d", &(num_search_ports));
            continue;
        }

        if (!strncmp("-UCA bank", line, strlen("-UCA bank"))) {
            sscanf(line, "-UCA bank%[((:-~)| )*]%d", jk, &(nbanks));
            continue;
        }

        if (!strncmp("-technology", line, strlen("-technology"))) {
            sscanf(line, "-technology (u) %lf", &(F_sz_um));
            F_sz_nm = F_sz_um * 1000;
            continue;
        }

        if (!strncmp("-output/input", line, strlen("-output/input"))) {
            sscanf(line, "-output/input bus %[(:-~)*]%d", jk, &(out_w));
            continue;
        }

        if (!strncmp("-operating temperature", line, strlen("-operating temperature"))) {
            sscanf(line, "-operating temperature %[(:-~)*]%d", jk, &(temp));
            continue;
        }

        if (!strncmp("-cache type", line, strlen("-cache type"))) {
            sscanf(line, "-cache type%[^\"]\"%[^\"]\"", jk, temp_var);

            if (!strncmp("cache", temp_var, sizeof("cache"))) {
                is_cache = true;
            }
            else
            {
                is_cache = false;
            }

            if (!strncmp("main memory", temp_var, sizeof("main memory"))) {
                is_main_mem = true;
            }
            else
            {
                is_main_mem = false;
            }

            if (!strncmp("3D memory or 2D main memory", temp_var, sizeof("3D memory or 2D main memory"))) {
                is_3d_mem   = true;
                is_main_mem = true;
            }
            else
            {
                is_3d_mem = false;
                // is_main_mem = false;
            }

            if (g_ip->print_detail_debug) {
                cout << "io.cc: is_3d_mem = " << is_3d_mem << endl;
            }

            if (!strncmp("cam", temp_var, sizeof("cam"))) {
                pure_cam = true;
            }
            else
            {
                pure_cam = false;
            }

            if (!strncmp("ram", temp_var, sizeof("ram"))) {
                pure_ram = true;
            }
            else
            {
                if (!is_main_mem)
                    pure_ram = false;
                else
                    pure_ram = true;
            }

            continue;
        }

        if (!strncmp("-3T-eDRAM", line, strlen("-3T-eDRAM"))) {
            is_eDRAM = true;
        }

        if (!strncmp("-print option", line, strlen("-print option"))) {
            sscanf(line, "-print option%[^\"]\"%[^\"]\"", jk, temp_var);

            if (!strncmp("debug detail", temp_var, sizeof("debug detail"))) {
                print_detail_debug = true;
            }
            else
            {
                print_detail_debug = false;
            }
            if (g_ip->print_detail_debug) {
                cout << "io.cc: print_detail_debug = " << print_detail_debug << endl;
            }
            continue;
        }

        if (!strncmp("-burst depth", line, strlen("-burst depth"))) {
            sscanf(line, "-burst %[(:-~)*]%u", jk, &(burst_depth));
            continue;
        }

        if (!strncmp("-IO width", line, strlen("-IO width"))) {
            sscanf(line, "-IO %[(:-~)*]%u", jk, &(io_width));
            continue;
        }

        if (!strncmp("-system frequency", line, strlen("-system frequency"))) {
            sscanf(line, "-system frequency %[(:-~)*]%u", jk, &(sys_freq_MHz));
            if (g_ip->print_detail_debug) cout << "system frequency: " << g_ip->sys_freq_MHz << endl;
            continue;
        }

        if (!strncmp("-stacked die", line, strlen("-stacked die"))) {
            sscanf(line, "-stacked die %[(:-~)*]%u", jk, &(num_die_3d));
            if (g_ip->print_detail_debug) cout << "num_die_3d: " << g_ip->num_die_3d << endl;
            continue;
        }

        if (!strncmp("-partitioning granularity", line, strlen("-partitioning granularity"))) {
            sscanf(line, "-partitioning %[(:-~)*]%u", jk, &(partition_gran));
            if (g_ip->print_detail_debug) cout << "partitioning granularity: " << g_ip->partition_gran << endl;
            continue;
        }

        if (!strncmp("-TSV projection", line, strlen("-TSV projection"))) {
            sscanf(line, "-TSV %[(:-~)*]%u", jk, &(TSV_proj_type));
            if (g_ip->print_detail_debug) cout << "TSV projection: " << g_ip->TSV_proj_type << endl;
            continue;
        }

        // g_ip->print_detail_debug = debug_detail;

        // g_ip->partition_gran = 1;

        // --- These two parameters are supposed for bank level partitioning, currently not shown to public
        g_ip->num_tier_row_sprd = 1;
        g_ip->num_tier_col_sprd = 1;

        if (!strncmp("-tag size", line, strlen("-tag size"))) {
            sscanf(line, "-tag size%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("default", temp_var, sizeof("default"))) {
                specific_tag = false;
                tag_w        = 42; /* the actual value is calculated
                                    * later based on the cache size, bank count, and associativity
                                    */
            }
            else
            {
                specific_tag = true;
                sscanf(line, "-tag size (b) %d", &(tag_w));
            }
            continue;
        }

        if (!strncmp("-access mode", line, strlen("-access mode"))) {
            sscanf(line, "-access %[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("fast", temp_var, strlen("fast"))) {
                access_mode = 2;
            }
            else if (!strncmp("sequential", temp_var, strlen("sequential")))
            {
                access_mode = 1;
            }
            else if (!strncmp("normal", temp_var, strlen("normal")))
            {
                access_mode = 0;
            }
            else
            {
                cout << "ERROR: Invalid access mode!\n";
                exit(0);
            }
            continue;
        }

        if (!strncmp("-Data array cell type", line, strlen("-Data array cell type"))) {
            sscanf(line, "-Data array cell type %[^\"]\"%[^\"]\"", jk, temp_var);

            if (!strncmp("itrs-hp", temp_var, strlen("itrs-hp"))) {
                data_arr_ram_cell_tech_type = 0;
            }
            else if (!strncmp("itrs-lstp", temp_var, strlen("itrs-lstp")))
            {
                data_arr_ram_cell_tech_type = 1;
            }
            else if (!strncmp("itrs-lop", temp_var, strlen("itrs-lop")))
            {
                data_arr_ram_cell_tech_type = 2;
            }
            else if (!strncmp("lp-dram", temp_var, strlen("lp-dram")))
            {
                data_arr_ram_cell_tech_type = 3;
            }
            else if (!strncmp("comm-dram", temp_var, strlen("comm-dram")))
            {
                data_arr_ram_cell_tech_type = 4;
            }
            else
            {
                cout << "ERROR: Invalid type!\n";
                exit(0);
            }
            continue;
        }

        if (!strncmp("-Data array peripheral type", line, strlen("-Data array peripheral type"))) {
            sscanf(line, "-Data array peripheral type %[^\"]\"%[^\"]\"", jk, temp_var);

            if (!strncmp("itrs-hp", temp_var, strlen("itrs-hp"))) {
                data_arr_peri_global_tech_type = 0;
            }
            else if (!strncmp("itrs-lstp", temp_var, strlen("itrs-lstp")))
            {
                data_arr_peri_global_tech_type = 1;
            }
            else if (!strncmp("itrs-lop", temp_var, strlen("itrs-lop")))
            {
                data_arr_peri_global_tech_type = 2;
            }
            else
            {
                cout << "ERROR: Invalid type!\n";
                exit(0);
            }
            continue;
        }

        if (!strncmp("-Tag array cell type", line, strlen("-Tag array cell type"))) {
            sscanf(line, "-Tag array cell type %[^\"]\"%[^\"]\"", jk, temp_var);

            if (!strncmp("itrs-hp", temp_var, strlen("itrs-hp"))) {
                tag_arr_ram_cell_tech_type = 0;
            }
            else if (!strncmp("itrs-lstp", temp_var, strlen("itrs-lstp")))
            {
                tag_arr_ram_cell_tech_type = 1;
            }
            else if (!strncmp("itrs-lop", temp_var, strlen("itrs-lop")))
            {
                tag_arr_ram_cell_tech_type = 2;
            }
            else if (!strncmp("lp-dram", temp_var, strlen("lp-dram")))
            {
                tag_arr_ram_cell_tech_type = 3;
            }
            else if (!strncmp("comm-dram", temp_var, strlen("comm-dram")))
            {
                tag_arr_ram_cell_tech_type = 4;
            }
            else
            {
                cout << "ERROR: Invalid type!\n";
                exit(0);
            }
            continue;
        }

        if (!strncmp("-Tag array peripheral type", line, strlen("-Tag array peripheral type"))) {
            sscanf(line, "-Tag array peripheral type %[^\"]\"%[^\"]\"", jk, temp_var);

            if (!strncmp("itrs-hp", temp_var, strlen("itrs-hp"))) {
                tag_arr_peri_global_tech_type = 0;
            }
            else if (!strncmp("itrs-lstp", temp_var, strlen("itrs-lstp")))
            {
                tag_arr_peri_global_tech_type = 1;
            }
            else if (!strncmp("itrs-lop", temp_var, strlen("itrs-lop")))
            {
                tag_arr_peri_global_tech_type = 2;
            }
            else
            {
                cout << "ERROR: Invalid type!\n";
                exit(0);
            }
            continue;
        }
        if (!strncmp("-design", line, strlen("-design"))) {
            sscanf(line, "-%[((:-~)| |,)*]%d:%d:%d:%d:%d", jk, &(delay_wt), &(dynamic_power_wt), &(leakage_power_wt), &(cycle_time_wt), &(area_wt));
            continue;
        }

        if (!strncmp("-deviate", line, strlen("-deviate"))) {
            sscanf(line, "-%[((:-~)| |,)*]%d:%d:%d:%d:%d", jk, &(delay_dev), &(dynamic_power_dev), &(leakage_power_dev), &(cycle_time_dev), &(area_dev));
            continue;
        }

        if (!strncmp("-Optimize", line, strlen("-Optimize"))) {
            sscanf(line, "-Optimize  %[^\"]\"%[^\"]\"", jk, temp_var);

            if (!strncmp("ED^2", temp_var, strlen("ED^2"))) {
                ed = 2;
            }
            else if (!strncmp("ED", temp_var, strlen("ED")))
            {
                ed = 1;
            }
            else
            {
                ed = 0;
            }
        }

        if (!strncmp("-NUCAdesign", line, strlen("-NUCAdesign"))) {
            sscanf(
                line,
                "-%[((:-~)| |,)*]%d:%d:%d:%d:%d",
                jk,
                &(delay_wt_nuca),
                &(dynamic_power_wt_nuca),
                &(leakage_power_wt_nuca),
                &(cycle_time_wt_nuca),
                &(area_wt_nuca));
            continue;
        }

        if (!strncmp("-NUCAdeviate", line, strlen("-NUCAdeviate"))) {
            sscanf(
                line,
                "-%[((:-~)| |,)*]%d:%d:%d:%d:%d",
                jk,
                &(delay_dev_nuca),
                &(dynamic_power_dev_nuca),
                &(leakage_power_dev_nuca),
                &(cycle_time_dev_nuca),
                &(area_dev_nuca));
            continue;
        }

        if (!strncmp("-Cache model", line, strlen("-cache model"))) {
            sscanf(line, "-Cache model %[^\"]\"%[^\"]\"", jk, temp_var);

            if (!strncmp("UCA", temp_var, strlen("UCA"))) {
                nuca = 0;
            }
            else
            {
                nuca = 1;
            }
            continue;
        }

        if (!strncmp("-NUCA bank", line, strlen("-NUCA bank"))) {
            sscanf(line, "-NUCA bank count %d", &(nuca_bank_count));

            if (nuca_bank_count != 0) {
                force_nuca_bank = 1;
            }
            continue;
        }

        if (!strncmp("-Wire inside mat", line, strlen("-Wire inside mat"))) {
            sscanf(line, "-Wire%[^\"]\"%[^\"]\"", jk, temp_var);

            if (!strncmp("global", temp_var, strlen("global"))) {
                wire_is_mat_type = 2;
                continue;
            }
            else if (!strncmp("local", temp_var, strlen("local")))
            {
                wire_is_mat_type = 0;
                continue;
            }
            else
            {
                wire_is_mat_type = 1;
                continue;
            }
        }

        if (!strncmp("-Wire outside mat", line, strlen("-Wire outside mat"))) {
            sscanf(line, "-Wire%[^\"]\"%[^\"]\"", jk, temp_var);

            if (!strncmp("global", temp_var, strlen("global"))) {
                wire_os_mat_type = 2;
            }
            else
            {
                wire_os_mat_type = 1;
            }
            continue;
        }

        if (!strncmp("-Interconnect projection", line, strlen("-Interconnect projection"))) {
            sscanf(line, "-Interconnect projection%[^\"]\"%[^\"]\"", jk, temp_var);

            if (!strncmp("aggressive", temp_var, strlen("aggressive"))) {
                ic_proj_type = 0;
            }
            else
            {
                ic_proj_type = 1;
            }
            continue;
        }

        if (!strncmp("-Wire signaling", line, strlen("-wire signaling"))) {
            sscanf(line, "-Wire%[^\"]\"%[^\"]\"", jk, temp_var);

            if (!strncmp("default", temp_var, strlen("default"))) {
                force_wiretype = 0;
                wt             = Global;
            }
            else if (!(strncmp("Global_10", temp_var, strlen("Global_10"))))
            {
                force_wiretype = 1;
                wt             = Global_10;
            }
            else if (!(strncmp("Global_20", temp_var, strlen("Global_20"))))
            {
                force_wiretype = 1;
                wt             = Global_20;
            }
            else if (!(strncmp("Global_30", temp_var, strlen("Global_30"))))
            {
                force_wiretype = 1;
                wt             = Global_30;
            }
            else if (!(strncmp("Global_5", temp_var, strlen("Global_5"))))
            {
                force_wiretype = 1;
                wt             = Global_5;
            }
            else if (!(strncmp("Global", temp_var, strlen("Global"))))
            {
                force_wiretype = 1;
                wt             = Global;
            }
            else if (!(strncmp("fullswing", temp_var, strlen("fullswing"))))
            {
                force_wiretype = 1;
                wt             = Full_swing;
            }
            else if (!(strncmp("lowswing", temp_var, strlen("lowswing"))))
            {
                force_wiretype = 1;
                wt             = Low_swing;
            }
            else
            {
                cout << "Unknown wire type!\n";
                exit(0);
            }
            continue;
        }

        if (!strncmp("-Core", line, strlen("-Core"))) {
            sscanf(line, "-Core count %d\n", &(cores));
            if (cores > 16) {
                printf("No. of cores should be less than 16!\n");
            }
            continue;
        }

        if (!strncmp("-Cache level", line, strlen("-Cache level"))) {
            sscanf(line, "-Cache l%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("L2", temp_var, strlen("L2"))) {
                cache_level = 0;
            }
            else
            {
                cache_level = 1;
            }
        }

        if (!strncmp("-Print level", line, strlen("-Print level"))) {
            sscanf(line, "-Print l%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("DETAILED", temp_var, strlen("DETAILED"))) {
                print_detail = 1;
            }
            else
            {
                print_detail = 0;
            }
        }
        if (!strncmp("-Add ECC", line, strlen("-Add ECC"))) {
            sscanf(line, "-Add ECC %[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("true", temp_var, strlen("true"))) {
                add_ecc_b_ = true;
            }
            else
            {
                add_ecc_b_ = false;
            }
        }

        if (!strncmp("-CLDriver vertical", line, strlen("-CLDriver vertical"))) {
            sscanf(line, "-CLDriver vertical %[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("true", temp_var, strlen("true"))) {
                cl_vertical = true;
            }
            else
            {
                cl_vertical = false;
            }
        }

        if (!strncmp("-Array Power Gating", line, strlen("-Array Power Gating"))) {
            sscanf(line, "-Array Power Gating %[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("true", temp_var, strlen("true"))) {
                array_power_gated = true;
            }
            else
            {
                array_power_gated = false;
            }
        }

        if (!strncmp("-Bitline floating", line, strlen("-Bitline floating"))) {
            sscanf(line, "-Bitline floating %[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("true", temp_var, strlen("true"))) {
                bitline_floating = true;
            }
            else
            {
                bitline_floating = false;
            }
        }

        if (!strncmp("-WL Power Gating", line, strlen("-WL Power Gating"))) {
            sscanf(line, "-WL Power Gating %[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("true", temp_var, strlen("true"))) {
                wl_power_gated = true;
            }
            else
            {
                wl_power_gated = false;
            }
        }

        if (!strncmp("-CL Power Gating", line, strlen("-CL Power Gating"))) {
            sscanf(line, "-CL Power Gating %[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("true", temp_var, strlen("true"))) {
                cl_power_gated = true;
            }
            else
            {
                cl_power_gated = false;
            }
        }

        if (!strncmp("-Interconnect Power Gating", line, strlen("-Interconnect Power Gating"))) {
            sscanf(line, "-Interconnect Power Gating %[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("true", temp_var, strlen("true"))) {
                interconect_power_gated = true;
            }
            else
            {
                interconect_power_gated = false;
            }
        }

        if (!strncmp("-Power Gating Performance Loss", line, strlen("-Power Gating Performance Loss"))) {
            sscanf(line, "-Power Gating Performance Loss %lf", &(perfloss));
            continue;
        }

        if (!strncmp("-Print input parameters", line, strlen("-Print input parameters"))) {
            sscanf(line, "-Print input %[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("true", temp_var, strlen("true"))) {
                print_input_args = true;
            }
            else
            {
                print_input_args = false;
            }
        }

        if (!strncmp("-Force cache config", line, strlen("-Force cache config"))) {
            sscanf(line, "-Force cache %[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("true", temp_var, strlen("true"))) {
                force_cache_config = true;
            }
            else
            {
                force_cache_config = false;
            }
        }

        if (!strncmp("-Ndbl", line, strlen("-Ndbl"))) {
            sscanf(line, "-Ndbl %d\n", &(ndbl));
            continue;
        }
        if (!strncmp("-Ndwl", line, strlen("-Ndwl"))) {
            sscanf(line, "-Ndwl %d\n", &(ndwl));
            continue;
        }
        if (!strncmp("-Nspd", line, strlen("-Nspd"))) {
            sscanf(line, "-Nspd %lf\n", &(nspd));
            continue;
        }
        if (!strncmp("-Ndsam1", line, strlen("-Ndsam1"))) {
            sscanf(line, "-Ndsam1 %d\n", &(ndsam1));
            continue;
        }
        if (!strncmp("-Ndsam2", line, strlen("-Ndsam2"))) {
            sscanf(line, "-Ndsam2 %d\n", &(ndsam2));
            continue;
        }
        if (!strncmp("-Ndcm", line, strlen("-Ndcm"))) {
            sscanf(line, "-Ndcm %d\n", &(ndcm));
            continue;
        }

        // Parameters related to off-chip interconnect

        if (!strncmp("-dram type", line, strlen("-dram type"))) {
            sscanf(line, "-dram type%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("DDR3", temp_var, strlen("DDR3"))) {
                io_type = DDR3;
            }
            else if (!strncmp("DDR4", temp_var, strlen("DDR4")))
            {
                io_type = DDR4;
            }
            else if (!strncmp("LPDDR2", temp_var, strlen("LPDDR2")))
            {
                io_type = LPDDR2;
            }
            else if (!strncmp("WideIO", temp_var, strlen("WideIO")))
            {
                io_type = WideIO;
            }
            else if (!strncmp("Low_Swing_Diff", temp_var, strlen("Low_Swing_Diff")))
            {
                io_type = Low_Swing_Diff;
            }
            else if (!strncmp("Serial", temp_var, strlen("Serial")))
            {
                io_type = Serial;
            }
            else
            {
                cout << "Invalid Input for dram type!" << endl;
                exit(1);
            }
            // sscanf(line, "-io_type \"%c\"\n", &(io_type));
        }
        if (!strncmp("-io state", line, strlen("-io state"))) {
            sscanf(line, "-io state%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("READ", temp_var, strlen("READ"))) {
                iostate = READ;
            }
            else if (!strncmp("WRITE", temp_var, strlen("WRITE")))
            {
                iostate = WRITE;
            }
            else if (!strncmp("IDLE", temp_var, strlen("IDLE")))
            {
                iostate = IDLE;
            }
            else if (!strncmp("SLEEP", temp_var, strlen("SLEEP")))
            {
                iostate = SLEEP;
            }
            else
            {
                cout << "Invalid Input for io state!" << endl;
                exit(1);
            }
            // sscanf(line, "-iostate \"%c\"\n", &(iostate));
        }
        if (!strncmp("-addr_timing", line, strlen("-addr_timing"))) {
            sscanf(line, "-addr_timing %lf", &(addr_timing));
        }
        if (!strncmp("-dram ecc", line, strlen("-dram ecc"))) {
            sscanf(line, "-dram ecc%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("NO_ECC", temp_var, strlen("NO_ECC"))) {
                dram_ecc = NO_ECC;
            }
            else if (!strncmp("SECDED", temp_var, strlen("SECDED")))
            {
                dram_ecc = SECDED;
            }
            else if (!strncmp("CHIP_KILL", temp_var, strlen("CHIP_KILL")))
            {
                dram_ecc = CHIP_KILL;
            }
            else
            {
                cout << "Invalid Input for dram ecc!" << endl;
                exit(1);
            }
            // sscanf(line, "-dram_ecc \"%c\"\n", &(dram_ecc));
        }
        if (!strncmp("-dram dimm", line, strlen("-dram dimm"))) {
            sscanf(line, "-dram dimm%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("UDIMM", temp_var, strlen("UDIMM"))) {
                dram_dimm = UDIMM;
            }
            else if (!strncmp("RDIMM", temp_var, strlen("RDIMM")))
            {
                dram_dimm = RDIMM;
            }
            else if (!strncmp("LRDIMM", temp_var, strlen("LRDIMM")))
            {
                dram_dimm = LRDIMM;
            }
            else
            {
                cout << "Invalid Input for dram dimm!" << endl;
                exit(1);
            }
            // sscanf(line, "-dram_ecc \"%c\"\n", &(dram_ecc));
        }

        if (!strncmp("-bus_bw", line, strlen("-bus_bw"))) {
            sscanf(line, "-bus_bw %lf", &(bus_bw));
        }
        if (!strncmp("-duty_cycle", line, strlen("-duty_cycle"))) {
            sscanf(line, "-duty_cycle %lf", &(duty_cycle));
        }
        if (!strncmp("-mem_density", line, strlen("-mem_density"))) {
            sscanf(line, "-mem_density %lf", &(mem_density));
        }
        if (!strncmp("-activity_dq", line, strlen("-activity_dq"))) {
            sscanf(line, "-activity_dq %lf", &activity_dq);
        }
        if (!strncmp("-activity_ca", line, strlen("-activity_ca"))) {
            sscanf(line, "-activity_ca %lf", &activity_ca);
        }
        if (!strncmp("-bus_freq", line, strlen("-bus_freq"))) {
            sscanf(line, "-bus_freq %lf", &bus_freq);
        }
        if (!strncmp("-num_dq", line, strlen("-num_dq"))) {
            sscanf(line, "-num_dq %d", &num_dq);
        }
        if (!strncmp("-num_dqs", line, strlen("-num_dqs"))) {
            sscanf(line, "-num_dqs %d", &num_dqs);
        }
        if (!strncmp("-num_ca", line, strlen("-num_ca"))) {
            sscanf(line, "-num_ca %d", &num_ca);
        }
        if (!strncmp("-num_clk", line, strlen("-num_clk"))) {
            sscanf(line, "-num_clk %d", &num_clk);
            if (num_clk <= 0) {
                cout << "num_clk should be greater than zero!\n";
                exit(1);
            }
        }
        if (!strncmp("-num_mem_dq", line, strlen("-num_mem_dq"))) {
            sscanf(line, "-num_mem_dq %d", &num_mem_dq);
        }
        if (!strncmp("-mem_data_width", line, strlen("-mem_data_width"))) {
            sscanf(line, "-mem_data_width %d", &mem_data_width);
        }

        // added just for memcad

        if (!strncmp("-num_bobs", line, strlen("-num_bobs"))) {
            sscanf(line, "-num_bobs %d", &num_bobs);
        }
        if (!strncmp("-capacity", line, strlen("-capacity"))) {
            sscanf(line, "-capacity %d", &capacity);
        }
        if (!strncmp("-num_channels_per_bob", line, strlen("-num_channels_per_bob"))) {
            sscanf(line, "-num_channels_per_bob %d", &num_channels_per_bob);
        }
        if (!strncmp("-first metric", line, strlen("-first metric"))) {
            sscanf(line, "-first metric%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("Cost", temp_var, strlen("Cost"))) {
                first_metric = Cost;
            }
            else if (!strncmp("Energy", temp_var, strlen("Energy")))
            {
                first_metric = Energy;
            }
            else if (!strncmp("Bandwidth", temp_var, strlen("Bandwidth")))
            {
                first_metric = Bandwidth;
            }
            else
            {
                cout << "Invalid Input for first metric!" << endl;
                exit(1);
            }
        }
        if (!strncmp("-second metric", line, strlen("-second metric"))) {
            sscanf(line, "-second metric%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("Cost", temp_var, strlen("Cost"))) {
                second_metric = Cost;
            }
            else if (!strncmp("Energy", temp_var, strlen("Energy")))
            {
                second_metric = Energy;
            }
            else if (!strncmp("Bandwidth", temp_var, strlen("Bandwidth")))
            {
                second_metric = Bandwidth;
            }
            else
            {
                cout << "Invalid Input for second metric!" << endl;
                exit(1);
            }
        }
        if (!strncmp("-third metric", line, strlen("-third metric"))) {
            sscanf(line, "-third metric%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("Cost", temp_var, strlen("Cost"))) {
                third_metric = Cost;
            }
            else if (!strncmp("Energy", temp_var, strlen("Energy")))
            {
                third_metric = Energy;
            }
            else if (!strncmp("Bandwidth", temp_var, strlen("Bandwidth")))
            {
                third_metric = Bandwidth;
            }
            else
            {
                cout << "Invalid Input for third metric!" << endl;
                exit(1);
            }
        }
        if (!strncmp("-DIMM model", line, strlen("-DIMM model"))) {
            sscanf(line, "-DIMM model%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("JUST_UDIMM", temp_var, strlen("JUST_UDIMM"))) {
                dimm_model = JUST_UDIMM;
            }
            else if (!strncmp("JUST_RDIMM", temp_var, strlen("JUST_RDIMM")))
            {
                dimm_model = JUST_RDIMM;
            }
            else if (!strncmp("JUST_LRDIMM", temp_var, strlen("JUST_LRDIMM")))
            {
                dimm_model = JUST_LRDIMM;
            }
            else if (!strncmp("ALL", temp_var, strlen("ALL")))
            {
                dimm_model = ALL;
            }
            else
            {
                cout << "Invalid Input for DIMM model!" << endl;
                exit(1);
            }
        }
        if (!strncmp("-Low Power Permitted", line, strlen("-Low Power Permitted"))) {
            sscanf(line, "-Low Power Permitted%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("T", temp_var, strlen("T"))) {
                low_power_permitted = true;
            }
            else if (!strncmp("F", temp_var, strlen("F")))
            {
                low_power_permitted = false;
            }
            else
            {
                cout << "Invalid Input for Low Power Permitted!" << endl;
                exit(1);
            }
        }
        if (!strncmp("-load", line, strlen("-load"))) {
            sscanf(line, "-load %lf", &(load));
        }
        if (!strncmp("-row_buffer_hit_rate", line, strlen("-row_buffer_hit_rate"))) {
            sscanf(line, "-row_buffer_hit_rate %lf", &(row_buffer_hit_rate));
        }
        if (!strncmp("-rd_2_wr_ratio", line, strlen("-rd_2_wr_ratio"))) {
            sscanf(line, "-rd_2_wr_ratio %lf", &(rd_2_wr_ratio));
        }
        if (!strncmp("-same_bw_in_bob", line, strlen("-same_bw_in_bob"))) {
            sscanf(line, "-same_bw_in_bob%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("T", temp_var, strlen("T"))) {
                same_bw_in_bob = true;
            }
            else if (!strncmp("F", temp_var, strlen("F")))
            {
                same_bw_in_bob = false;
            }
            else
            {
                cout << "Invalid Input for same_bw_in_bob!" << endl;
                exit(1);
            }
        }
        if (!strncmp("-mirror_in_bob", line, strlen("-mirror_in_bob"))) {
            sscanf(line, "-mirror_in_bob%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("T", temp_var, strlen("T"))) {
                mirror_in_bob = true;
            }
            else if (!strncmp("F", temp_var, strlen("F")))
            {
                mirror_in_bob = false;
            }
            else
            {
                cout << "Invalid Input for mirror_in_bob!" << endl;
                exit(1);
            }
        }
        if (!strncmp("-total_power", line, strlen("-total_power"))) {
            sscanf(line, "-total_power%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("T", temp_var, strlen("T"))) {
                total_power = true;
            }
            else if (!strncmp("F", temp_var, strlen("F")))
            {
                total_power = false;
            }
            else
            {
                cout << "Invalid Input for total_power!" << endl;
                exit(1);
            }
        }
        if (!strncmp("-verbose", line, strlen("-verbose"))) {
            sscanf(line, "-verbose%[^\"]\"%[^\"]\"", jk, temp_var);
            if (!strncmp("T", temp_var, strlen("T"))) {
                verbose = true;
            }
            else if (!strncmp("F", temp_var, strlen("F")))
            {
                verbose = false;
            }
            else
            {
                cout << "Invalid Input for same_bw_in_bob!" << endl;
                exit(1);
            }
        }
    }
    rpters_in_htree = true;
    fclose(fp);
}

bool InputParameter::error_checking()
{
    int  A;
    bool seq_access = false;
    fast_access     = true;

    switch (access_mode)
    {
    case 0:
        seq_access  = false;
        fast_access = false;
        break;
    case 1:
        seq_access  = true;
        fast_access = false;
        break;
    case 2:
        seq_access  = false;
        fast_access = true;
        break;
    }

    if (is_main_mem) {
        if (ic_proj_type == 0 && !g_ip->is_3d_mem) {
            cerr << "DRAM model supports only conservative interconnect projection!\n\n";
            return false;
        }
    }

    uint32_t B = line_sz;

    if (B < 1) {
        cerr << "Block size must >= 1" << endl;
        return false;
    }

    else if (B * 8 < out_w)
    {
        cerr << "Block size must be at least " << out_w / 8 << endl;
        return false;
    }

    if (F_sz_um <= 0) {
        cerr << "Feature size must be > 0" << endl;
        return false;
    }
    else if (F_sz_um > 0.091)
    {
        cerr << "Feature size must be <= 90 nm" << endl;
        return false;
    }

    uint32_t RWP  = num_rw_ports;
    uint32_t ERP  = num_rd_ports;
    uint32_t EWP  = num_wr_ports;
    uint32_t NSER = num_se_rd_ports;
    uint32_t SCHP = num_search_ports;

    // TODO: revisit this. This is an important feature.  thought this should be used
    //  // If multiple banks and multiple ports are specified, then if number of ports is less than or equal to
    //  // the number of banks, we assume that the multiple ports are implemented via the multiple banks.
    //  // In such a case we assume that each bank has 1 RWP port.
    //  if ((RWP + ERP + EWP) <= nbanks && nbanks>1)
    //  {
    //    RWP  = 1;
    //    ERP  = 0;
    //    EWP  = 0;
    //    NSER = 0;
    //  }
    //  else if ((RWP < 0) || (EWP < 0) || (ERP < 0))
    //  {
    //    cerr << "Ports must >=0" << endl;
    //    return false;
    //  }
    //  else if (RWP > 2)
    //  {
    //    cerr << "Maximum of 2 read/write ports" << endl;
    //    return false;
    //  }
    //  else if ((RWP+ERP+EWP) < 1)
    // Changed to new implementation:
    // The number of ports specified at input is per bank
    if ((RWP + ERP + EWP) < 1) {
        cerr << "Must have at least one port" << endl;
        return false;
    }

    if (is_pow2(nbanks) == false) {
        cerr << "Number of subbanks should be greater than or equal to 1 and should be a power of 2" << endl;
        return false;
    }

    int C = cache_sz / nbanks;
    if (C < 64 && !g_ip->is_3d_mem) {
        cerr << "Cache size must >=64" << endl;
        return false;
    }

    // TODO: revisit this
    //   if (pure_ram==true && assoc!=1)
    //    {
    //  	  cerr << "Pure RAM must have assoc as 1" << endl;
    //  	  return false;
    //    }

    // fully assoc and cam check
    if (is_cache && assoc == 0)
        fully_assoc = true;
    else
        fully_assoc = false;

    if (pure_cam == true && assoc != 0) {
        cerr << "Pure CAM must have associativity as 0" << endl;
        return false;
    }

    if (assoc == 0 && (pure_cam == false && is_cache == false)) {
        cerr << "Only CAM or Fully associative cache can have associativity as 0" << endl;
        return false;
    }

    if ((fully_assoc == true || pure_cam == true)
        && (data_arr_ram_cell_tech_type != tag_arr_ram_cell_tech_type || data_arr_peri_global_tech_type != tag_arr_peri_global_tech_type))
    {
        cerr << "CAM and fully associative cache must have same device type for both data and tag array" << endl;
        return false;
    }

    if ((fully_assoc == true || pure_cam == true) && (data_arr_ram_cell_tech_type == lp_dram || data_arr_ram_cell_tech_type == comm_dram)) {
        cerr << "DRAM based CAM and fully associative cache are not supported" << endl;
        return false;
    }

    if ((fully_assoc == true || pure_cam == true) && (is_main_mem == true)) {
        cerr << "CAM and fully associative cache cannot be as main memory" << endl;
        return false;
    }

    if ((fully_assoc || pure_cam) && SCHP < 1) {
        cerr << "CAM and fully associative must have at least 1 search port" << endl;
        return false;
    }

    if (RWP == 0 && ERP == 0 && SCHP > 0 && ((fully_assoc || pure_cam))) {
        ERP = SCHP;
    }

    //    if ((!(fully_assoc || pure_cam)) && SCHP>=1)
    //    {
    //	  cerr << "None CAM and fully associative cannot have search ports" << endl;
    //	  return false;
    //    }

    if (assoc == 0) {
        A = C / B;
        // fully_assoc = true;
    }
    else
    {
        if (assoc == 1) {
            A = 1;
            // fully_assoc = false;
        }
        else
        {
            // fully_assoc = false;
            A = assoc;
            if (is_pow2(A) == false) {
                cerr << "Associativity must be a power of 2" << endl;
                return false;
            }
        }
    }

    if (C / (B * A) <= 1 && assoc != 0 && !g_ip->is_3d_mem) {
        cerr << "Number of sets is too small: " << endl;
        cerr << " Need to either increase cache size, or decrease associativity or block size" << endl;
        cerr << " (or use fully associative cache)" << endl;
        return false;
    }

    block_sz = B;

    /*dt: testing sequential access mode*/
    if (seq_access) {
        tag_assoc  = A;
        data_assoc = 1;
        is_seq_acc = true;
    }
    else
    {
        tag_assoc  = A;
        data_assoc = A;
        is_seq_acc = false;
    }

    if (assoc == 0) {
        data_assoc = 1;
    }
    num_rw_ports                                     = RWP;
    num_rd_ports                                     = ERP;
    num_wr_ports                                     = EWP;
    num_se_rd_ports                                  = NSER;
    if (!(fully_assoc || pure_cam)) num_search_ports = 0;
    nsets                                            = C / (B * A);

    if (temp < 300 || temp > 400 || temp % 10 != 0) {
        cerr << temp << " Temperature must be between 300 and 400 Kelvin and multiple of 10." << endl;
        return false;
    }

    if (nsets < 1 && !g_ip->is_3d_mem) {
        cerr << "Less than one set..." << endl;
        return false;
    }

    power_gating = (array_power_gated || bitline_floating || wl_power_gated || cl_power_gated || interconect_power_gated) ? true : false;

    return true;
}

void InputParameter::display_ip()
{
    cout << "Cache size                    : " << cache_sz << endl;
    cout << "Block size                    : " << line_sz << endl;
    cout << "Associativity                 : " << assoc << endl;
    cout << "Read only ports               : " << num_rd_ports << endl;
    cout << "Write only ports              : " << num_wr_ports << endl;
    cout << "Read write ports              : " << num_rw_ports << endl;
    cout << "Single ended read ports       : " << num_se_rd_ports << endl;
    if (fully_assoc || pure_cam) {
        cout << "Search ports                  : " << num_search_ports << endl;
    }
    cout << "Cache banks (UCA)             : " << nbanks << endl;
    cout << "Technology                    : " << F_sz_um << endl;
    cout << "Temperature                   : " << temp << endl;
    cout << "Tag size                      : " << tag_w << endl;
    if (is_cache) {
        cout << "array type                    : "
             << "Cache" << endl;
    }
    if (pure_ram) {
        cout << "array type                    : "
             << "Scratch RAM" << endl;
    }
    if (pure_cam) {
        cout << "array type                    : "
             << "CAM" << endl;
    }
    cout << "Model as memory               : " << is_main_mem << endl;
    cout << "Model as 3D memory       	 : " << is_3d_mem << endl;
    cout << "Access mode                   : " << access_mode << endl;
    cout << "Data array cell type          : " << data_arr_ram_cell_tech_type << endl;
    cout << "Data array peripheral type    : " << data_arr_peri_global_tech_type << endl;
    cout << "Tag array cell type           : " << tag_arr_ram_cell_tech_type << endl;
    cout << "Tag array peripheral type     : " << tag_arr_peri_global_tech_type << endl;
    cout << "Optimization target           : " << ed << endl;
    cout << "Design objective (UCA wt)     : " << delay_wt << " " << dynamic_power_wt << " " << leakage_power_wt << " " << cycle_time_wt << " " << area_wt
         << endl;
    cout << "Design objective (UCA dev)    : " << delay_dev << " " << dynamic_power_dev << " " << leakage_power_dev << " " << cycle_time_dev << " " << area_dev
         << endl;
    if (nuca) {
        cout << "Cores                         : " << cores << endl;

        cout << "Design objective (NUCA wt)    : " << delay_wt_nuca << " " << dynamic_power_wt_nuca << " " << leakage_power_wt_nuca << " " << cycle_time_wt_nuca
             << " " << area_wt_nuca << endl;
        cout << "Design objective (NUCA dev)   : " << delay_dev_nuca << " " << dynamic_power_dev_nuca << " " << leakage_power_dev_nuca << " "
             << cycle_time_dev_nuca << " " << area_dev_nuca << endl;
    }
    cout << "Cache model                   : " << nuca << endl;
    cout << "Nuca bank                     : " << nuca_bank_count << endl;
    cout << "Wire inside mat               : " << wire_is_mat_type << endl;
    cout << "Wire outside mat              : " << wire_os_mat_type << endl;
    cout << "Interconnect projection       : " << ic_proj_type << endl;
    cout << "Wire signaling               : " << force_wiretype << endl;
    cout << "Print level                   : " << print_detail << endl;
    cout << "ECC overhead                  : " << add_ecc_b_ << endl;
    cout << "Page size                     : " << page_sz_bits << endl;
    cout << "Burst length                  : " << burst_len << endl;
    cout << "Internal prefetch width       : " << int_prefetch_w << endl;
    cout << "Force cache config            : " << g_ip->force_cache_config << endl;
    if (g_ip->force_cache_config) {
        cout << "Ndwl                          : " << g_ip->ndwl << endl;
        cout << "Ndbl                          : " << g_ip->ndbl << endl;
        cout << "Nspd                          : " << g_ip->nspd << endl;
        cout << "Ndcm                          : " << g_ip->ndcm << endl;
        cout << "Ndsam1                        : " << g_ip->ndsam1 << endl;
        cout << "Ndsam2                        : " << g_ip->ndsam2 << endl;
    }
    cout << "Subarray Driver direction       : " << g_ip->cl_vertical << endl;

    // CACTI-I/O
    cout << "iostate                       : ";
    switch (iostate)
    {
    case (READ): cout << "READ" << endl; break;
    case (WRITE): cout << "WRITE" << endl; break;
    case (IDLE): cout << "IDLE" << endl; break;
    case (SLEEP): cout << "SLEEP" << endl; break;
    default: assert(false);
    }
    cout << "dram_ecc                      : ";
    switch (dram_ecc)
    {
    case (NO_ECC): cout << "NO_ECC" << endl; break;
    case (SECDED): cout << "SECDED" << endl; break;
    case (CHIP_KILL): cout << "CHIP_KILL" << endl; break;
    default: assert(false);
    }
    cout << "io_type                     : ";
    switch (io_type)
    {
    case (DDR3): cout << "DDR3" << endl; break;
    case (DDR4): cout << "DDR4" << endl; break;
    case (LPDDR2): cout << "LPDDR2" << endl; break;
    case (WideIO): cout << "WideIO" << endl; break;
    case (Low_Swing_Diff): cout << "Low_Swing_Diff" << endl; break;
    default: assert(false);
    }
    cout << "dram_dimm                      : ";
    switch (dram_dimm)
    {
    case (UDIMM): cout << "UDIMM" << endl; break;
    case (RDIMM): cout << "RDIMM" << endl; break;
    case (LRDIMM): cout << "LRDIMM" << endl; break;
    default: assert(false);
    }
}
