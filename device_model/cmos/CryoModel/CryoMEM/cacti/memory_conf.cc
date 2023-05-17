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

#include <vector>
#include <cassert>

#include "memory_conf.h"
#include "bob_conf.h"

using namespace std;

memory_conf::memory_conf(MemCadParameters* memcad_params, vector<bob_conf*>* in_bobs)
    : memcad_params(memcad_params),
      num_bobs(0),
      capacity(0),
      bandwidth(0),
      energy_per_read(0),
      energy_per_write(0),
      energy_per_access(0),
      cost(0),
      latency(0),
      valid(true)
{
    assert(in_bobs->size() <= MAX_NUM_BOBS);
    for (int i = 0; i < MAX_NUM_BOBS; i++) bobs[i] = 0;

    for (unsigned int i = 0; i < in_bobs->size(); ++i) {
        bobs[i] = (*in_bobs)[i];
        num_bobs++;
        capacity += (*in_bobs)[i]->capacity;
        cost += (*in_bobs)[i]->cost;
        bandwidth += (*in_bobs)[i]->bandwidth;
        energy_per_read += (*in_bobs)[i]->energy_per_read;
        energy_per_write += (*in_bobs)[i]->energy_per_write;
        energy_per_access += (*in_bobs)[i]->energy_per_access;
    }
}

ostream& operator<<(ostream& os, const memory_conf& mem_cnf)
{
    os << "Memory    ";
    os << "cap: " << mem_cnf.capacity << " GB ";
    os << "num_bobs: " << mem_cnf.num_bobs << " ";
    os << "bw: " << mem_cnf.bandwidth << " (MHz) ";
    os << "cost: $" << mem_cnf.cost << " ";
    os << "energy: " << mem_cnf.energy_per_access << " (nJ) ";
    os << endl;
    os << " {" << endl;
    for (int i = 0; i < mem_cnf.num_bobs; i++) {
        bob_conf* temp = mem_cnf.bobs[i];
        os << " (" << i << ") " << (*temp) << endl;
    }
    os << " }" << endl;
    return os;
}
