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

#include "bob_conf.h"
#include "channel_conf.h"

using namespace std;

bob_conf::bob_conf(MemCadParameters* memcad_params, vector<channel_conf*>* in_channels)
    : memcad_params(memcad_params),
      num_channels(0),
      capacity(0),
      bandwidth(0),
      energy_per_read(0),
      energy_per_write(0),
      energy_per_access(0),
      cost(0),
      latency(0),
      valid(true)
{
    assert(in_channels->size() <= MAX_NUM_CHANNELS_PER_BOB);
    for (int i = 0; i < MAX_NUM_CHANNELS_PER_BOB; i++) channels[i] = 0;

    for (unsigned int i = 0; i < in_channels->size(); ++i) {
        channels[i] = (*in_channels)[i];
        num_channels++;
        capacity += (*in_channels)[i]->capacity;
        cost += (*in_channels)[i]->cost;
        bandwidth += (*in_channels)[i]->bandwidth;
        energy_per_read += (*in_channels)[i]->energy_per_read;
        energy_per_write += (*in_channels)[i]->energy_per_write;
        energy_per_access += (*in_channels)[i]->energy_per_access;
    }
}

bob_conf* clone(bob_conf* origin)
{
    vector<channel_conf*> temp;
    for (int i = 0; i < MAX_NUM_CHANNELS_PER_BOB; ++i) {
        if ((origin->channels)[i] == 0) break;
        temp.push_back((origin->channels)[i]);
    }

    bob_conf* new_bob = new bob_conf(origin->memcad_params, &temp);
    return new_bob;
}

ostream& operator<<(ostream& os, const bob_conf& bob_cnf)
{
    os << " "
       << "BoB       ";
    os << "cap: " << bob_cnf.capacity << " GB ";
    os << "num_channels: " << bob_cnf.num_channels << " ";
    os << "bw: " << bob_cnf.bandwidth << " (MHz) ";
    os << "cost: $" << bob_cnf.cost << " ";
    os << "energy: " << bob_cnf.energy_per_access << " (nJ) ";
    os << endl;
    os << "   "
       << " ==============" << endl;
    for (int i = 0; i < bob_cnf.num_channels; i++) {
        channel_conf* temp = bob_cnf.channels[i];
        os << "    (" << i << ") " << (*temp) << endl;
    }
    os << "   "
       << " ==============" << endl;
    return os;
}
