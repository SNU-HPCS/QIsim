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

#include "min_values_t.h"
#include "uca_org_t.h"
#include "nuca_org_t.h"
#include "mem_array.h"

void min_values_t::update_min_values(const min_values_t *val)
{
    min_delay   = (min_delay > val->min_delay) ? val->min_delay : min_delay;
    min_dyn     = (min_dyn > val->min_dyn) ? val->min_dyn : min_dyn;
    min_leakage = (min_leakage > val->min_leakage) ? val->min_leakage : min_leakage;
    min_area    = (min_area > val->min_area) ? val->min_area : min_area;
    min_cyc     = (min_cyc > val->min_cyc) ? val->min_cyc : min_cyc;
}

void min_values_t::update_min_values(const uca_org_t &res)
{
    min_delay   = (min_delay > res.access_time) ? res.access_time : min_delay;
    min_dyn     = (min_dyn > res.power.readOp.dynamic) ? res.power.readOp.dynamic : min_dyn;
    min_leakage = (min_leakage > res.power.readOp.leakage) ? res.power.readOp.leakage : min_leakage;
    min_area    = (min_area > res.area) ? res.area : min_area;
    min_cyc     = (min_cyc > res.cycle_time) ? res.cycle_time : min_cyc;
}

void min_values_t::update_min_values(const nuca_org_t *res)
{
    min_delay   = (min_delay > res->nuca_pda.delay) ? res->nuca_pda.delay : min_delay;
    min_dyn     = (min_dyn > res->nuca_pda.power.readOp.dynamic) ? res->nuca_pda.power.readOp.dynamic : min_dyn;
    min_leakage = (min_leakage > res->nuca_pda.power.readOp.leakage) ? res->nuca_pda.power.readOp.leakage : min_leakage;
    min_area    = (min_area > res->nuca_pda.area.get_area()) ? res->nuca_pda.area.get_area() : min_area;
    min_cyc     = (min_cyc > res->nuca_pda.cycle_time) ? res->nuca_pda.cycle_time : min_cyc;
}

void min_values_t::update_min_values(const mem_array *res)
{
    min_delay   = (min_delay > res->access_time) ? res->access_time : min_delay;
    min_dyn     = (min_dyn > res->power.readOp.dynamic) ? res->power.readOp.dynamic : min_dyn;
    min_leakage = (min_leakage > res->power.readOp.leakage) ? res->power.readOp.leakage : min_leakage;
    min_area    = (min_area > res->area) ? res->area : min_area;
    min_cyc     = (min_cyc > res->cycle_time) ? res->cycle_time : min_cyc;
}
