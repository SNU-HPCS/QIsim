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

#include "mem_array.h"

bool mem_array::lt::operator()(const mem_array *m1, const mem_array *m2) const noexcept{
    if (m1->Nspd < m2->Nspd)
        return true;
    else if (m1->Nspd > m2->Nspd)
        return false;
    else if (m1->Ndwl < m2->Ndwl)
        return true;
    else if (m1->Ndwl > m2->Ndwl)
        return false;
    else if (m1->Ndbl < m2->Ndbl)
        return true;
    else if (m1->Ndbl > m2->Ndbl)
        return false;
    else if (m1->deg_bl_muxing < m2->deg_bl_muxing)
        return true;
    else if (m1->deg_bl_muxing > m2->deg_bl_muxing)
        return false;
    else if (m1->Ndsam_lev_1 < m2->Ndsam_lev_1)
        return true;
    else if (m1->Ndsam_lev_1 > m2->Ndsam_lev_1)
        return false;
    else if (m1->Ndsam_lev_2 < m2->Ndsam_lev_2)
        return true;
    else
        return false;
}
