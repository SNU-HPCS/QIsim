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
#include <cmath>

#include "uca_org_t.h"
#include "min_values_t.h"
#include "mem_array.h"
#include "input_parameter.h"
#include "technology_parameter.h"
#include "calculate_time.h"
#include "dynamic_parameter.h"
#include "uca.h"

using namespace std;

static bool check_uca_org(uca_org_t &u, min_values_t *minval);
static bool check_mem_org(mem_array &u, const min_values_t *minval);
static void find_optimal_uca(uca_org_t *res, min_values_t *minval, list<uca_org_t> &ulist);
static void filter_tag_arr(const min_values_t *min, list<mem_array *> &list);
static void filter_data_arr(list<mem_array *> &curr_list);

uca_org_t::uca_org_t() : tag_array2(0), data_array2(0) {}
void uca_org_t::find_delay()
{
    mem_array *data_arr = data_array2;
    mem_array *tag_arr  = tag_array2;

    // check whether it is a regular cache or scratch ram
    if (g_ip->pure_ram || g_ip->pure_cam || g_ip->fully_assoc) {
        access_time = data_arr->access_time;
    }
    // Both tag and data lookup happen in parallel
    // and the entire set is sent over the data array h-tree without
    // waiting for the way-select signal --TODO add the corresponding
    // power overhead Nav
    else if (g_ip->fast_access == true)
    {
        access_time = MAX(tag_arr->access_time, data_arr->access_time);
    }
    // Tag is accessed first. On a hit, way-select signal along with the
    // address is sent to read/write the appropriate block in the data
    // array
    else if (g_ip->is_seq_acc == true)
    {
        access_time = tag_arr->access_time + data_arr->access_time;
    }
    // Normal access: tag array access and data array access happen in parallel.
    // But, the data array will wait for the way-select and transfer only the
    // appropriate block over the h-tree.
    else
    {
        access_time = MAX(tag_arr->access_time + data_arr->delay_senseamp_mux_decoder, data_arr->delay_before_subarray_output_driver)
                      + data_arr->delay_from_subarray_output_driver_to_output;
    }
}

void uca_org_t::find_energy()
{
    if (!(g_ip->pure_ram || g_ip->pure_cam || g_ip->fully_assoc))  //(g_ip->is_cache)
        power = data_array2->power + tag_array2->power;
    else
        power = data_array2->power;
}

void uca_org_t::find_area()
{
    if (g_ip->pure_ram || g_ip->pure_cam || g_ip->fully_assoc)  //(g_ip->is_cache == false)
    {
        cache_ht  = data_array2->height;
        cache_len = data_array2->width;
    }
    else
    {
        cache_ht  = MAX(tag_array2->height, data_array2->height);
        cache_len = tag_array2->width + data_array2->width;
    }
    area = cache_ht * cache_len;
}

void uca_org_t::find_cyc()
{
    if ((g_ip->pure_ram || g_ip->pure_cam || g_ip->fully_assoc))  //(g_ip->is_cache == false)
    {
        cycle_time = data_array2->cycle_time;
    }
    else
    {
        cycle_time = MAX(tag_array2->cycle_time, data_array2->cycle_time);
    }
}

void uca_org_t::adjust_area()
{
    double area_adjust;
    if (g_ip->pure_ram || g_ip->pure_cam || g_ip->fully_assoc) {
        if (data_array2->area_efficiency / 100.0 < 0.2) {
            // area_adjust = sqrt(area/(area*(data_array2->area_efficiency/100.0)/0.2));
            area_adjust = sqrt(0.2 / (data_array2->area_efficiency / 100.0));
            cache_ht    = cache_ht / area_adjust;
            cache_len   = cache_len / area_adjust;
        }
    }
    area = cache_ht * cache_len;
}

void uca_org_t::cleanup()
{
    if (data_array2 != 0) delete data_array2;
    if (tag_array2 != 0) delete tag_array2;
}

/*
 * Performs exhaustive search across different sub-array sizes,
 * wire types and aspect ratios to find an optimal UCA organization
 * 1. First different valid tag array organizations are calculated
 *    and stored in tag_arr array
 * 2. The exhaustive search is repeated to find valid data array
 *    organizations and stored in data_arr array
 * 3. Cache area, delay, power, and cycle time for different
 *    cache organizations are calculated based on the
 *    above results
 * 4. Cache model with least cost is picked from sol_list
 */
void solve(uca_org_t *fin_res)
{
    /// bool   is_dram  = false;
    int  pure_ram = g_ip->pure_ram;
    bool pure_cam = g_ip->pure_cam;

    init_tech_params(g_ip->F_sz_um, false);
    g_ip->print_detail_debug = 0;  // ---detail outputs for debug, initiated for 3D memory

    list<mem_array *>           tag_arr(0);
    list<mem_array *>           data_arr(0);
    list<mem_array *>::iterator miter;
    list<uca_org_t>             sol_list(1, uca_org_t());

    fin_res->tag_array.access_time   = 0;
    fin_res->tag_array.Ndwl          = 0;
    fin_res->tag_array.Ndbl          = 0;
    fin_res->tag_array.Nspd          = 0;
    fin_res->tag_array.deg_bl_muxing = 0;
    fin_res->tag_array.Ndsam_lev_1   = 0;
    fin_res->tag_array.Ndsam_lev_2   = 0;

    // distribute calculate_time() execution to multiple threads
    calc_time_mt_wrapper_struct *calc_array = new calc_time_mt_wrapper_struct[nthreads];
    pthread_t                    threads[nthreads];

    for (uint32_t t = 0; t < nthreads; t++) {
        calc_array[t].tid      = t;
        calc_array[t].pure_ram = pure_ram;
        calc_array[t].pure_cam = pure_cam;
        calc_array[t].data_res = new min_values_t();
        calc_array[t].tag_res  = new min_values_t();
    }

    bool is_tag;
    /// uint32_t ram_cell_tech_type;

    // If it's a cache, first calculate the area, delay and power for all tag array partitions.
    if (!(pure_ram || pure_cam || g_ip->fully_assoc)) {  // cache
        is_tag = true;
        /// ram_cell_tech_type  = g_ip->tag_arr_ram_cell_tech_type;
        ///  is_dram             = ((ram_cell_tech_type == lp_dram) || (ram_cell_tech_type == comm_dram));
        init_tech_params(g_ip->F_sz_um, is_tag);

        for (uint32_t t = 0; t < nthreads; t++) {
            calc_array[t].is_tag      = is_tag;
            calc_array[t].is_main_mem = false;
            calc_array[t].Nspd_min    = 0.125;
            pthread_create(&threads[t], NULL, calc_time_mt_wrapper, (void *)(&(calc_array[t])));
        }

        for (uint32_t t = 0; t < nthreads; t++) {
            pthread_join(threads[t], NULL);
        }

        for (uint32_t t = 0; t < nthreads; t++) {
            calc_array[t].data_arr.sort(mem_array::lt());
            data_arr.merge(calc_array[t].data_arr, mem_array::lt());
            calc_array[t].tag_arr.sort(mem_array::lt());
            tag_arr.merge(calc_array[t].tag_arr, mem_array::lt());
        }
    }

    // calculate the area, delay and power for all data array partitions (for cache or plain RAM).
    //  if (!g_ip->fully_assoc)
    // {//in the new cacti, cam, fully_associative cache are processed as single array in the data portion
    is_tag = false;
    /// ram_cell_tech_type  = g_ip->data_arr_ram_cell_tech_type;
    /// is_dram             = ((ram_cell_tech_type == lp_dram) || (ram_cell_tech_type == comm_dram));
    init_tech_params(g_ip->F_sz_um, is_tag);

    for (uint32_t t = 0; t < nthreads; t++) {
        calc_array[t].is_tag      = is_tag;
        calc_array[t].is_main_mem = g_ip->is_main_mem;
        if (!(pure_cam || g_ip->fully_assoc)) {
            calc_array[t].Nspd_min = (double)(g_ip->out_w) / (double)(g_ip->block_sz * 8);
        }
        else
        {
            calc_array[t].Nspd_min = 1;
        }

        pthread_create(&threads[t], NULL, calc_time_mt_wrapper, (void *)(&(calc_array[t])));
    }

    for (uint32_t t = 0; t < nthreads; t++) {
        pthread_join(threads[t], NULL);
    }

    data_arr.clear();
    for (uint32_t t = 0; t < nthreads; t++) {
        calc_array[t].data_arr.sort(mem_array::lt());
        data_arr.merge(calc_array[t].data_arr, mem_array::lt());
    }
    //  }

    min_values_t *d_min     = new min_values_t();
    min_values_t *t_min     = new min_values_t();
    min_values_t *cache_min = new min_values_t();

    for (uint32_t t = 0; t < nthreads; t++) {
        d_min->update_min_values(calc_array[t].data_res);
        t_min->update_min_values(calc_array[t].tag_res);
    }

    for (miter = data_arr.begin(); miter != data_arr.end(); miter++) {
        (*miter)->arr_min = d_min;
    }

    // cout << data_arr.size() << "\t" << tag_arr.size() <<" before\n";
    filter_data_arr(data_arr);
    if (!(pure_ram || pure_cam || g_ip->fully_assoc)) {
        filter_tag_arr(t_min, tag_arr);
    }
    // cout << data_arr.size() << "\t" << tag_arr.size() <<" after\n";

    if (pure_ram || pure_cam || g_ip->fully_assoc) {
        for (miter = data_arr.begin(); miter != data_arr.end(); miter++) {
            uca_org_t &curr_org  = sol_list.back();
            curr_org.tag_array2  = NULL;
            curr_org.data_array2 = (*miter);

            curr_org.find_characteristics();

            // update min values for the entire cache
            cache_min->update_min_values(curr_org);

            sol_list.push_back(uca_org_t());
        }
    }
    else
    {
        while (tag_arr.empty() != true) {
            mem_array *arr_temp = (tag_arr.back());
            // delete tag_arr.back();
            tag_arr.pop_back();

            for (miter = data_arr.begin(); miter != data_arr.end(); miter++) {
                uca_org_t &curr_org  = sol_list.back();
                curr_org.tag_array2  = arr_temp;
                curr_org.data_array2 = (*miter);

                curr_org.find_characteristics();

                // update min values for the entire cache
                cache_min->update_min_values(curr_org);

                sol_list.push_back(uca_org_t());
            }
        }
    }

    sol_list.pop_back();

    find_optimal_uca(fin_res, cache_min, sol_list);

    sol_list.clear();

    for (miter = data_arr.begin(); miter != data_arr.end(); ++miter) {
        if (*miter != fin_res->data_array2) {
            delete *miter;
        }
    }
    data_arr.clear();

    for (uint32_t t = 0; t < nthreads; t++) {
        delete calc_array[t].data_res;
        delete calc_array[t].tag_res;
    }

    delete[] calc_array;
    delete cache_min;
    delete d_min;
    delete t_min;
}

void update(uca_org_t *fin_res)
{
    if (fin_res->tag_array2) {
        init_tech_params(g_ip->F_sz_um, true);
        DynamicParameter tag_arr_dyn_p(
            true,
            g_ip->pure_ram,
            g_ip->pure_cam,
            fin_res->tag_array2->Nspd,
            fin_res->tag_array2->Ndwl,
            fin_res->tag_array2->Ndbl,
            fin_res->tag_array2->Ndcm,
            fin_res->tag_array2->Ndsam_lev_1,
            fin_res->tag_array2->Ndsam_lev_2,
            fin_res->data_array2->wt,
            g_ip->is_main_mem);
        if (tag_arr_dyn_p.is_valid) {
            UCA *tag_arr               = new UCA(tag_arr_dyn_p);
            fin_res->tag_array2->power = tag_arr->power;
        }
        else
        {
            cout << "ERROR: Cannot retrieve array structure for leakage feedback" << endl;
            exit(1);
        }
    }
    init_tech_params(g_ip->F_sz_um, false);
    DynamicParameter data_arr_dyn_p(
        false,
        g_ip->pure_ram,
        g_ip->pure_cam,
        fin_res->data_array2->Nspd,
        fin_res->data_array2->Ndwl,
        fin_res->data_array2->Ndbl,
        fin_res->data_array2->Ndcm,
        fin_res->data_array2->Ndsam_lev_1,
        fin_res->data_array2->Ndsam_lev_2,
        fin_res->data_array2->wt,
        g_ip->is_main_mem);
    if (data_arr_dyn_p.is_valid) {
        UCA *data_arr               = new UCA(data_arr_dyn_p);
        fin_res->data_array2->power = data_arr->power;
    }
    else
    {
        cout << "ERROR: Cannot retrieve array structure for leakage feedback" << endl;
        exit(1);
    }

    fin_res->find_energy();
}

bool check_uca_org(uca_org_t &u, min_values_t *minval)
{
    if (((u.access_time - minval->min_delay) * 100 / minval->min_delay) > g_ip->delay_dev) {
        return false;
    }
    if (((u.power.readOp.dynamic - minval->min_dyn) / minval->min_dyn) * 100 > g_ip->dynamic_power_dev) {
        return false;
    }
    if (((u.power.readOp.leakage - minval->min_leakage) / minval->min_leakage) * 100 > g_ip->leakage_power_dev) {
        return false;
    }
    if (((u.cycle_time - minval->min_cyc) / minval->min_cyc) * 100 > g_ip->cycle_time_dev) {
        return false;
    }
    if (((u.area - minval->min_area) / minval->min_area) * 100 > g_ip->area_dev) {
        return false;
    }
    return true;
}

bool check_mem_org(mem_array &u, const min_values_t *minval)
{
    if (((u.access_time - minval->min_delay) * 100 / minval->min_delay) > g_ip->delay_dev) {
        return false;
    }
    if (((u.power.readOp.dynamic - minval->min_dyn) / minval->min_dyn) * 100 > g_ip->dynamic_power_dev) {
        return false;
    }
    if (((u.power.readOp.leakage - minval->min_leakage) / minval->min_leakage) * 100 > g_ip->leakage_power_dev) {
        return false;
    }
    if (((u.cycle_time - minval->min_cyc) / minval->min_cyc) * 100 > g_ip->cycle_time_dev) {
        return false;
    }
    if (((u.area - minval->min_area) / minval->min_area) * 100 > g_ip->area_dev) {
        return false;
    }
    return true;
}

void find_optimal_uca(uca_org_t *res, min_values_t *minval, list<uca_org_t> &ulist)
{
    double cost     = 0;
    double min_cost = BIGNUM;
    float  d, a, dp, lp, c;

    dp = g_ip->dynamic_power_wt;
    lp = g_ip->leakage_power_wt;
    a  = g_ip->area_wt;
    d  = g_ip->delay_wt;
    c  = g_ip->cycle_time_wt;

    if (ulist.empty() == true) {
        cout << "ERROR: no valid cache organizations found" << endl;
        exit(0);
    }

    for (list<uca_org_t>::iterator niter = ulist.begin(); niter != ulist.end(); niter++) {
        if (g_ip->ed == 1) {
            cost = ((niter)->access_time / minval->min_delay) * ((niter)->power.readOp.dynamic / minval->min_dyn);
            if (min_cost > cost) {
                min_cost = cost;
                *res     = (*(niter));
            }
        }
        else if (g_ip->ed == 2)
        {
            cost = ((niter)->access_time / minval->min_delay) * ((niter)->access_time / minval->min_delay) * ((niter)->power.readOp.dynamic / minval->min_dyn);
            if (min_cost > cost) {
                min_cost = cost;
                *res     = (*(niter));
            }
        }
        else
        {
            /*
             * check whether the current organization
             * meets the input deviation constraints
             */
            bool v = check_uca_org(*niter, minval);
            // if (minval->min_leakage == 0) minval->min_leakage = 0.1; //FIXME remove this after leakage modeling

            if (v) {
                cost
                    = (d * ((niter)->access_time / minval->min_delay) + c * ((niter)->cycle_time / minval->min_cyc)
                       + dp * ((niter)->power.readOp.dynamic / minval->min_dyn)
                       + lp * ((niter)->power.readOp.leakage / minval->min_leakage)
                       + a * ((niter)->area / minval->min_area));
                // fprintf(stderr, "cost = %g\n", cost);

                if (min_cost > cost) {
                    min_cost = cost;
                    *res     = (*(niter));
                    niter    = ulist.erase(niter);
                    if (niter != ulist.begin()) niter--;
                }
            }
            else
            {
                niter = ulist.erase(niter);
                if (niter != ulist.begin()) niter--;
            }
        }
    }

    if (min_cost == BIGNUM) {
        cout << "ERROR: no cache organizations met optimization criteria" << endl;
        exit(0);
    }
}

void filter_tag_arr(const min_values_t *min, list<mem_array *> &list)
{
    double cost = BIGNUM;
    double cur_cost;
    double wt_delay = g_ip->delay_wt, wt_dyn = g_ip->dynamic_power_wt, wt_leakage = g_ip->leakage_power_wt, wt_cyc = g_ip->cycle_time_wt,
           wt_area = g_ip->area_wt;
    mem_array *res = NULL;

    if (list.empty() == true) {
        cout << "ERROR: no valid tag organizations found" << endl;
        exit(1);
    }

    while (list.empty() != true) {
        bool v = check_mem_org(*list.back(), min);
        if (v) {
            cur_cost = wt_delay * (list.back()->access_time / min->min_delay) + wt_dyn * (list.back()->power.readOp.dynamic / min->min_dyn)
                       + wt_leakage * (list.back()->power.readOp.leakage / min->min_leakage) + wt_area * (list.back()->area / min->min_area)
                       + wt_cyc * (list.back()->cycle_time / min->min_cyc);
        }
        else
        {
            cur_cost = BIGNUM;
        }
        if (cur_cost < cost) {
            if (res != NULL) {
                delete res;
            }
            cost = cur_cost;
            res  = list.back();
        }
        else
        {
            delete list.back();
        }
        list.pop_back();
    }
    if (!res) {
        cout << "ERROR: no valid tag organizations found" << endl;
        exit(0);
    }

    list.push_back(res);
}

void filter_data_arr(list<mem_array *> &curr_list)
{
    if (curr_list.empty() == true) {
        cout << "ERROR: no valid data array organizations found" << endl;
        exit(1);
    }

    list<mem_array *>::iterator iter;

    for (iter = curr_list.begin(); iter != curr_list.end(); ++iter) {
        mem_array *m = *iter;

        if (m == NULL) exit(1);

        if (((m->access_time - m->arr_min->min_delay) / m->arr_min->min_delay > 0.5)
            && ((m->power.readOp.dynamic - m->arr_min->min_dyn) / m->arr_min->min_dyn > 0.5))
        {
            delete m;
            iter = curr_list.erase(iter);
            iter--;
        }
    }
}
