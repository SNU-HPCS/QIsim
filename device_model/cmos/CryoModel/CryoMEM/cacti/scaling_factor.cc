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
#include <iomanip>
#include <string>
#include <cstring>
#include <cassert>

#include "scaling_factor.h"
#include "basic_circuit.h"
#include "input_parameter.h"
#include "io.h"

using namespace std;

void ScalingFactor::assign(const string& in_file)
{
    FILE* fp = fopen(in_file.c_str(), "r");
    char  line[5000];
    // char temp_var[5000];
    if (!fp) {
        cout << in_file << " is missing!\n";
        exit(-1);
    }

    while (fscanf(fp, "%[^\n]\n", line) != EOF) {
        if (!strncmp("-logic_scaling_co_eff", line, strlen("-logic_scaling_co_eff"))) {
            logic_scaling_co_eff = scan_single_input_double(line, "-logic_scaling_co_eff", "F/um", g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-core_tx_density", line, strlen("-core_tx_density"))) {
            core_tx_density = scan_single_input_double(line, "-core_tx_density", "F/um", g_ip->print_detail_debug);
            continue;
        }
    }

    fclose(fp);
}

void ScalingFactor::interpolate(double alpha, const ScalingFactor& dev1, const ScalingFactor& dev2)
{
    logic_scaling_co_eff = alpha * dev1.logic_scaling_co_eff + (1 - alpha) * dev2.logic_scaling_co_eff;
    core_tx_density      = alpha * dev1.core_tx_density + (1 - alpha) * dev2.core_tx_density;
}

void /*TechnologyParameter::*/ ScalingFactor::display(uint32_t indent)
{
    string indent_str(indent, ' ');

    cout << indent_str << "logic_scaling_co_eff    = " << setw(12) << logic_scaling_co_eff << endl;
    cout << indent_str << "curr_core_tx_density = " << setw(12) << core_tx_density << " # of tx/um^2" << endl;
    cout << indent_str << "long_channel_leakage_reduction = " << setw(12) << long_channel_leakage_reduction << " # of tx/um^2" << endl;
}

bool ScalingFactor::isEqual(const ScalingFactor& scal)
{
    if (!is_equal(logic_scaling_co_eff, scal.logic_scaling_co_eff)) {
        display(0);
        assert(false);
    }
    if (!is_equal(core_tx_density, scal.core_tx_density)) {
        display(0);
        assert(false);
    }
    if (!is_equal(long_channel_leakage_reduction, scal.long_channel_leakage_reduction)) {
        display(0);
        assert(false);
    }
    return true;
}
