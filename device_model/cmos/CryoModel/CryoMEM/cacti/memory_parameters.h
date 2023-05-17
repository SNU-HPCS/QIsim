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

#ifndef __MEMORY_PARAMETERS_H__
#define __MEMORY_PARAMETERS_H__

#include "enum/mem_io_type.h"

class MemoryParameters
{
   public:
    // Power Parameteres
    static double VDD[2][2][4];
    static double IDD0[2][4];
    static double IDD1[2][4];
    static double IDD2P0[2][4];
    static double IDD2P1[2][4];
    static double IDD2N[2][4];
    static double IDD3P[2][4];
    static double IDD3N[2][4];
    static double IDD4R[2][4];
    static double IDD4W[2][4];
    static double IDD5[2][4];

    static double io_energy_read[2][3][3][4];
    static double io_energy_write[2][3][3][4];

    // Timing Parameters
    static double T_RAS[2];
    static double T_RC[2];
    static double T_RP[2];
    static double T_RFC[2];
    static double T_REFI[2];

    // Bandwidth Parameters
    static int bandwidth_load[2][4];

    // Cost Parameters
    static double cost[2][3][5];

    // Functions
    MemoryParameters();

    int bw_index(Mem_IO_type type, int bandwidth);
};

#endif