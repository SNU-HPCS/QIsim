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
#include <list>
#include <memory>

#include "calculate_time.h"
#include "mem_array.h"
#include "basic_circuit.h"
#include "const.h"
#include "input_parameter.h"
#include "min_values_t.h"
#include "dynamic_parameter.h"
#include "uca.h"
#include "htree2.h"
#include "predec.h"
#include "decoder.h"
#include "memorybus.h"

using namespace std;

void *calc_time_mt_wrapper(void *void_obj)
{
    calc_time_mt_wrapper_struct *calc_obj    = (calc_time_mt_wrapper_struct *)void_obj;
    uint32_t                     tid         = calc_obj->tid;
    list<mem_array *> &          data_arr    = calc_obj->data_arr;
    list<mem_array *> &          tag_arr     = calc_obj->tag_arr;
    bool                         is_tag      = calc_obj->is_tag;
    bool                         pure_ram    = calc_obj->pure_ram;
    bool                         pure_cam    = calc_obj->pure_cam;
    bool                         is_main_mem = calc_obj->is_main_mem;
    double                       Nspd_min    = calc_obj->Nspd_min;
    min_values_t *               data_res    = calc_obj->data_res;
    min_values_t *               tag_res     = calc_obj->tag_res;

    data_arr.clear();
    data_arr.push_back(new mem_array);
    tag_arr.clear();
    tag_arr.push_back(new mem_array);

    uint32_t Ndwl_niter = _log2(MAXDATAN) + 1;
    uint32_t Ndbl_niter = _log2(MAXDATAN) + 1;
    uint32_t Ndcm_niter = _log2(MAX_COL_MUX) + 1;
    uint32_t niter      = Ndwl_niter * Ndbl_niter * Ndcm_niter;

    bool is_valid_partition;
    int  wt_min, wt_max;

    if (g_ip->force_wiretype) {
        if (g_ip->wt == Full_swing) {
            wt_min = Global;
            wt_max = Low_swing - 1;
        }
        else
        {
            switch (g_ip->wt)
            {
            case Global: wt_min = wt_max = Global; break;
            case Global_5: wt_min = wt_max = Global_5; break;
            case Global_10: wt_min = wt_max = Global_10; break;
            case Global_20: wt_min = wt_max = Global_20; break;
            case Global_30: wt_min = wt_max = Global_30; break;
            case Low_swing: wt_min = wt_max = Low_swing; break;
            default: cerr << "Unknown wire type!\n"; exit(0);
            }
        }
    }
    else
    {
        wt_min = Global;
        wt_max = Low_swing;
    }

    for (double Nspd = Nspd_min; Nspd <= MAXDATASPD; Nspd *= 2) {
        for (int wr = wt_min; wr <= wt_max; wr++) {
            for (uint32_t iter = tid; iter < niter; iter += nthreads) {
                // reconstruct Ndwl, Ndbl, Ndcm
                unsigned int Ndwl = 1 << (iter / (Ndbl_niter * Ndcm_niter));
                unsigned int Ndbl = 1 << ((iter / (Ndcm_niter)) % Ndbl_niter);
                unsigned int Ndcm = 1 << (iter % Ndcm_niter);
                for (unsigned int Ndsam_lev_1 = 1; Ndsam_lev_1 <= MAX_COL_MUX; Ndsam_lev_1 *= 2) {
                    for (unsigned int Ndsam_lev_2 = 1; Ndsam_lev_2 <= MAX_COL_MUX; Ndsam_lev_2 *= 2) {
                        // for debuging
                        if (g_ip->force_cache_config && is_tag == false) {
                            wr   = g_ip->wt;
                            Ndwl = g_ip->ndwl;
                            Ndbl = g_ip->ndbl;
                            Ndcm = g_ip->ndcm;
                            if (g_ip->nspd != 0) {
                                Nspd = g_ip->nspd;
                            }
                            if (g_ip->ndsam1 != 0) {
                                Ndsam_lev_1 = g_ip->ndsam1;
                                Ndsam_lev_2 = g_ip->ndsam2;
                            }
                        }

                        if (is_tag == true) {
                            is_valid_partition = calculate_time(
                                is_tag,
                                pure_ram,
                                pure_cam,
                                Nspd,
                                Ndwl,
                                Ndbl,
                                Ndcm,
                                Ndsam_lev_1,
                                Ndsam_lev_2,
                                tag_arr.back(),
                                0,
                                NULL,
                                NULL,
                                (Wire_type)wr,
                                is_main_mem);
                        }
                        // If it's a fully-associative cache, the data array partition parameters are identical to that of
                        // the tag array, so compute data array partition properties also here.
                        if (is_tag == false || g_ip->fully_assoc) {
                            is_valid_partition = calculate_time(
                                is_tag /*false*/,
                                pure_ram,
                                pure_cam,
                                Nspd,
                                Ndwl,
                                Ndbl,
                                Ndcm,
                                Ndsam_lev_1,
                                Ndsam_lev_2,
                                data_arr.back(),
                                0,
                                NULL,
                                NULL,
                                (Wire_type)wr,
                                is_main_mem);
                            if (g_ip->is_3d_mem) {
                                Ndsam_lev_1 = MAX_COL_MUX + 1;
                                Ndsam_lev_2 = MAX_COL_MUX + 1;
                            }
                        }

                        if (is_valid_partition) {
                            if (is_tag == true) {
                                tag_arr.back()->wt = (enum Wire_type)wr;
                                tag_res->update_min_values(tag_arr.back());
                                tag_arr.push_back(new mem_array);
                            }
                            if (is_tag == false || g_ip->fully_assoc) {
                                data_arr.back()->wt = (enum Wire_type)wr;
                                data_res->update_min_values(data_arr.back());
                                data_arr.push_back(new mem_array);
                            }
                        }

                        if (g_ip->force_cache_config && is_tag == false) {
                            wr   = wt_max;
                            iter = niter;
                            if (g_ip->nspd != 0) {
                                Nspd = MAXDATASPD;
                            }
                            if (g_ip->ndsam1 != 0) {
                                Ndsam_lev_1 = MAX_COL_MUX + 1;
                                Ndsam_lev_2 = MAX_COL_MUX + 1;
                            }
                        }
                    }
                }
            }
        }
    }

    delete data_arr.back();
    delete tag_arr.back();
    data_arr.pop_back();
    tag_arr.pop_back();

    pthread_exit(NULL);
}

bool calculate_time(
    bool               is_tag,
    int                pure_ram,
    bool               pure_cam,
    double             Nspd,
    unsigned int       Ndwl,
    unsigned int       Ndbl,
    unsigned int       Ndcm,
    unsigned int       Ndsam_lev_1,
    unsigned int       Ndsam_lev_2,
    mem_array *        ptr_array,
    int                flag_results_populate,
    results_mem_array *ptr_results,
    uca_org_t *        ptr_fin_res,
    Wire_type          wt,  // merge from cacti-7 to cacti3d
    bool               is_main_mem)
{
    // GH
    // DynamicParameter dyn_p(is_tag, pure_ram, pure_cam, Nspd, Ndwl, Ndbl, Ndcm, Ndsam_lev_1, Ndsam_lev_2, wt, is_main_mem);
    auto dyn_p = make_unique<DynamicParameter>(is_tag, pure_ram, pure_cam, Nspd, Ndwl, Ndbl, Ndcm, Ndsam_lev_1, Ndsam_lev_2, wt, is_main_mem);

    if (dyn_p->is_valid != true) {
        return false;
    }

    calculate_time_internal(move(dyn_p), ptr_array);

    return true;
}

// GH
void calculate_time_internal(unique_ptr<DynamicParameter> dyn_p, mem_array *ptr_array)
{
    auto uca = make_unique<UCA>(*dyn_p);

    /*
    if (flag_results_populate) {  // For the final solution, populate the ptr_results data structure  -- TODO: copy only necessary variables
    }
    else
    {
    */
    int  num_act_mats_hor_dir                     = uca->bank.dp.num_act_mats_hor_dir;
    int  num_mats                                 = uca->bank.dp.num_mats;
    bool is_fa                                    = uca->bank.dp.fully_assoc;
    bool pure_cam                                 = uca->bank.dp.pure_cam;
    ptr_array->Ndcm                               = dyn_p->Ndcm;
    ptr_array->Ndwl                               = dyn_p->Ndwl;
    ptr_array->Ndbl                               = dyn_p->Ndbl;
    ptr_array->Nspd                               = dyn_p->Nspd;
    ptr_array->deg_bl_muxing                      = dyn_p->deg_bl_muxing;
    ptr_array->Ndsam_lev_1                        = dyn_p->Ndsam_lev_1;
    ptr_array->Ndsam_lev_2                        = dyn_p->Ndsam_lev_2;
    ptr_array->access_time                        = uca->access_time;
    ptr_array->cycle_time                         = uca->cycle_time;
    ptr_array->multisubbank_interleave_cycle_time = uca->multisubbank_interleave_cycle_time;
    ptr_array->area_ram_cells                     = uca->area_all_dataramcells;
    ptr_array->area                               = uca->area.get_area();
    if (g_ip->is_3d_mem) {  // ptr_array->area   = (uca->area_all_dataramcells)/0.5;
        ptr_array->area = uca->area.get_area();
        if (g_ip->num_die_3d > 1) ptr_array->area += uca->area_TSV_tot;
    }

    ptr_array->height                                      = uca->area.h;
    ptr_array->width                                       = uca->area.w;
    ptr_array->bank_height                                 = uca->bank.area.h;
    ptr_array->bank_length                                 = uca->bank.area.w;
    ptr_array->mat_height                                  = uca->bank.mat.area.h;
    ptr_array->mat_length                                  = uca->bank.mat.area.w;
    ptr_array->subarray_height                             = uca->bank.mat.subarray.area.h;
    ptr_array->subarray_length                             = uca->bank.mat.subarray.area.w;
    ptr_array->power                                       = uca->power;
    ptr_array->delay_senseamp_mux_decoder                  = MAX(uca->delay_array_to_sa_mux_lev_1_decoder, uca->delay_array_to_sa_mux_lev_2_decoder);
    ptr_array->delay_before_subarray_output_driver         = uca->delay_before_subarray_output_driver;
    ptr_array->delay_from_subarray_output_driver_to_output = uca->delay_from_subarray_out_drv_to_out;

    ptr_array->delay_route_to_bank                  = uca->htree_in_add->delay;
    ptr_array->delay_input_htree                    = uca->bank.htree_in_add->delay;
    ptr_array->delay_row_predecode_driver_and_block = uca->bank.mat.r_predec->delay;
    ptr_array->delay_row_decoder                    = uca->bank.mat.row_dec->delay;
    ptr_array->delay_bitlines                       = uca->bank.mat.delay_bitline;
    ptr_array->delay_matchlines                     = uca->bank.mat.delay_matchchline;
    ptr_array->delay_sense_amp                      = uca->bank.mat.delay_sa;
    ptr_array->delay_subarray_output_driver         = uca->bank.mat.delay_subarray_out_drv_htree;
    ptr_array->delay_dout_htree                     = uca->bank.htree_out_data->delay;
    ptr_array->delay_comparator                     = uca->bank.mat.delay_comparator;

    if (g_ip->is_3d_mem) {
        ptr_array->delay_row_activate_net               = uca->membus_RAS->delay_bus;
        ptr_array->delay_row_predecode_driver_and_block = uca->membus_RAS->delay_add_predecoder;
        ptr_array->delay_row_decoder                    = uca->membus_RAS->delay_add_decoder;
        ptr_array->delay_local_wordline                 = uca->membus_RAS->delay_lwl_drv;
        ptr_array->delay_column_access_net              = uca->membus_CAS->delay_bus;
        ptr_array->delay_column_predecoder              = uca->membus_CAS->delay_add_predecoder;
        ptr_array->delay_column_decoder                 = uca->membus_CAS->delay_add_decoder;
        ptr_array->delay_column_selectline              = 0;  // Integrated into add_decoder
        ptr_array->delay_datapath_net                   = uca->membus_data->delay_bus;
        ptr_array->delay_global_data                    = uca->membus_data->delay_global_data;
        ptr_array->delay_local_data_and_drv             = uca->membus_data->delay_local_data;
        ptr_array->delay_subarray_output_driver         = uca->bank.mat.delay_subarray_out_drv;
        ptr_array->delay_data_buffer                    = uca->membus_data->delay_data_buffer;

        /*ptr_array->energy_row_activate_net = uca->membus_RAS->add_bits * (uca->membus_RAS->center_stripe->power.readOp.dynamic +
        uca->membus_RAS->bank_bus->power.readOp.dynamic);
        ptr_array->energy_row_predecode_driver_and_block = uca->membus_RAS->add_predec->power.readOp.dynamic;
        ptr_array->energy_row_decoder = uca->membus_RAS->add_dec->power.readOp.dynamic;
        ptr_array->energy_local_wordline = uca->membus_RAS->num_lwl_drv * uca->membus_RAS->lwl_drv->power.readOp.dynamic;
        ptr_array->energy_column_access_net = uca->membus_CAS->add_bits * (uca->membus_CAS->center_stripe->power.readOp.dynamic +
        uca->membus_CAS->bank_bus->power.readOp.dynamic);
        ptr_array->energy_column_predecoder = uca->membus_CAS->add_predec->power.readOp.dynamic;
        ptr_array->energy_column_decoder = uca->membus_CAS->add_dec->power.readOp.dynamic;
        ptr_array->energy_column_selectline = uca->membus_CAS->column_sel->power.readOp.dynamic;
        ptr_array->energy_datapath_net = uca->membus_data->data_bits * (uca->membus_data->center_stripe->power.readOp.dynamic +
        uca->membus_data->bank_bus->power.readOp.dynamic);
        ptr_array->energy_global_data = uca->membus_data->data_bits * (uca->membus_data->global_data->power.readOp.dynamic);
        ptr_array->energy_local_data_and_drv = uca->membus_data->data_bits * (uca->membus_data->data_drv->power.readOp.dynamic);
        ptr_array->energy_data_buffer = 0;*/

        ptr_array->energy_row_activate_net               = uca->membus_RAS->power_bus.readOp.dynamic;
        ptr_array->energy_row_predecode_driver_and_block = uca->membus_RAS->power_add_predecoder.readOp.dynamic;
        ptr_array->energy_row_decoder                    = uca->membus_RAS->power_add_decoders.readOp.dynamic;
        ptr_array->energy_local_wordline                 = uca->membus_RAS->power_lwl_drv.readOp.dynamic;
        ptr_array->energy_bitlines                       = dyn_p->Ndwl * uca->bank.mat.power_bitline.readOp.dynamic;
        ptr_array->energy_sense_amp                      = dyn_p->Ndwl * uca->bank.mat.power_sa.readOp.dynamic;

        ptr_array->energy_column_access_net = uca->membus_CAS->power_bus.readOp.dynamic;
        ptr_array->energy_column_predecoder = uca->membus_CAS->power_add_predecoder.readOp.dynamic;
        ptr_array->energy_column_decoder    = uca->membus_CAS->power_add_decoders.readOp.dynamic;
        ptr_array->energy_column_selectline = uca->membus_CAS->power_col_sel.readOp.dynamic;

        ptr_array->energy_datapath_net           = uca->membus_data->power_bus.readOp.dynamic;
        ptr_array->energy_global_data            = uca->membus_data->power_global_data.readOp.dynamic;
        ptr_array->energy_local_data_and_drv     = uca->membus_data->power_local_data.readOp.dynamic;
        ptr_array->energy_subarray_output_driver = uca->bank.mat.power_subarray_out_drv.readOp.dynamic;  //
        ptr_array->energy_data_buffer            = 0;

        ptr_array->area_lwl_drv        = uca->area_lwl_drv;
        ptr_array->area_row_predec_dec = uca->area_row_predec_dec;
        ptr_array->area_col_predec_dec = uca->area_col_predec_dec;
        ptr_array->area_subarray       = uca->area_subarray;
        ptr_array->area_bus            = uca->area_bus;
        ptr_array->area_address_bus    = uca->area_address_bus;
        ptr_array->area_data_bus       = uca->area_data_bus;
        ptr_array->area_data_drv       = uca->area_data_drv;
        ptr_array->area_IOSA           = uca->area_IOSA;
        ptr_array->area_sense_amp      = uca->area_sense_amp;
        ptr_array->area_per_bank       = uca->area_per_bank;
    }

    ptr_array->all_banks_height = uca->area.h;
    ptr_array->all_banks_width  = uca->area.w;
    // ptr_array->area_efficiency = uca->area_all_dataramcells * 100 / (uca->area.get_area());
    ptr_array->area_efficiency = uca->area_all_dataramcells * 100 / ptr_array->area;

    ptr_array->power_routing_to_bank  = uca->power_routing_to_bank;
    ptr_array->power_addr_input_htree = uca->bank.htree_in_add->power;
    ptr_array->power_data_input_htree = uca->bank.htree_in_data->power;
    //    cout<<"power_data_input_htree"<<uca->bank.htree_in_data->power.readOp.leakage<<endl;
    ptr_array->power_data_output_htree = uca->bank.htree_out_data->power;
    //    cout<<"power_data_output_htree"<<uca->bank.htree_out_data->power.readOp.leakage<<endl;
    ptr_array->power_row_predecoder_drivers = uca->bank.mat.r_predec->driver_power;
    ptr_array->power_row_predecoder_drivers.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_row_predecoder_drivers.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_row_predecoder_drivers.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_row_predecoder_blocks = uca->bank.mat.r_predec->block_power;
    ptr_array->power_row_predecoder_blocks.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_row_predecoder_blocks.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_row_predecoder_blocks.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_row_decoders = uca->bank.mat.power_row_decoders;
    ptr_array->power_row_decoders.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_row_decoders.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_row_decoders.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_bit_mux_predecoder_drivers = uca->bank.mat.b_mux_predec->driver_power;
    ptr_array->power_bit_mux_predecoder_drivers.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_bit_mux_predecoder_drivers.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_bit_mux_predecoder_drivers.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_bit_mux_predecoder_blocks = uca->bank.mat.b_mux_predec->block_power;
    ptr_array->power_bit_mux_predecoder_blocks.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_bit_mux_predecoder_blocks.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_bit_mux_predecoder_blocks.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_bit_mux_decoders = uca->bank.mat.power_bit_mux_decoders;
    ptr_array->power_bit_mux_decoders.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_bit_mux_decoders.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_bit_mux_decoders.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_senseamp_mux_lev_1_predecoder_drivers = uca->bank.mat.sa_mux_lev_1_predec->driver_power;
    ptr_array->power_senseamp_mux_lev_1_predecoder_drivers.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_senseamp_mux_lev_1_predecoder_drivers.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_senseamp_mux_lev_1_predecoder_drivers.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_senseamp_mux_lev_1_predecoder_blocks = uca->bank.mat.sa_mux_lev_1_predec->block_power;
    ptr_array->power_senseamp_mux_lev_1_predecoder_blocks.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_senseamp_mux_lev_1_predecoder_blocks.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_senseamp_mux_lev_1_predecoder_blocks.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_senseamp_mux_lev_1_decoders = uca->bank.mat.power_sa_mux_lev_1_decoders;
    ptr_array->power_senseamp_mux_lev_1_decoders.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_senseamp_mux_lev_1_decoders.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_senseamp_mux_lev_1_decoders.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_senseamp_mux_lev_2_predecoder_drivers = uca->bank.mat.sa_mux_lev_2_predec->driver_power;
    ptr_array->power_senseamp_mux_lev_2_predecoder_drivers.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_senseamp_mux_lev_2_predecoder_drivers.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_senseamp_mux_lev_2_predecoder_drivers.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_senseamp_mux_lev_2_predecoder_blocks = uca->bank.mat.sa_mux_lev_2_predec->block_power;
    ptr_array->power_senseamp_mux_lev_2_predecoder_blocks.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_senseamp_mux_lev_2_predecoder_blocks.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_senseamp_mux_lev_2_predecoder_blocks.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_senseamp_mux_lev_2_decoders = uca->bank.mat.power_sa_mux_lev_2_decoders;
    ptr_array->power_senseamp_mux_lev_2_decoders.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_senseamp_mux_lev_2_decoders.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_senseamp_mux_lev_2_decoders.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_bitlines = uca->bank.mat.power_bitline;
    ptr_array->power_bitlines.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_bitlines.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_bitlines.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_sense_amps = uca->bank.mat.power_sa;
    ptr_array->power_sense_amps.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_sense_amps.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_sense_amps.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_prechg_eq_drivers = uca->bank.mat.power_bl_precharge_eq_drv;
    ptr_array->power_prechg_eq_drivers.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_prechg_eq_drivers.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_prechg_eq_drivers.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_output_drivers_at_subarray = uca->bank.mat.power_subarray_out_drv;
    ptr_array->power_output_drivers_at_subarray.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_output_drivers_at_subarray.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_output_drivers_at_subarray.searchOp.dynamic *= num_act_mats_hor_dir;

    ptr_array->power_comparators = uca->bank.mat.power_comparator;
    ptr_array->power_comparators.readOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_comparators.writeOp.dynamic *= num_act_mats_hor_dir;
    ptr_array->power_comparators.searchOp.dynamic *= num_act_mats_hor_dir;

    //    cout <<  "  num of mats: " << dyn_p.num_mats << endl;
    if (is_fa || pure_cam) {
        ptr_array->power_htree_in_search = uca->bank.htree_in_search->power;
        //    cout<<"power_htree_in_search"<<uca->bank.htree_in_search->power.readOp.leakage<<endl;
        ptr_array->power_htree_out_search = uca->bank.htree_out_search->power;
        //    cout<<"power_htree_out_search"<<uca->bank.htree_out_search->power.readOp.leakage<<endl;
        ptr_array->power_searchline = uca->bank.mat.power_searchline;
        //    cout<<"power_searchlineh"<<uca->bank.mat.power_searchline.readOp.leakage<<endl;
        ptr_array->power_searchline.searchOp.dynamic *= num_mats;
        ptr_array->power_searchline_precharge = uca->bank.mat.power_searchline_precharge;
        ptr_array->power_searchline_precharge.searchOp.dynamic *= num_mats;
        ptr_array->power_matchlines = uca->bank.mat.power_matchline;
        ptr_array->power_matchlines.searchOp.dynamic *= num_mats;
        ptr_array->power_matchline_precharge = uca->bank.mat.power_matchline_precharge;
        ptr_array->power_matchline_precharge.searchOp.dynamic *= num_mats;
        ptr_array->power_matchline_to_wordline_drv = uca->bank.mat.power_ml_to_ram_wl_drv;
        //    cout<<"power_matchline.searchOp.leakage"<<uca->bank.mat.power_matchline.searchOp.leakage<<endl;
    }

    ptr_array->activate_energy                       = uca->activate_energy;
    ptr_array->read_energy                           = uca->read_energy;
    ptr_array->write_energy                          = uca->write_energy;
    ptr_array->precharge_energy                      = uca->precharge_energy;
    ptr_array->refresh_power                         = uca->refresh_power;
    ptr_array->leak_power_subbank_closed_page        = uca->leak_power_subbank_closed_page;
    ptr_array->leak_power_subbank_open_page          = uca->leak_power_subbank_open_page;
    ptr_array->leak_power_request_and_reply_networks = uca->leak_power_request_and_reply_networks;

    ptr_array->precharge_delay = uca->precharge_delay;

    if (g_ip->is_3d_mem) {
        // CACTI3DD
        ptr_array->t_RCD = uca->t_RCD;
        ptr_array->t_RAS = uca->t_RAS;
        ptr_array->t_RC  = uca->t_RC;
        ptr_array->t_CAS = uca->t_CAS;
        ptr_array->t_RP  = uca->t_RP;
        ptr_array->t_RRD = uca->t_RRD;

        ptr_array->activate_energy  = uca->activate_energy;
        ptr_array->read_energy      = uca->read_energy;
        ptr_array->write_energy     = uca->write_energy;
        ptr_array->precharge_energy = uca->precharge_energy;

        ptr_array->activate_power  = uca->activate_power;
        ptr_array->read_power      = uca->read_power;
        ptr_array->write_power     = uca->write_power;
        ptr_array->peak_read_power = uca->read_energy / ((g_ip->burst_depth) / (g_ip->sys_freq_MHz * 1e6) / 2);

        ptr_array->num_row_subarray = dyn_p->num_r_subarray;
        ptr_array->num_col_subarray = dyn_p->num_c_subarray;

        ptr_array->delay_TSV_tot          = uca->delay_TSV_tot;
        ptr_array->area_TSV_tot           = uca->area_TSV_tot;
        ptr_array->dyn_pow_TSV_tot        = uca->dyn_pow_TSV_tot;
        ptr_array->dyn_pow_TSV_per_access = uca->dyn_pow_TSV_per_access;
        ptr_array->num_TSV_tot            = uca->num_TSV_tot;

        // Covers the previous values
        // ptr_array->area = g_ip->num_die_3d * (uca->area_per_bank * g_ip->nbanks);
        // ptr_array->area_efficiency = g_ip->num_die_3d * uca->area_all_dataramcells * 100 / ptr_array->area;
    }
    //      cout<<"power_matchline.searchOp.leakage"<<uca->bank.mat.<<endl;
    //
    //    if (!(is_fa || pure_cam))
    //    {
    //     cout <<  "  num of cols: " << dyn_p.num_c_subarray << endl;
    //    }
    //    else if (is_fa)
    //    {
    //  	  cout <<  "  num of cols: " << dyn_p.tag_num_c_subarray+ dyn_p.data_num_c_subarray<< endl;
    //    } else
    //  	  cout <<  "  num of cols: " << dyn_p.tag_num_c_subarray<< endl;
    //      cout <<  uca->bank.mat.subarray.get_total_cell_area()<<endl;

    if (g_ip->power_gating) {
        ptr_array->sram_sleep_tx_width       = uca->bank.mat.sram_sleep_tx->width;
        ptr_array->sram_sleep_tx_area        = uca->bank.mat.array_sleep_tx_area;
        ptr_array->sram_sleep_wakeup_latency = uca->bank.mat.array_wakeup_t;
        ptr_array->sram_sleep_wakeup_energy  = uca->bank.mat.array_wakeup_e.readOp.dynamic;

        ptr_array->wl_sleep_tx_width       = uca->bank.mat.row_dec->sleeptx->width;
        ptr_array->wl_sleep_tx_area        = uca->bank.mat.wl_sleep_tx_area;
        ptr_array->wl_sleep_wakeup_latency = uca->bank.mat.wl_wakeup_t;
        ptr_array->wl_sleep_wakeup_energy  = uca->bank.mat.wl_wakeup_e.readOp.dynamic;

        ptr_array->bl_floating_wakeup_latency = uca->bank.mat.blfloating_wakeup_t;
        ptr_array->bl_floating_wakeup_energy  = uca->bank.mat.blfloating_wakeup_e.readOp.dynamic;

        ptr_array->array_leakage = uca->bank.array_leakage;
        ptr_array->wl_leakage    = uca->bank.wl_leakage;
        ptr_array->cl_leakage    = uca->bank.cl_leakage;
    }

    ptr_array->num_active_mats    = uca->bank.dp.num_act_mats_hor_dir;
    ptr_array->num_submarray_mats = uca->bank.mat.num_subarrays_per_mat;
    //    cout<<"array_leakage"<<ptr_array->array_leakage<<endl;
    //    cout<<"wl_leakage"<<ptr_array->wl_leakage<<endl;
    //    cout<<"cl_leakage"<<ptr_array->cl_leakage<<endl;

    // GH
    ptr_array->dp = move(dyn_p);
    /*
    }
    */
}
