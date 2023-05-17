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

#ifndef __MEM_CAD_PARAMETERS_H__
#define __MEM_CAD_PARAMETERS_H__

#include "enum/mem_io_type.h"
#include "enum/mem_cad_metrics.h"
#include "enum/dimm_model.h"

///#define INF 1000000
#define EPS 0.0000001

#define MAX_DIMM_PER_CHANNEL 3
#define MAX_CAP_PER_DIMM 64
#define MAX_RANKS_PER_DIMM 4
#define MIN_BW_PER_CHANNEL 400
#define MAX_DDR3_CHANNEL_BW 800
#define MAX_DDR4_CHANNEL_BW 1600
#define MAX_NUM_CHANNELS_PER_BOB 2
#define MAX_NUM_BOBS 6
#define DIMM_PER_CHANNEL 3

class InputParameter;

class MemCadParameters
{
   public:
    Mem_IO_type io_type;  // DDR3 vs. DDR4

    int capacity;  // in GB

    int num_bobs;  // default=4me

    /// int bw_per_channel; // defaul=1600 MHz;

    /// bool with_bob;

    int num_channels_per_bob;  // 1 means no bob

    bool capacity_wise;  // true means the load on each channel is proportional to its capacity.

    /// int min_bandwith;

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

    // Functions
    MemCadParameters(InputParameter* g_ip);
    void print_inputs();
    bool sanity_check();
};

int bw_index(Mem_IO_type type, int bandwidth);

#endif