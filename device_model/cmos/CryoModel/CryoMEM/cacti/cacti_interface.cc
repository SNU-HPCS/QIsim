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

#include <iostream>
#include <string>

#include "cacti_interface.h"
#include "global_cacti_input.h"
#include "input_parameter.h"
#include "technology_parameter.h"
#include "wire.h"
#include "io.h"
#include "nuca.h"

#ifndef CACTI_REPRODUCE
#include "tsv.h"
#include "io_tech_param.h"
#include "extio.h"
#include "mem_cad_parameters.h"
#include "mem_cad.h"
#include "enum/tsv_type.h"
#else
#include <fstream>
#include <memory>

#include "mem_array.h"
#include "calculate_time.h"
#include "dynamic_parameter.h"
#endif

using namespace std;

void reconfigure(InputParameter *local_interface, uca_org_t *fin_res)
{
    // Copy the InputParameter to global interface (g_ip) and do error checking.
    g_ip = local_interface;
    g_ip->error_checking();

    // Initialize technology parameters
    init_tech_params(g_ip->F_sz_um, false);

    Wire winit;  // Do not delete this line. It initializes wires.

    // This corresponds to solve() in the initialization process.
    update(fin_res);
}

uca_org_t cacti_interface()
{
    // cout<<"TSV_proj_type: " << g_ip->TSV_proj_type << endl;
    uca_org_t fin_res;
    // uca_org_t result;
    fin_res.valid = false;

    // Too many uninitialized fields in InputParameter!
    // Zero-initialize the memory before constructing g_ip.
    // (Temporary workaround; we need to initialize them properly)
    // g_ip = new InputParameter();
    void *raw_g_ip = operator new(sizeof(InputParameter));
    memset(raw_g_ip, 0, sizeof(InputParameter));
    g_ip = new (raw_g_ip) InputParameter;

    g_ip->parse_cfg(GlobalCactiInput::get().config_file());
    if (!g_ip->error_checking()) exit(0);
    // if (g_ip->print_input_args)
    g_ip->display_ip();

    init_tech_params(g_ip->F_sz_um, false);
    Wire winit;  // Do not delete this line. It initializes wires.
                 //  cout << winit.wire_res(256*8*64e-9) << endl;
                 //  exit(0);
    if (GlobalCactiInput::get().has_wire_config())
#ifndef CACTI_REPRODUCE
        winit.save();
#else
        winit.load();
#endif

#ifndef CACTI_REPRODUCE
    // CACTI3DD
    // --- These two parameters are supposed for two different TSV technologies within one DRAM fabrication, currently assume one individual TSV geometry size
    // for cost efficiency
    g_ip->tsv_is_subarray_type = g_ip->TSV_proj_type;
    g_ip->tsv_os_bank_type     = g_ip->TSV_proj_type;
    TSV tsv_test(Coarse);  // ********* double len_ /* in um*/, 	double diam_, 	double TSV_pitch_,
    if (g_ip->print_detail_debug) {
        tsv_test.print_TSV();
    }

    //  For HighRadix Only
    //  ////  Wire wirea(g_ip->wt, 1000);
    //  ////  wirea.print_wire();
    //  ////  cout << "Wire Area " << wirea.area.get_area() << " sq. u" << endl;
    //  //  winit.print_wire();
    //  //
    //    HighRadix *hr;
    //      hr = new HighRadix();
    //      hr->compute_power();
    //      hr->print_router();
    //    exit(0);
    //
    //    double sub_switch_sz = 2;
    //    double rows = 32;
    //    for (int i=0; i<6; i++) {
    //      sub_switch_sz = pow(2, i);
    //      rows = 64/sub_switch_sz;
    //      hr = new HighRadix(sub_switch_sz, rows, .8/* freq */, 64, 2, 64, 0.7);
    //      hr->compute_power();
    //      hr->print_router();
    //      delete hr;
    //    }
    //  //  HighRadix yarc;
    //  //  yarc.compute_power();
    //  //  yarc.print_router();
    //    winit.print_wire();
    //    exit(0);
    //  For HighRadix Only End

    if (g_ip->nuca == 1) {
        Nuca n(&g_tp.peri_global);
        n.sim_nuca();
    }

    // g_ip->display_ip();

    IOTechParam iot(g_ip, g_ip->io_type, g_ip->num_mem_dq, g_ip->mem_data_width, g_ip->num_dq, g_ip->dram_dimm, 1, g_ip->bus_freq);
    Extio       testextio(&iot);
    testextio.extio_area();
    testextio.extio_eye();
    testextio.extio_power_dynamic();
    testextio.extio_power_phy();
    testextio.extio_power_term();

    /*
    int freq[][4]={{400,533,667,800},{800,933,1066,1200}};

    Mem_IO_type types[2]={DDR3,DDR4};

    int max_load[3]={3,3,8};

    for(int j=0;j<1;j++)
    {
        for(int connection=0;connection<3;connection++)
        {
            for(int frq=3;frq<4;frq++)
            {
                for(int load=1;load<=max_load[connection];load++)
                {
                    IOTechParam iot(g_ip, types[j], load, 8, 72, connection, load, freq[j][frq]);
                    Extio testextio(&iot);
                   // testextio.extio_area();
                   // testextio.extio_eye();
                    testextio.extio_power_dynamic();
                    testextio.extio_power_phy();
                    testextio.extio_power_term();

                }
                cout << endl;
            }
            cout << endl;
        }
         cout << endl;
    }
    */

    /// double total_io_p, total_phy_p, total_io_area, total_vmargin, total_tmargin;
    // testextio.extio_power_area_timing(total_io_p, total_phy_p, total_io_area, total_vmargin, total_tmargin);

    solve(&fin_res);
#else
    if (!GlobalCactiInput::get().has_dyn_param_prefix()) exit(0);
    {
        ifstream ifs(GlobalCactiInput::get().dyn_param_prefix() + "dyn_param.tag.txt");
        if(ifs){
            boost::archive::text_iarchive ia(ifs);
            auto dp_tag = make_unique<DynamicParameter>();

            ia >> *dp_tag;
            fin_res.tag_array2 = new mem_array;
            calculate_time_internal(move(dp_tag), fin_res.tag_array2);
        }
    }
    {
        ifstream ifs(GlobalCactiInput::get().dyn_param_prefix() + "dyn_param.data.txt");
        if(ifs){
            boost::archive::text_iarchive ia(ifs);
            auto dp_data = make_unique<DynamicParameter>();

            ia >> *dp_data;

            if (g_ip->print_detail_debug) {
                dp_data->print_args();
            }

            fin_res.data_array2 = new mem_array;
            calculate_time_internal(move(dp_data), fin_res.data_array2);
        }
    }

    fin_res.find_characteristics();
#endif

    output_UCA(&fin_res);
    output_data_csv(fin_res, GlobalCactiInput::get().config_file() + ".out");

#ifndef CACTI_REPRODUCE
    // Memcad Optimization
    MemCadParameters memcad_params(g_ip);
    solve_memcad(&memcad_params);
#endif

    delete (g_ip);
    return fin_res;
}

// McPAT's plain interface, please keep !!!
uca_org_t cacti_interface(InputParameter *const local_interface)
{
    //  g_ip = new InputParameter();
    // g_ip->add_ecc_b_ = true;

    uca_org_t fin_res;
    fin_res.valid = false;

    g_ip = local_interface;

    //  g_ip->data_arr_ram_cell_tech_type    = data_arr_ram_cell_tech_flavor_in;
    //  g_ip->data_arr_peri_global_tech_type = data_arr_peri_global_tech_flavor_in;
    //  g_ip->tag_arr_ram_cell_tech_type     = tag_arr_ram_cell_tech_flavor_in;
    //  g_ip->tag_arr_peri_global_tech_type  = tag_arr_peri_global_tech_flavor_in;
    //
    //  g_ip->ic_proj_type     = interconnect_projection_type_in;
    //  g_ip->wire_is_mat_type = wire_inside_mat_type_in;
    //  g_ip->wire_os_mat_type = wire_outside_mat_type_in;
    //  g_ip->burst_len        = BURST_LENGTH_in;
    //  g_ip->int_prefetch_w   = INTERNAL_PREFETCH_WIDTH_in;
    //  g_ip->page_sz_bits     = PAGE_SIZE_BITS_in;
    //
    //  g_ip->cache_sz            = cache_size;
    //  g_ip->line_sz             = line_size;
    //  g_ip->assoc               = associativity;
    //  g_ip->nbanks              = banks;
    //  g_ip->out_w               = output_width;
    //  g_ip->specific_tag        = specific_tag;
    //  if (tag_width == 0) {
    //    g_ip->tag_w = 42;
    //  }
    //  else {
    //    g_ip->tag_w               = tag_width;
    //  }
    //
    //  g_ip->access_mode         = access_mode;
    //  g_ip->delay_wt = obj_func_delay;
    //  g_ip->dynamic_power_wt = obj_func_dynamic_power;
    //  g_ip->leakage_power_wt = obj_func_leakage_power;
    //  g_ip->area_wt = obj_func_area;
    //  g_ip->cycle_time_wt    = obj_func_cycle_time;
    //  g_ip->delay_dev = dev_func_delay;
    //  g_ip->dynamic_power_dev = dev_func_dynamic_power;
    //  g_ip->leakage_power_dev = dev_func_leakage_power;
    //  g_ip->area_dev = dev_func_area;
    //  g_ip->cycle_time_dev    = dev_func_cycle_time;
    //  g_ip->temp = temp;
    //
    //  g_ip->F_sz_nm         = tech_node;
    //  g_ip->F_sz_um         = tech_node / 1000;
    //  g_ip->is_main_mem     = (main_mem != 0) ? true : false;
    //  g_ip->is_cache        = (cache ==1) ? true : false;
    //  g_ip->pure_ram        = (cache ==0) ? true : false;
    //  g_ip->pure_cam        = (cache ==2) ? true : false;
    //  g_ip->rpters_in_htree = (REPEATERS_IN_HTREE_SEGMENTS_in != 0) ? true : false;
    //  g_ip->ver_htree_wires_over_array = VERTICAL_HTREE_WIRES_OVER_THE_ARRAY_in;
    //  g_ip->broadcast_addr_din_over_ver_htrees = BROADCAST_ADDR_DATAIN_OVER_VERTICAL_HTREES_in;
    //
    //  g_ip->num_rw_ports    = rw_ports;
    //  g_ip->num_rd_ports    = excl_read_ports;
    //  g_ip->num_wr_ports    = excl_write_ports;
    //  g_ip->num_se_rd_ports = single_ended_read_ports;
    //  g_ip->num_search_ports = search_ports;
    //
    //  g_ip->print_detail = 1;
    //    g_ip->nuca = 0;
    //    g_ip->is_cache=true;
    //
    //  if (force_wiretype == 0)
    //  {
    //	  g_ip->wt = Global;
    //      g_ip->force_wiretype = false;
    //  }
    //  else
    //  {   g_ip->force_wiretype = true;
    //	  if (wiretype==10) {
    //		  g_ip->wt = Global_10;
    //	        }
    //	  if (wiretype==20) {
    //		  g_ip->wt = Global_20;
    //	        }
    //	  if (wiretype==30) {
    //		  g_ip->wt = Global_30;
    //	        }
    //	  if (wiretype==5) {
    //	      g_ip->wt = Global_5;
    //	        }
    //	  if (wiretype==0) {
    //		  g_ip->wt = Low_swing;
    //	  }
    //  }
    //  //g_ip->wt = Global_5;
    //  if (force_config == 0)
    //    {
    //  	  g_ip->force_cache_config = false;
    //    }
    //    else
    //    {
    //    	g_ip->force_cache_config = true;
    //    	g_ip->ndbl=ndbl;
    //    	g_ip->ndwl=ndwl;
    //    	g_ip->nspd=nspd;
    //    	g_ip->ndcm=ndcm;
    //    	g_ip->ndsam1=ndsam1;
    //    	g_ip->ndsam2=ndsam2;
    //
    //
    //    }
    //
    //  if (ecc==0){
    //	  g_ip->add_ecc_b_=false;
    //  }
    //  else
    //  {
    //	  g_ip->add_ecc_b_=true;
    //  }

    g_ip->error_checking();

    init_tech_params(g_ip->F_sz_um, false);
    Wire winit;  // Do not delete this line. It initializes wires.

    solve(&fin_res);

    //  g_ip->display_ip();
    //  output_UCA(&fin_res);
    //  output_data_csv(fin_res);

    // delete (g_ip);

    return fin_res;
}

// McPAT's plain interface, please keep !!!
uca_org_t init_interface(InputParameter *const local_interface)
{
    // g_ip = new InputParameter();
    // g_ip->add_ecc_b_ = true;

    uca_org_t fin_res;
    fin_res.valid = false;

    g_ip = local_interface;

    //  g_ip->data_arr_ram_cell_tech_type    = data_arr_ram_cell_tech_flavor_in;
    //  g_ip->data_arr_peri_global_tech_type = data_arr_peri_global_tech_flavor_in;
    //  g_ip->tag_arr_ram_cell_tech_type     = tag_arr_ram_cell_tech_flavor_in;
    //  g_ip->tag_arr_peri_global_tech_type  = tag_arr_peri_global_tech_flavor_in;
    //
    //  g_ip->ic_proj_type     = interconnect_projection_type_in;
    //  g_ip->wire_is_mat_type = wire_inside_mat_type_in;
    //  g_ip->wire_os_mat_type = wire_outside_mat_type_in;
    //  g_ip->burst_len        = BURST_LENGTH_in;
    //  g_ip->int_prefetch_w   = INTERNAL_PREFETCH_WIDTH_in;
    //  g_ip->page_sz_bits     = PAGE_SIZE_BITS_in;
    //
    //  g_ip->cache_sz            = cache_size;
    //  g_ip->line_sz             = line_size;
    //  g_ip->assoc               = associativity;
    //  g_ip->nbanks              = banks;
    //  g_ip->out_w               = output_width;
    //  g_ip->specific_tag        = specific_tag;
    //  if (tag_width == 0) {
    //    g_ip->tag_w = 42;
    //  }
    //  else {
    //    g_ip->tag_w               = tag_width;
    //  }
    //
    //  g_ip->access_mode         = access_mode;
    //  g_ip->delay_wt = obj_func_delay;
    //  g_ip->dynamic_power_wt = obj_func_dynamic_power;
    //  g_ip->leakage_power_wt = obj_func_leakage_power;
    //  g_ip->area_wt = obj_func_area;
    //  g_ip->cycle_time_wt    = obj_func_cycle_time;
    //  g_ip->delay_dev = dev_func_delay;
    //  g_ip->dynamic_power_dev = dev_func_dynamic_power;
    //  g_ip->leakage_power_dev = dev_func_leakage_power;
    //  g_ip->area_dev = dev_func_area;
    //  g_ip->cycle_time_dev    = dev_func_cycle_time;
    //  g_ip->temp = temp;
    //
    //  g_ip->F_sz_nm         = tech_node;
    //  g_ip->F_sz_um         = tech_node / 1000;
    //  g_ip->is_main_mem     = (main_mem != 0) ? true : false;
    //  g_ip->is_cache        = (cache ==1) ? true : false;
    //  g_ip->pure_ram        = (cache ==0) ? true : false;
    //  g_ip->pure_cam        = (cache ==2) ? true : false;
    //  g_ip->rpters_in_htree = (REPEATERS_IN_HTREE_SEGMENTS_in != 0) ? true : false;
    //  g_ip->ver_htree_wires_over_array = VERTICAL_HTREE_WIRES_OVER_THE_ARRAY_in;
    //  g_ip->broadcast_addr_din_over_ver_htrees = BROADCAST_ADDR_DATAIN_OVER_VERTICAL_HTREES_in;
    //
    //  g_ip->num_rw_ports    = rw_ports;
    //  g_ip->num_rd_ports    = excl_read_ports;
    //  g_ip->num_wr_ports    = excl_write_ports;
    //  g_ip->num_se_rd_ports = single_ended_read_ports;
    //  g_ip->num_search_ports = search_ports;
    //
    //  g_ip->print_detail = 1;
    //  g_ip->nuca = 0;
    //
    //  if (force_wiretype == 0)
    //  {
    //	  g_ip->wt = Global;
    //      g_ip->force_wiretype = false;
    //  }
    //  else
    //  {   g_ip->force_wiretype = true;
    //	  if (wiretype==10) {
    //		  g_ip->wt = Global_10;
    //	        }
    //	  if (wiretype==20) {
    //		  g_ip->wt = Global_20;
    //	        }
    //	  if (wiretype==30) {
    //		  g_ip->wt = Global_30;
    //	        }
    //	  if (wiretype==5) {
    //	      g_ip->wt = Global_5;
    //	        }
    //	  if (wiretype==0) {
    //		  g_ip->wt = Low_swing;
    //	  }
    //  }
    //  //g_ip->wt = Global_5;
    //  if (force_config == 0)
    //    {
    //  	  g_ip->force_cache_config = false;
    //    }
    //    else
    //    {
    //    	g_ip->force_cache_config = true;
    //    	g_ip->ndbl=ndbl;
    //    	g_ip->ndwl=ndwl;
    //    	g_ip->nspd=nspd;
    //    	g_ip->ndcm=ndcm;
    //    	g_ip->ndsam1=ndsam1;
    //    	g_ip->ndsam2=ndsam2;
    //
    //
    //    }
    //
    //  if (ecc==0){
    //	  g_ip->add_ecc_b_=false;
    //  }
    //  else
    //  {
    //	  g_ip->add_ecc_b_=true;
    //  }

    g_ip->error_checking();

    init_tech_params(g_ip->F_sz_um, false);
    Wire winit;  // Do not delete this line. It initializes wires.
    // solve(&fin_res);
    // g_ip->display_ip();

    // solve(&fin_res);
    // output_UCA(&fin_res);
    // output_data_csv(fin_res);
    // delete (g_ip);

    return fin_res;
}

// McPAT's plain interface, please keep !!!
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
    int    ecc)
{
    g_ip = new InputParameter();

    uca_org_t fin_res;
    fin_res.valid = false;

    g_ip->data_arr_ram_cell_tech_type    = data_arr_ram_cell_tech_flavor_in;
    g_ip->data_arr_peri_global_tech_type = data_arr_peri_global_tech_flavor_in;
    g_ip->tag_arr_ram_cell_tech_type     = tag_arr_ram_cell_tech_flavor_in;
    g_ip->tag_arr_peri_global_tech_type  = tag_arr_peri_global_tech_flavor_in;

    g_ip->ic_proj_type     = interconnect_projection_type_in;
    g_ip->wire_is_mat_type = wire_inside_mat_type_in;
    g_ip->wire_os_mat_type = wire_outside_mat_type_in;
    g_ip->burst_len        = BURST_LENGTH_in;
    g_ip->int_prefetch_w   = INTERNAL_PREFETCH_WIDTH_in;
    g_ip->page_sz_bits     = PAGE_SIZE_BITS_in;

    g_ip->cache_sz     = cache_size;
    g_ip->line_sz      = line_size;
    g_ip->assoc        = associativity;
    g_ip->nbanks       = banks;
    g_ip->out_w        = output_width;
    g_ip->specific_tag = specific_tag;
    if (specific_tag == 0) {
        g_ip->tag_w = 42;
    }
    else
    {
        g_ip->tag_w = tag_width;
    }

    g_ip->access_mode       = access_mode;
    g_ip->delay_wt          = obj_func_delay;
    g_ip->dynamic_power_wt  = obj_func_dynamic_power;
    g_ip->leakage_power_wt  = obj_func_leakage_power;
    g_ip->area_wt           = obj_func_area;
    g_ip->cycle_time_wt     = obj_func_cycle_time;
    g_ip->delay_dev         = dev_func_delay;
    g_ip->dynamic_power_dev = dev_func_dynamic_power;
    g_ip->leakage_power_dev = dev_func_leakage_power;
    g_ip->area_dev          = dev_func_area;
    g_ip->cycle_time_dev    = dev_func_cycle_time;
    g_ip->temp              = temp;
    g_ip->ed                = ed_ed2_none;

    g_ip->F_sz_nm                            = tech_node;
    g_ip->F_sz_um                            = tech_node / 1000;
    g_ip->is_main_mem                        = (main_mem != 0) ? true : false;
    g_ip->is_cache                           = (cache == 1) ? true : false;
    g_ip->pure_ram                           = (cache == 0) ? true : false;
    g_ip->pure_cam                           = (cache == 2) ? true : false;
    g_ip->rpters_in_htree                    = (REPEATERS_IN_HTREE_SEGMENTS_in != 0) ? true : false;
    g_ip->ver_htree_wires_over_array         = VERTICAL_HTREE_WIRES_OVER_THE_ARRAY_in;
    g_ip->broadcast_addr_din_over_ver_htrees = BROADCAST_ADDR_DATAIN_OVER_VERTICAL_HTREES_in;

    g_ip->num_rw_ports     = rw_ports;
    g_ip->num_rd_ports     = excl_read_ports;
    g_ip->num_wr_ports     = excl_write_ports;
    g_ip->num_se_rd_ports  = single_ended_read_ports;
    g_ip->num_search_ports = search_ports;

    g_ip->print_detail = 1;
    g_ip->nuca         = 0;

    if (force_wiretype == 0) {
        g_ip->wt             = Global;
        g_ip->force_wiretype = false;
    }
    else
    {
        g_ip->force_wiretype = true;
        if (wiretype == 10) {
            g_ip->wt = Global_10;
        }
        if (wiretype == 20) {
            g_ip->wt = Global_20;
        }
        if (wiretype == 30) {
            g_ip->wt = Global_30;
        }
        if (wiretype == 5) {
            g_ip->wt = Global_5;
        }
        if (wiretype == 0) {
            g_ip->wt = Low_swing;
        }
    }
    // g_ip->wt = Global_5;
    if (force_config == 0) {
        g_ip->force_cache_config = false;
    }
    else
    {
        g_ip->force_cache_config = true;
        g_ip->ndbl               = ndbl;
        g_ip->ndwl               = ndwl;
        g_ip->nspd               = nspd;
        g_ip->ndcm               = ndcm;
        g_ip->ndsam1             = ndsam1;
        g_ip->ndsam2             = ndsam2;
    }

    if (ecc == 0) {
        g_ip->add_ecc_b_ = false;
    }
    else
    {
        g_ip->add_ecc_b_ = true;
    }

    if (!g_ip->error_checking()) exit(0);

    init_tech_params(g_ip->F_sz_um, false);
    Wire winit;  // Do not delete this line. It initializes wires.

    g_ip->display_ip();
    solve(&fin_res);
    output_UCA(&fin_res);
    output_data_csv(fin_res);
    delete (g_ip);

    return fin_res;
}

// cacti6.5's plain interface, please keep !!!
uca_org_t cacti_interface(
    int    cache_size,
    int    line_size,
    int    associativity,
    int    rw_ports,
    int    excl_read_ports,
    int    excl_write_ports,
    int    single_ended_read_ports,
    int    banks,
    double tech_node,  // in nm
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
    int    data_arr_ram_cell_tech_flavor_in,  // 0-4
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
    int    p_input)
{
    g_ip             = new InputParameter();
    g_ip->add_ecc_b_ = true;

    g_ip->data_arr_ram_cell_tech_type    = data_arr_ram_cell_tech_flavor_in;
    g_ip->data_arr_peri_global_tech_type = data_arr_peri_global_tech_flavor_in;
    g_ip->tag_arr_ram_cell_tech_type     = tag_arr_ram_cell_tech_flavor_in;
    g_ip->tag_arr_peri_global_tech_type  = tag_arr_peri_global_tech_flavor_in;

    g_ip->ic_proj_type     = interconnect_projection_type_in;
    g_ip->wire_is_mat_type = wire_inside_mat_type_in;
    g_ip->wire_os_mat_type = wire_outside_mat_type_in;
    g_ip->burst_len        = burst_length;
    g_ip->int_prefetch_w   = pre_width;
    g_ip->page_sz_bits     = page_sz;

    g_ip->cache_sz     = cache_size;
    g_ip->line_sz      = line_size;
    g_ip->assoc        = associativity;
    g_ip->nbanks       = banks;
    g_ip->out_w        = output_width;
    g_ip->specific_tag = specific_tag;
    if (tag_width == 0) {
        g_ip->tag_w = 42;
    }
    else
    {
        g_ip->tag_w = tag_width;
    }

    g_ip->access_mode       = access_mode;
    g_ip->delay_wt          = obj_func_delay;
    g_ip->dynamic_power_wt  = obj_func_dynamic_power;
    g_ip->leakage_power_wt  = obj_func_leakage_power;
    g_ip->area_wt           = obj_func_area;
    g_ip->cycle_time_wt     = obj_func_cycle_time;
    g_ip->delay_dev         = dev_func_delay;
    g_ip->dynamic_power_dev = dev_func_dynamic_power;
    g_ip->leakage_power_dev = dev_func_leakage_power;
    g_ip->area_dev          = dev_func_area;
    g_ip->cycle_time_dev    = dev_func_cycle_time;
    g_ip->ed                = ed_ed2_none;

    switch (wt)
    {
    case (0):
        g_ip->force_wiretype = 0;
        g_ip->wt             = Global;
        break;
    case (1):
        g_ip->force_wiretype = 1;
        g_ip->wt             = Global;
        break;
    case (2):
        g_ip->force_wiretype = 1;
        g_ip->wt             = Global_5;
        break;
    case (3):
        g_ip->force_wiretype = 1;
        g_ip->wt             = Global_10;
        break;
    case (4):
        g_ip->force_wiretype = 1;
        g_ip->wt             = Global_20;
        break;
    case (5):
        g_ip->force_wiretype = 1;
        g_ip->wt             = Global_30;
        break;
    case (6):
        g_ip->force_wiretype = 1;
        g_ip->wt             = Low_swing;
        break;
    default: cout << "Unknown wire type!\n"; exit(0);
    }

    g_ip->delay_wt_nuca          = nuca_obj_func_delay;
    g_ip->dynamic_power_wt_nuca  = nuca_obj_func_dynamic_power;
    g_ip->leakage_power_wt_nuca  = nuca_obj_func_leakage_power;
    g_ip->area_wt_nuca           = nuca_obj_func_area;
    g_ip->cycle_time_wt_nuca     = nuca_obj_func_cycle_time;
    g_ip->delay_dev_nuca         = dev_func_delay;
    g_ip->dynamic_power_dev_nuca = nuca_dev_func_dynamic_power;
    g_ip->leakage_power_dev_nuca = nuca_dev_func_leakage_power;
    g_ip->area_dev_nuca          = nuca_dev_func_area;
    g_ip->cycle_time_dev_nuca    = nuca_dev_func_cycle_time;
    g_ip->nuca                   = is_nuca;
    g_ip->nuca_bank_count        = nuca_bank_count;
    if (nuca_bank_count > 0) {
        g_ip->force_nuca_bank = 1;
    }
    g_ip->cores       = core_count;
    g_ip->cache_level = cache_level;

    g_ip->temp = temp;

    g_ip->F_sz_nm         = tech_node;
    g_ip->F_sz_um         = tech_node / 1000;
    g_ip->is_main_mem     = (main_mem != 0) ? true : false;
    g_ip->is_cache        = (cache != 0) ? true : false;
    g_ip->rpters_in_htree = (REPEATERS_IN_HTREE_SEGMENTS_in != 0) ? true : false;

    g_ip->num_rw_ports    = rw_ports;
    g_ip->num_rd_ports    = excl_read_ports;
    g_ip->num_wr_ports    = excl_write_ports;
    g_ip->num_se_rd_ports = single_ended_read_ports;
    g_ip->print_detail    = 1;
    g_ip->nuca            = 0;

    g_ip->wt                 = Global_5;
    g_ip->force_cache_config = false;
    g_ip->force_wiretype     = false;
    g_ip->print_input_args   = p_input;

    uca_org_t fin_res;
    fin_res.valid = false;

    if (g_ip->error_checking() == false) exit(0);
    if (g_ip->print_input_args) g_ip->display_ip();
    init_tech_params(g_ip->F_sz_um, false);
    Wire winit;  // Do not delete this line. It initializes wires.

    if (g_ip->nuca == 1) {
        Nuca n(&g_tp.peri_global);
        n.sim_nuca();
    }
    solve(&fin_res);

    output_UCA(&fin_res);

    delete (g_ip);
    return fin_res;
}

// CACTI3DD's plain interface, please keep !!!
uca_org_t cacti_interface(
    int    dram_cap_tot_byte,
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
    int    partition_level)
{
    g_ip = new InputParameter();

    uca_org_t fin_res;
    fin_res.valid = false;

    g_ip->data_arr_ram_cell_tech_type    = data_arr_ram_cell_tech_flavor_in;
    g_ip->data_arr_peri_global_tech_type = data_arr_peri_global_tech_flavor_in;
    g_ip->tag_arr_ram_cell_tech_type     = tag_arr_ram_cell_tech_flavor_in;
    g_ip->tag_arr_peri_global_tech_type  = tag_arr_peri_global_tech_flavor_in;

    g_ip->ic_proj_type     = interconnect_projection_type_in;
    g_ip->wire_is_mat_type = wire_inside_mat_type_in;
    g_ip->wire_os_mat_type = wire_outside_mat_type_in;
    g_ip->burst_len        = BURST_LENGTH_in;
    g_ip->int_prefetch_w   = INTERNAL_PREFETCH_WIDTH_in;
    g_ip->page_sz_bits     = PAGE_SIZE_BITS_in;

    g_ip->num_die_3d   = num_dies;
    g_ip->cache_sz     = dram_cap_tot_byte;
    g_ip->line_sz      = line_size;
    g_ip->assoc        = associativity;
    g_ip->nbanks       = banks;
    g_ip->out_w        = output_width;
    g_ip->specific_tag = specific_tag;
    if (specific_tag == 0) {
        g_ip->tag_w = 42;
    }
    else
    {
        g_ip->tag_w = tag_width;
    }

    g_ip->access_mode       = access_mode;
    g_ip->delay_wt          = obj_func_delay;
    g_ip->dynamic_power_wt  = obj_func_dynamic_power;
    g_ip->leakage_power_wt  = obj_func_leakage_power;
    g_ip->area_wt           = obj_func_area;
    g_ip->cycle_time_wt     = obj_func_cycle_time;
    g_ip->delay_dev         = dev_func_delay;
    g_ip->dynamic_power_dev = dev_func_dynamic_power;
    g_ip->leakage_power_dev = dev_func_leakage_power;
    g_ip->area_dev          = dev_func_area;
    g_ip->cycle_time_dev    = dev_func_cycle_time;
    g_ip->temp              = temp;
    g_ip->ed                = ed_ed2_none;

    g_ip->F_sz_nm                            = tech_node;
    g_ip->F_sz_um                            = tech_node / 1000;
    g_ip->is_main_mem                        = (main_mem != 0) ? true : false;
    g_ip->is_cache                           = (cache == 1) ? true : false;
    g_ip->pure_ram                           = (cache == 0) ? true : false;
    g_ip->pure_cam                           = (cache == 2) ? true : false;
    g_ip->rpters_in_htree                    = (REPEATERS_IN_HTREE_SEGMENTS_in != 0) ? true : false;
    g_ip->ver_htree_wires_over_array         = VERTICAL_HTREE_WIRES_OVER_THE_ARRAY_in;
    g_ip->broadcast_addr_din_over_ver_htrees = BROADCAST_ADDR_DATAIN_OVER_VERTICAL_HTREES_in;

    g_ip->num_rw_ports     = rw_ports;
    g_ip->num_rd_ports     = excl_read_ports;
    g_ip->num_wr_ports     = excl_write_ports;
    g_ip->num_se_rd_ports  = single_ended_read_ports;
    g_ip->num_search_ports = search_ports;

    g_ip->print_detail = 1;
    g_ip->nuca         = 0;

    if (force_wiretype == 0) {
        g_ip->wt             = Global;
        g_ip->force_wiretype = false;
    }
    else
    {
        g_ip->force_wiretype = true;
        if (wiretype == 10) {
            g_ip->wt = Global_10;
        }
        if (wiretype == 20) {
            g_ip->wt = Global_20;
        }
        if (wiretype == 30) {
            g_ip->wt = Global_30;
        }
        if (wiretype == 5) {
            g_ip->wt = Global_5;
        }
        if (wiretype == 0) {
            g_ip->wt = Low_swing;
        }
    }
    // g_ip->wt = Global_5;
    if (force_config == 0) {
        g_ip->force_cache_config = false;
    }
    else
    {
        g_ip->force_cache_config = true;
        g_ip->ndbl               = ndbl;
        g_ip->ndwl               = ndwl;
        g_ip->nspd               = nspd;
        g_ip->ndcm               = ndcm;
        g_ip->ndsam1             = ndsam1;
        g_ip->ndsam2             = ndsam2;
    }

    if (ecc == 0) {
        g_ip->add_ecc_b_ = false;
    }
    else
    {
        g_ip->add_ecc_b_ = true;
    }

    // CACTI3DD
    g_ip->is_3d_mem          = is_3d_dram;
    g_ip->burst_depth        = burst_depth;
    g_ip->io_width           = IO_width;
    g_ip->sys_freq_MHz       = sys_freq;
    g_ip->print_detail_debug = debug_detail;

    g_ip->tsv_is_subarray_type = tsv_gran_is_subarray;
    g_ip->tsv_os_bank_type     = tsv_gran_os_bank;

    g_ip->partition_gran    = partition_level;
    g_ip->num_tier_row_sprd = num_tier_row_sprd;
    g_ip->num_tier_col_sprd = num_tier_col_sprd;
    if (partition_level == 3)
        g_ip->fine_gran_bank_lvl = true;
    else
        g_ip->fine_gran_bank_lvl = false;

    if (!g_ip->error_checking()) exit(0);

    init_tech_params(g_ip->F_sz_um, false);
    Wire winit;  // Do not delete this line. It initializes wires.

    // tsv
    // TSV tsv_test(Coarse);
    // tsv_test.print_TSV();

    g_ip->display_ip();
    solve(&fin_res);
    output_UCA(&fin_res);
    output_data_csv_3dd(fin_res);
    delete (g_ip);

    return fin_res;
}
