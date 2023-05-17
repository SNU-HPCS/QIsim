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

#include "interconnect_type.h"
#include "cacti_interface.pb.h"
#include "input_parameter.h"
#include "io.h"
#include "wire.h"
#include "basic_circuit.h"

using namespace std;

void InterconnectType::assign(const string& in_file, int projection_type, int tech_flavor)
{
    FILE* fp = fopen(in_file.c_str(), "r");
    char  line[5000];
    // char temp_var[5000];

    // double temp[5];
    // unsigned int thermal_temp;

    // double nmos_effective_resistance_multiplier;

    double resistivity;

    if (!fp) {
        cout << in_file << " is missing!\n";
        exit(-1);
    }

    bool print = g_ip->print_detail_debug;

    while (fscanf(fp, "%[^\n]\n", line) != EOF) {
        if (!strncmp("-wire_pitch", line, strlen("-wire_pitch"))) {
            pitch = scan_input_double_inter_type(line, "-wire_pitch", "um", g_ip->ic_proj_type, tech_flavor, print);
            continue;
        }
        if (!strncmp("-barrier_thickness", line, strlen("-barrier_thickness"))) {
            barrier_thickness = scan_input_double_inter_type(line, "-barrier_thickness", "ohm", g_ip->ic_proj_type, tech_flavor, print);
            continue;
        }
        if (!strncmp("-dishing_thickness", line, strlen("-dishing_thickness"))) {
            dishing_thickness = scan_input_double_inter_type(line, "-dishing_thickness", "um", g_ip->ic_proj_type, tech_flavor, print);
            continue;
        }
        if (!strncmp("-alpha_scatter", line, strlen("-alpha_scatter"))) {
            alpha_scatter = scan_input_double_inter_type(line, "-alpha_scatter", "um", g_ip->ic_proj_type, tech_flavor, print);
            continue;
        }
        if (!strncmp("-aspect_ratio", line, strlen("-aspect_ratio"))) {
            aspect_ratio = scan_input_double_inter_type(line, "-aspect_ratio", "um", g_ip->ic_proj_type, tech_flavor, print);
            continue;
        }
        if (!strncmp("-miller_value", line, strlen("-miller_value"))) {
            miller_value = scan_input_double_inter_type(line, "-miller_value", "um", g_ip->ic_proj_type, tech_flavor, print);
            continue;
        }
        if (!strncmp("-horiz_dielectric_constant", line, strlen("-horiz_dielectric_constant"))) {
            horiz_dielectric_constant = scan_input_double_inter_type(line, "-horiz_dielectric_constant", "um", g_ip->ic_proj_type, tech_flavor, print);
            continue;
        }
        if (!strncmp("-vert_dielectric_constant", line, strlen("-vert_dielectric_constant"))) {
            vert_dielectric_constant = scan_input_double_inter_type(line, "-vert_dielectric_constant", "um", g_ip->ic_proj_type, tech_flavor, print);
            continue;
        }
        if (!strncmp("-ild_thickness", line, strlen("-ild_thickness"))) {
            ild_thickness = scan_input_double_inter_type(line, "-ild_thickness", "um", g_ip->ic_proj_type, tech_flavor, print);
            continue;
        }
        if (!strncmp("-fringe_cap", line, strlen("-fringe_cap"))) {
            fringe_cap = scan_input_double_inter_type(line, "-fringe_cap", "um", g_ip->ic_proj_type, tech_flavor, print);
            continue;
        }
        if (!strncmp("-wire_r_per_micron", line, strlen("-wire_r_per_micron"))) {
            R_per_um = scan_input_double_inter_type(line, "-wire_r_per_micron", "um", g_ip->ic_proj_type, tech_flavor, print);
            continue;
        }
        if (!strncmp("-wire_c_per_micron", line, strlen("-wire_c_per_micron"))) {
            C_per_um = scan_input_double_inter_type(line, "-wire_c_per_micron", "um", g_ip->ic_proj_type, tech_flavor, print);
            continue;
        }
        if (!strncmp("-resistivity", line, strlen("-resistivity"))) {
            resistivity = scan_input_double_inter_type(line, "-resistivity", "um", g_ip->ic_proj_type, tech_flavor, print);
            continue;
        }
    }

    pitch *= g_ip->F_sz_um;
    wire_width     = pitch / 2;                  // micron
    wire_thickness = aspect_ratio * wire_width;  // micron
    wire_spacing   = pitch - wire_width;         // micron
    if ((projection_type != 1) || (tech_flavor != 3)) {
        R_per_um = wire_resistance(resistivity, wire_width, wire_thickness, barrier_thickness, dishing_thickness, alpha_scatter);  // ohm/micron
        if (print)
            cout << R_per_um << " = wire_resistance(" << resistivity << "," << wire_width << "," << wire_thickness << "," << barrier_thickness << ","
                 << dishing_thickness << "," << alpha_scatter << ")\n";

        C_per_um = wire_capacitance(
            wire_width,
            wire_thickness,
            wire_spacing,
            ild_thickness,
            miller_value,
            horiz_dielectric_constant,
            vert_dielectric_constant,
            fringe_cap);  // F/micron.
        if (print)
            cout << C_per_um << " = wire_capacitance(" << wire_width << "," << wire_thickness << "," << wire_spacing << "," << ild_thickness << ","
                 << miller_value << "," << horiz_dielectric_constant << "," << vert_dielectric_constant << "," << fringe_cap << ")\n";
    }
    fclose(fp);
}

void InterconnectType::interpolate(double alpha, const InterconnectType& inter1, const InterconnectType& inter2)
{
    pitch                     = alpha * inter1.pitch + (1 - alpha) * inter2.pitch;
    R_per_um                  = alpha * inter1.R_per_um + (1 - alpha) * inter2.R_per_um;
    C_per_um                  = alpha * inter1.C_per_um + (1 - alpha) * inter2.C_per_um;
    horiz_dielectric_constant = alpha * inter1.horiz_dielectric_constant + (1 - alpha) * inter2.horiz_dielectric_constant;
    vert_dielectric_constant  = alpha * inter1.vert_dielectric_constant + (1 - alpha) * inter2.vert_dielectric_constant;
    aspect_ratio              = alpha * inter1.aspect_ratio + (1 - alpha) * inter2.aspect_ratio;
    miller_value              = alpha * inter1.miller_value + (1 - alpha) * inter2.miller_value;
    ild_thickness             = alpha * inter1.ild_thickness + (1 - alpha) * inter2.ild_thickness;
}

void InterconnectType::overriding(const CactiInput::TechnologyParameter::InterconnectType &interconnect_type){
    if (interconnect_type.has_r_per_um())      R_per_um  = interconnect_type.r_per_um();
    if (interconnect_type.has_r_per_um_mult()) R_per_um *= interconnect_type.r_per_um_mult();
}

void /*TechnologyParameter::*/ InterconnectType::display(uint32_t indent)
{
    string indent_str(indent, ' ');

    cout << indent_str << "pitch    = " << setw(12) << pitch << " um" << endl;
    cout << indent_str << "R_per_um = " << setw(12) << R_per_um << " ohm/um" << endl;
    cout << indent_str << "C_per_um = " << setw(12) << C_per_um << " F/um" << endl;

    cout << indent_str << "horiz_dielectric_constant = " << setw(12) << horiz_dielectric_constant << " F/um" << endl;
    cout << indent_str << "vert_dielectric_constant = " << setw(12) << vert_dielectric_constant << " F/um" << endl;
    cout << indent_str << "aspect_ratio = " << setw(12) << aspect_ratio << " F/um" << endl;
    cout << indent_str << "miller_value = " << setw(12) << miller_value << " F/um" << endl;
    cout << indent_str << "ild_thickness = " << setw(12) << ild_thickness << " F/um" << endl;

    cout << indent_str << "wire_width       = " << setw(12) << wire_width << " um" << endl;
    cout << indent_str << "wire_thickness   = " << setw(12) << wire_thickness << " um" << endl;
    cout << indent_str << "wire_spacing     = " << setw(12) << wire_spacing << " um" << endl;
    cout << indent_str << "barrier_thickness= " << setw(12) << barrier_thickness << " um" << endl;
    cout << indent_str << "dishing_thickness= " << setw(12) << dishing_thickness << " um" << endl;
    cout << indent_str << "alpha_scatter    = " << setw(12) << alpha_scatter << " um" << endl;
    cout << indent_str << "fringe_cap       = " << setw(12) << fringe_cap << " um" << endl;
}

bool InterconnectType::isEqual(const InterconnectType& inter)
{
    if (!is_equal(pitch, inter.pitch)) {
        display(0);
        assert(false);
    }
    if (!is_equal(R_per_um, inter.R_per_um)) {
        display(0);
        assert(false);
    }
    if (!is_equal(C_per_um, inter.C_per_um)) {
        display(0);
        assert(false);
    }
    if (!is_equal(horiz_dielectric_constant, inter.horiz_dielectric_constant)) {
        display(0);
        assert(false);
    }
    if (!is_equal(vert_dielectric_constant, inter.vert_dielectric_constant)) {
        display(0);
        assert(false);
    }
    if (!is_equal(aspect_ratio, inter.aspect_ratio)) {
        display(0);
        assert(false);
    }
    if (!is_equal(miller_value, inter.miller_value)) {
        display(0);
        assert(false);
    }
    if (!is_equal(ild_thickness, inter.ild_thickness)) {
        display(0);
        assert(false);
    }

    // auxilary parameters
    /// if(  !is_equal(wire_width , inter.wire_width)) {display(0); assert(false);}
    /// if(  !is_equal(wire_thickness , inter.wire_thickness)) {display(0); assert(false);}
    /// if(  !is_equal(wire_spacing , inter.wire_spacing)) {display(0); assert(false);}
    /// if(  !is_equal(barrier_thickness , inter.barrier_thickness)) {display(0); assert(false);}
    /// if(  !is_equal(dishing_thickness , inter.dishing_thickness)) {display(0); assert(false);}
    /// if(  !is_equal(alpha_scatter , inter.alpha_scatter)) {display(0); assert(false);}
    /// if(  !is_equal(fringe_cap , inter.fringe_cap)) {display(0); assert(false);}

    return true;
}
