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

#ifndef __INTERCONNECT_TYPE_H__
#define __INTERCONNECT_TYPE_H__

#include <string>

class CactiInput_TechnologyParameter_InterconnectType;

class InterconnectType
{
   public:
    double pitch;
    double R_per_um;
    double C_per_um;
    double horiz_dielectric_constant;
    double vert_dielectric_constant;
    double aspect_ratio;
    double miller_value;
    double ild_thickness;

    // auxilary parameters
    double wire_width;
    double wire_thickness;
    double wire_spacing;
    double barrier_thickness;
    double dishing_thickness;
    double alpha_scatter;
    double fringe_cap;

    InterconnectType() : pitch(0), R_per_um(0), C_per_um(0) { reset(); };
    void reset()
    {
        pitch                     = 0;
        R_per_um                  = 0;
        C_per_um                  = 0;
        horiz_dielectric_constant = 0;
        vert_dielectric_constant  = 0;
        aspect_ratio              = 0;
        miller_value              = 0;
        ild_thickness             = 0;

        // auxilary parameters
        wire_width        = 0;
        wire_thickness    = 0;
        wire_spacing      = 0;
        barrier_thickness = 0;
        dishing_thickness = 0;
        alpha_scatter     = 0;
        fringe_cap        = 0;
    }
    void assign(const std::string& in_file, int projection_type, int tech_flavor);
    void interpolate(double alpha, const InterconnectType& inter1, const InterconnectType& inter2);
    void overriding(const CactiInput_TechnologyParameter_InterconnectType &interconnect_type);
    void display(uint32_t indent = 0);
    bool isEqual(const InterconnectType& inter);
};

#endif
