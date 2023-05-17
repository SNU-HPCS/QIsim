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

#ifndef __POWER_COMPONENTS_H__
#define __POWER_COMPONENTS_H__

#include <boost/archive/text_oarchive.hpp>
#include <boost/archive/text_iarchive.hpp>

class powerComponents
{
   public:
    double dynamic;
    double leakage;
    double gate_leakage;
    double short_circuit;
    double longer_channel_leakage;

    powerComponents() : dynamic(0), leakage(0), gate_leakage(0), short_circuit(0), longer_channel_leakage(0) {}
    powerComponents(const powerComponents &obj) { *this = obj; }
    powerComponents &operator=(const powerComponents &rhs)
    {
        dynamic                = rhs.dynamic;
        leakage                = rhs.leakage;
        gate_leakage           = rhs.gate_leakage;
        short_circuit          = rhs.short_circuit;
        longer_channel_leakage = rhs.longer_channel_leakage;
        return *this;
    }
    void reset()
    {
        dynamic                = 0;
        leakage                = 0;
        gate_leakage           = 0;
        short_circuit          = 0;
        longer_channel_leakage = 0;
    }

    friend powerComponents operator+(const powerComponents &x, const powerComponents &y);
    friend powerComponents operator*(const powerComponents &x, double const *const y);

    //GH
   private:
    friend class boost::serialization::access;

    template<typename Archive>
    void serialize(Archive &ar, const unsigned int version){
        ar & dynamic;
        ar & leakage;
        ar & gate_leakage;
        ar & short_circuit;
        ar & longer_channel_leakage;
    }
};

#endif
