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

#include "power_components.h"

powerComponents operator+(const powerComponents &x, const powerComponents &y)
{
    powerComponents z;

    z.dynamic                = x.dynamic + y.dynamic;
    z.leakage                = x.leakage + y.leakage;
    z.gate_leakage           = x.gate_leakage + y.gate_leakage;
    z.short_circuit          = x.short_circuit + y.short_circuit;
    z.longer_channel_leakage = x.longer_channel_leakage + y.longer_channel_leakage;

    return z;
}

powerComponents operator*(const powerComponents &x, double const *const y)
{
    powerComponents z;

    z.dynamic                = x.dynamic * y[0];
    z.leakage                = x.leakage * y[1];
    z.gate_leakage           = x.gate_leakage * y[2];
    z.short_circuit          = x.short_circuit * y[3];
    z.longer_channel_leakage = x.longer_channel_leakage * y[1];  // longer channel leakage has the same behavior as normal leakage

    return z;
}
