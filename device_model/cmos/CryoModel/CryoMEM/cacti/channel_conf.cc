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

#include <vector>
#include <cassert>
#include <cmath>

#include "channel_conf.h"
#include "mem_cad_parameters.h"
#include "memory_parameters.h"

using namespace std;

channel_conf::channel_conf(MemCadParameters* memcad_params, const vector<int>& dimm_cap, int bandwidth, Mem_DIMM type, bool low_power)
    : memcad_params(memcad_params), type(type), low_power(low_power), bandwidth(bandwidth), latency(0), valid(true)
{
    // assert(memcad_params);
    assert(dimm_cap.size() <= DIMM_PER_CHANNEL);
    assert(memcad_params->io_type < 2);  // So far, we just support DDR3 and DDR4.
    // upading capacity
    num_dimm_per_channel = 0;
    capacity             = 0;
    for (int i = 0; i < 5; i++) histogram_capacity[i] = 0;
    for (unsigned int i = 0; i < dimm_cap.size(); i++) {
        if (dimm_cap[i] == 0) continue;

        int index = (int)(log2(dimm_cap[i] + 0.1)) - 2;
        assert(index < 5);
        histogram_capacity[index]++;
        num_dimm_per_channel++;
        capacity += dimm_cap[i];
    }

    // updating bandwidth
    if (capacity > 0) bandwidth = 0;

    // bandwidth = MemoryParameters::bandwidth_load[memcad_params->io_type][4-num_dimm_per_channel];
    // updating channel cost
    cost = 0;
    for (int i = 0; i < 5; ++i) cost += histogram_capacity[i] * MemoryParameters::cost[memcad_params->io_type][type][i];

    // update energy
    calc_power();
}

void channel_conf::calc_power()
{
    double      read_ratio      = memcad_params->rd_2_wr_ratio / (1.0 + memcad_params->rd_2_wr_ratio);
    double      write_ratio     = 1.0 / (1.0 + memcad_params->rd_2_wr_ratio);
    Mem_IO_type current_io_type = memcad_params->io_type;
    double      capacity_ratio  = (capacity / (double)memcad_params->capacity);

    double T_BURST = 4;  // memory cycles

    energy_per_read = MemoryParameters::io_energy_read[current_io_type][type][num_dimm_per_channel - 1][bw_index(current_io_type, bandwidth)];
    energy_per_read /= (bandwidth / T_BURST);

    energy_per_write = MemoryParameters::io_energy_write[current_io_type][type][num_dimm_per_channel - 1][bw_index(current_io_type, bandwidth)];
    energy_per_write /= (bandwidth / T_BURST);
    if (memcad_params->capacity_wise) {
        energy_per_read *= capacity_ratio;
        energy_per_write *= capacity_ratio;
    }

    energy_per_access = read_ratio * energy_per_read + write_ratio * energy_per_write;
}

channel_conf* clone(channel_conf* origin)
{
    vector<int> temp;
    int         size = 4;
    for (int i = 0; i < 5; ++i) {
        for (int j = 0; j < origin->histogram_capacity[i]; ++j) {
            temp.push_back(size);
        }
        size *= 2;
    }
    channel_conf* new_channel = new channel_conf(origin->memcad_params, temp, origin->bandwidth, origin->type, origin->low_power);
    return new_channel;
}

ostream& operator<<(ostream& os, const channel_conf& ch_cnf)
{
    os << "cap: " << ch_cnf.capacity << " GB ";
    os << "bw: " << ch_cnf.bandwidth << " (MHz) ";
    os << "cost: $" << ch_cnf.cost << " ";
    os << "dpc: " << ch_cnf.num_dimm_per_channel << " ";
    os << "energy: " << ch_cnf.energy_per_access << " (nJ) ";
    os << " DIMM: " << ((ch_cnf.type == UDIMM) ? " UDIMM " : ((ch_cnf.type == RDIMM) ? " RDIMM " : "LRDIMM "));
    os << " low power: " << ((ch_cnf.low_power) ? "T " : "F ");
    os << "[ ";
    for (int i = 0; i < 5; i++) os << ch_cnf.histogram_capacity[i] << "(" << (1 << (i + 2)) << "GB) ";
    os << "]";
    return os;
}
