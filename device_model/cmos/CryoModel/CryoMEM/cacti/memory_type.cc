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
#include <cmath>
#include <cassert>

#include "memory_type.h"
#include "io.h"
#include "input_parameter.h"
#include "basic_circuit.h"

using namespace std;

// cell_type --> sram(0),cam(1),dram(2)
void MemoryType::assign(const string& in_file, int tech_flavor, int cell_type)
{
    FILE* fp = fopen(in_file.c_str(), "r");
    char  line[5000];
    // char temp_var[5000];

    // double temp;
    // unsigned int thermal_temp;

    double vdd_cell, vdd;

    if (!fp) {
        cout << in_file << " is missing!\n";
        exit(-1);
    }
    while (fscanf(fp, "%[^\n]\n", line) != EOF) {
        if (!strncmp("-Vdd", line, strlen("-Vdd"))) {
            vdd = scan_five_input_double(line, "-Vdd", "V", tech_flavor, g_ip->print_detail_debug);
            continue;
        }
        if (!strncmp("-vdd_cell", line, strlen("-vdd_cell"))) {
            scan_five_input_double_mem_type(line, "-vdd_cell", "V", tech_flavor, cell_type, g_ip->print_detail_debug, vdd_cell);
            continue;
        }
        if (!strncmp("-Wmemcella", line, strlen("-Wmemcella"))) {
            scan_five_input_double_mem_type(line, "-Wmemcella", "V", tech_flavor, cell_type, g_ip->print_detail_debug, cell_a_w);
            continue;
        }
        if (!strncmp("-Wmemcellpmos", line, strlen("-Wmemcellpmos"))) {
            scan_five_input_double_mem_type(line, "-Wmemcellpmos", "V", tech_flavor, cell_type, g_ip->print_detail_debug, cell_pmos_w);
            continue;
        }
        if (!strncmp("-Wmemcellnmos", line, strlen("-Wmemcellnmos"))) {
            scan_five_input_double_mem_type(line, "-Wmemcellnmos", "V", tech_flavor, cell_type, g_ip->print_detail_debug, cell_nmos_w);
            continue;
        }
        if (!strncmp("-area_cell", line, strlen("-area_cell"))) {
            scan_five_input_double_mem_type(line, "-area_cell", "V", tech_flavor, cell_type, g_ip->print_detail_debug, area_cell);
            continue;
        }
        if (!strncmp("-asp_ratio_cell", line, strlen("-asp_ratio_cell"))) {
            scan_five_input_double_mem_type(line, "-asp_ratio_cell", "V", tech_flavor, cell_type, g_ip->print_detail_debug, asp_ratio_cell);
            continue;
        }
    }

    if (g_ip->is_eDRAM) {
        // ref. A 3T Gain cell embedded DRAM utilizing~. Chris Kim.
        cell_a_w = 1.0; // read transistor (PR)
        cell_pmos_w = 1.0; // gate cell transistor (PS)
        cell_nmos_w = 1.0; // write transistor (PW)
        area_cell = 68;
        asp_ratio_cell = 1.667;
    }

    if (cell_type != 2) cell_a_w *= g_ip->F_sz_um;
    cell_pmos_w *= g_ip->F_sz_um;
    cell_nmos_w *= g_ip->F_sz_um;
    if (cell_type != 2) area_cell *= (g_ip->F_sz_um * g_ip->F_sz_um);
    /// assert(asp_ratio_cell!=0);
    b_w = sqrt(area_cell / (asp_ratio_cell));
    b_h = asp_ratio_cell * b_w;
    if (cell_type == 2)  // dram
        Vbitpre = vdd_cell;
    else  // sram or cam
        Vbitpre = vdd;

    Vbitfloating = Vbitpre * 0.7;

    // display(5);
}

void MemoryType::interpolate(double alpha, const MemoryType& mem1, const MemoryType& mem2)
{
    cell_a_w    = alpha * mem1.cell_a_w + (1 - alpha) * mem2.cell_a_w;
    cell_pmos_w = alpha * mem1.cell_pmos_w + (1 - alpha) * mem2.cell_pmos_w;
    cell_nmos_w = alpha * mem1.cell_nmos_w + (1 - alpha) * mem2.cell_nmos_w;

    area_cell      = alpha * mem1.area_cell + (1 - alpha) * mem2.area_cell;
    asp_ratio_cell = alpha * mem1.asp_ratio_cell + (1 - alpha) * mem2.asp_ratio_cell;

    Vbitpre      = mem2.Vbitpre;
    Vbitfloating = Vbitpre * 0.7;
    // updating dependant variables after scaling/interpolating
    /// assert(asp_ratio_cell!=0);
    b_w = sqrt(area_cell / (asp_ratio_cell));
    b_h = asp_ratio_cell * b_w;
    // display(10);
}

void /*TechnologyParameter::*/ MemoryType::display(uint32_t indent) const
{
    string indent_str(indent, ' ');

    cout << indent_str << "b_w         = " << setw(12) << b_w << " um" << endl;
    cout << indent_str << "b_h         = " << setw(12) << b_h << " um" << endl;
    cout << indent_str << "cell_a_w    = " << setw(12) << cell_a_w << " um" << endl;
    cout << indent_str << "cell_pmos_w = " << setw(12) << cell_pmos_w << " um" << endl;
    cout << indent_str << "cell_nmos_w = " << setw(12) << cell_nmos_w << " um" << endl;
    cout << indent_str << "Vbitpre     = " << setw(12) << Vbitpre << " V" << endl;
    cout << indent_str << "Vbitfloating= " << setw(12) << Vbitfloating << " V" << endl;
}

bool MemoryType::isEqual(const MemoryType& mem)
{
    if (!is_equal(b_w, mem.b_w)) {
        display(0);
        cout << "\n\n\n";
        mem.display(0);
        assert(false);
    }
    if (!is_equal(b_h, mem.b_h)) {
        display(0);
        cout << "\n\n\n";
        mem.display(0);
        assert(false);
    }
    if (!is_equal(cell_a_w, mem.cell_a_w)) {
        display(0);
        cout << "\n\n\n";
        mem.display(0);
        assert(false);
    }
    if (!is_equal(cell_pmos_w, mem.cell_pmos_w)) {
        display(0);
        cout << "\n\n\n";
        mem.display(0);
        assert(false);
    }
    if (!is_equal(cell_nmos_w, mem.cell_nmos_w)) {
        display(0);
        cout << "\n\n\n";
        mem.display(0);
        assert(false);
    }
    if (!is_equal(Vbitpre, mem.Vbitpre)) {
        display(0);
        cout << "\n\n\n";
        mem.display(0);
        assert(false);
    }
    /// if( !is_equal(Vbitfloating , mem.Vbitfloating)) {display(0); cout << "\n\n\n"; mem.display(0); assert(false);}

    // needed to calculate b_w b_h
    /// if( !is_equal(area_cell , mem.area_cell)) {display(0); assert(false);}
    /// if( !is_equal(asp_ratio_cell , mem.asp_ratio_cell)) {display(0); assert(false);}

    return true;
}
