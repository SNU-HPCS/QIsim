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

#ifndef __CALCULATE_TIME_H__
#define __CALCULATE_TIME_H__

#include <list>
#include <memory>

#include "results_mem_array.h"
#include "enum/wire_type.h"

class min_values_t;
class mem_array;
class uca_org_t;
class DynamicParameter;

struct calc_time_mt_wrapper_struct
{
    std::uint32_t tid;
    bool          is_tag;
    bool          pure_ram;
    bool          pure_cam;
    bool          is_main_mem;
    double        Nspd_min;

    min_values_t *data_res;
    min_values_t *tag_res;

    std::list<mem_array *> data_arr;
    std::list<mem_array *> tag_arr;
};

void *calc_time_mt_wrapper(void *void_obj);

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
    Wire_type          wtype,  // merge from cacti-7 to cacti3d
    bool               is_main_mem);

void calculate_time_internal(std::unique_ptr<DynamicParameter> dyn_p, mem_array *ptr_array);

#endif
