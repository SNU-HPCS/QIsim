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

#ifndef __MEMORY_TYPE_H__
#define __MEMORY_TYPE_H__

#include <string>
#include <cstdint>

class MemoryType
{
   public:
    double b_w;
    double b_h;
    double cell_a_w;
    double cell_pmos_w;
    double cell_nmos_w;
    double Vbitpre;
    double Vbitfloating;  // voltage when floating bitline is supported

    // needed to calculate b_w b_h
    double area_cell;
    double asp_ratio_cell;

    MemoryType() { reset(); }
    void reset()
    {
        b_w          = 0;
        b_h          = 0;
        cell_a_w     = 0;
        cell_pmos_w  = 0;
        cell_nmos_w  = 0;
        Vbitpre      = 0;
        Vbitfloating = 0;
    }
    void assign(const std::string& in_file, int tech_flavor, int cell_type);  // sram(0),cam(1),dram(2)
    void interpolate(double alpha, const MemoryType& dev1, const MemoryType& dev2);
    void display(std::uint32_t indent = 0) const;
    bool isEqual(const MemoryType& mem);
};

#endif