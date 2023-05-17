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

#ifndef __DEVICE_TYPE_H__
#define __DEVICE_TYPE_H__

#include <cstdint>
#include <string>

class CactiInput_TechnologyParameter_DeviceType;

class DeviceType
{
   public:
    double C_g_ideal;
    double C_fringe;
    double C_overlap;
    double C_junc;  // C_junc_area
    double C_junc_sidewall;
    double l_phy;
    double l_elec;
    double R_nch_on;
    double R_pch_on;
    double Vdd;
    double Vth;
    double Vcc_min;  // allowed min vcc; for memory cell it is the lowest vcc for data retention. for logic it is the vcc to balance the leakage reduction and
                     // wakeup latency
    double I_on_n;
    double I_on_p;
    double I_off_n;
    double I_off_p;
    double I_g_on_n;
    double I_g_on_p;
    double C_ox;
    double t_ox;
    double n_to_p_eff_curr_drv_ratio;
    double long_channel_leakage_reduction;
    double Mobility_n;

    // auxilary parameters
    double Vdsat;
    double gmp_to_gmn_multiplier;

    DeviceType()
        : C_g_ideal(0),
          C_fringe(0),
          C_overlap(0),
          C_junc(0),
          C_junc_sidewall(0),
          l_phy(0),
          l_elec(0),
          R_nch_on(0),
          R_pch_on(0),
          Vdd(0),
          Vth(0),
          Vcc_min(0),
          I_on_n(0),
          I_on_p(0),
          I_off_n(0),
          I_off_p(0),
          I_g_on_n(0),
          I_g_on_p(0),
          C_ox(0),
          t_ox(0),
          n_to_p_eff_curr_drv_ratio(0),
          long_channel_leakage_reduction(0),
          Mobility_n(0)
    {
        reset();
    };

    void assign(const std::string& in_file, int tech_flavor, unsigned int temp);
    void interpolate(double alpha, const DeviceType& dev1, const DeviceType& dev2);
    void overriding(const CactiInput_TechnologyParameter_DeviceType &device_type);
    void reset()
    {
        C_g_ideal       = 0;
        C_fringe        = 0;
        C_overlap       = 0;
        C_junc          = 0;  // C_junc_area
        C_junc_sidewall = 0;
        l_phy           = 0;
        l_elec          = 0;
        R_nch_on        = 0;
        R_pch_on        = 0;
        Vdd             = 0;
        Vth             = 0;
        Vcc_min = 0;  // allowed min vcc, for memory cell it is the lowest vcc for data retention. for logic it is the vcc to balance the leakage reduction and
                      // wakeup latency
        I_on_n                         = 0;
        I_on_p                         = 0;
        I_off_n                        = 0;
        I_off_p                        = 0;
        I_g_on_n                       = 0;
        I_g_on_p                       = 0;
        C_ox                           = 0;
        t_ox                           = 0;
        n_to_p_eff_curr_drv_ratio      = 0;
        long_channel_leakage_reduction = 0;
        Mobility_n                     = 0;

        // auxilary parameters
        Vdsat                 = 0;
        gmp_to_gmn_multiplier = 0;
    }

    void display(std::uint32_t indent = 0) const;
    bool isEqual(const DeviceType& dev);
};

#endif
