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

#include "mem_cad_parameters.h"
#include "input_parameter.h"

MemCadParameters::MemCadParameters(InputParameter* g_ip)
{
    // default value
    io_type              = DDR4;  // DDR3 vs. DDR4
    capacity             = 400;   // in GB
    num_bobs             = 4;     // default=4me
    num_channels_per_bob = 2;     // 1 means no bob
    capacity_wise        = true;  // true means the load on each channel is proportional to its capacity.
    first_metric         = Cost;
    second_metric        = Bandwidth;
    third_metric         = Energy;
    dimm_model           = ALL;
    low_power_permitted  = false;
    load                 = 0.9;  // between 0 to 1
    row_buffer_hit_rate  = 1;
    rd_2_wr_ratio        = 2;
    same_bw_in_bob       = true;   // true if all the channels in the bob have the same bandwidth
    mirror_in_bob        = true;   // true if all the channels in the bob have the same configs
    total_power          = false;  // false means just considering I/O Power.
    verbose              = false;
    // values for input
    io_type              = g_ip->io_type;
    capacity             = g_ip->capacity;
    num_bobs             = g_ip->num_bobs;
    num_channels_per_bob = g_ip->num_channels_per_bob;
    first_metric         = g_ip->first_metric;
    second_metric        = g_ip->second_metric;
    third_metric         = g_ip->third_metric;
    dimm_model           = g_ip->dimm_model;
    /// low_power_permitted=g_ip->low_power_permitted;
    /// load=g_ip->load;
    /// row_buffer_hit_rate=g_ip->row_buffer_hit_rate;
    /// rd_2_wr_ratio=g_ip->rd_2_wr_ratio;
    /// same_bw_in_bob=g_ip->same_bw_in_bob;
    mirror_in_bob = g_ip->mirror_in_bob;
    /// total_power=g_ip->total_power;
    verbose = g_ip->verbose;
}

void   MemCadParameters::print_inputs() {}
bool   MemCadParameters::sanity_check() { return true; }
double calculate_power(double load, double row_buffer_hr, double rd_wr_ratio, int chips_per_rank, int frequency_index, int lp) { return 0; }
int bw_index(Mem_IO_type type, int bandwidth)
{
    if (type == DDR3) {
        if (bandwidth <= 400)
            return 0;
        else if (bandwidth <= 533)
            return 1;
        else if (bandwidth <= 667)
            return 2;
        else
            return 3;
    }
    else
    {
        if (bandwidth <= 800)
            return 0;
        else if (bandwidth <= 933)
            return 1;
        else if (bandwidth <= 1066)
            return 2;
        else
            return 3;
    }
    return 0;
}
