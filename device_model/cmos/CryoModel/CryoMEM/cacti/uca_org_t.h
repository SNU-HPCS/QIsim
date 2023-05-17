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

#ifndef __UCA_ORG_T_H__
#define __UCA_ORG_T_H__

#include "power_def.h"
#include "results_mem_array.h"

class mem_array;

class uca_org_t
{
   public:
    mem_array *       tag_array2;
    mem_array *       data_array2;
    double            access_time;
    double            cycle_time;
    double            area;
    double            area_efficiency;
    powerDef          power;
    double            leak_power_with_sleep_transistors_in_mats;
    double            cache_ht;
    double            cache_len;
    char              file_n[100];
    double            vdd_periph_global;
    bool              valid;
    results_mem_array tag_array;
    results_mem_array data_array;

    uca_org_t();
    void find_delay();
    void find_energy();
    void find_area();
    void find_cyc();
    void find_characteristics(){ find_delay(); find_energy(); find_area(); find_cyc(); }
    void adjust_area();  // for McPAT only to adjust routing overhead
    void cleanup();
    ~uca_org_t(){};
};

void solve(uca_org_t *fin_res);
void update(uca_org_t *fin_res);

#endif
