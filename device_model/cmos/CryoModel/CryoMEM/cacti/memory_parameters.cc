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

#include "memory_parameters.h"
#include "const.h"

double MemoryParameters::VDD[2][2][4] =  //[lp:hp][ddr3:ddr4][frequency index]
    {{{1.5, 1.5, 1.5, 1.5}, {1.2, 1.2, 1.2, 1.2}}, {{1.35, 1.35, 1.35, 1.35}, {1.0, 1.0, 1.0, 1.0}}};

double MemoryParameters::IDD0[2][4] = {{55, 60, 65, 75}, {58, 58, 60, 64}};

double MemoryParameters::IDD2P0[2][4] = {{20, 20, 20, 20}, {20, 20, 20, 20}};

double MemoryParameters::IDD2P1[2][4] = {{30, 30, 32, 37}, {30, 30, 30, 32}};

double MemoryParameters::IDD2N[2][4] = {{40, 42, 45, 50}, {44, 44, 46, 50}};

double MemoryParameters::IDD3P[2][4] = {{45, 50, 55, 60}, {44, 44, 44, 44}};

double MemoryParameters::IDD3N[2][4] = {{42, 47, 52, 57}, {44, 44, 44, 44}};

double MemoryParameters::IDD4R[2][4] = {{120, 135, 155, 175}, {140, 140, 150, 160}};

double MemoryParameters::IDD4W[2][4] = {{100, 125, 145, 165}, {156, 156, 176, 196}};

double MemoryParameters::IDD5[2][4] = {{150, 205, 210, 220}, {190, 190, 190, 192}};

double MemoryParameters::io_energy_read[2][3][3][4] =  // [ddr3:ddr4][udimm:rdimm:lrdimm][load 1:2:3][frequency 0:1:2:3]
    {{                                                 // ddr3
      {                                                // udimm
       {2592.33, 2593.33, 3288.784, 4348.612},
       {2638.23, 2640.23, 3941.584, 5415.492},
       {2978.659, 2981.659, 4816.644, 6964.162}

      },
      {// rdimm
       {2592.33, 3087.071, 3865.044, 4844.982},
       {2932.759, 3733.318, 4237.634, 5415.492},
       {3572.509, 4603.109, 5300.004, 6964.162}},
      {// lrdimm
       {4628.966, 6357.625, 7079.348, 9680.454},
       {5368.26, 6418.788, 7428.058, 10057.164},
       {5708.689, 7065.038, 7808.678, 10627.674}

      }

     },
     { // ddr
      {// udimm
       {2135.906, 2633.317, 2750.919, 2869.406},
       {2458.714, 2695.791, 2822.298, 3211.111},
       {2622.85, 3030.048, 3160.265, 3534.448}

      },
      {// rdimm
       {2135.906, 2633.317, 2750.919, 2869.406},
       {2458.714, 2695.791, 3088.886, 3211.111},
       {2622.85, 3030.048, 3312.468, 3758.445}

      },
      {// lrdimm
       {4226.903, 5015.342, 5490.61, 5979.864},
       {4280.471, 5319.132, 5668.945, 6060.216},
       {4603.279, 5381.605, 5740.325, 6401.926}

      }

     }};

double MemoryParameters::io_energy_write[2][3][3][4] = {{ // ddr3
                                                         {// udimm
                                                          {2758.951, 2984.854, 3571.804, 4838.902},
                                                          {2804.851, 3768.524, 4352.214, 5580.362},
                                                          {3213.897, 3829.684, 5425.854, 6933.512}

                                                         },
                                                         {// rdimm
                                                          {2758.951, 3346.104, 3931.154, 4838.902},
                                                          {3167.997, 4114.754, 4696.724, 5580.362},
                                                          {3561.831, 3829.684, 6039.994, 8075.542}

                                                         },
                                                         {// lrdimm
                                                          {4872.238, 5374.314, 7013.868, 9267.574},
                                                          {5701.502, 6214.348, 7449.758, 10045.004},
                                                          {5747.402, 6998.018, 8230.168, 10786.464}

                                                         }

                                                        },
                                                        { // ddr4
                                                         {// udimm
                                                          {2525.129, 2840.853, 2979.037, 3293.608},
                                                          {2933.756, 3080.126, 3226.497, 3979.698},
                                                          {3293.964, 3753.37, 3906.137, 4312.448}

                                                         },
                                                         {// rdimm
                                                          {2525.129, 2840.853, 3155.117, 3293.608},
                                                          {2933.756, 3080.126, 3834.757, 3979.698},
                                                          {3293.964, 3753.37, 4413.037, 5358.078}

                                                         },
                                                         {// lrdimm
                                                          {4816.453, 5692.314, 5996.134, 6652.936},
                                                          {4870.021, 5754.788, 6067.514, 6908.636},
                                                          {5298.373, 5994.07, 6491.054, 7594.726}

                                                         }

                                                        }};

double MemoryParameters::T_RAS[2] = {35, 35};

double MemoryParameters::T_RC[2] = {47.5, 47.5};

double MemoryParameters::T_RP[2] = {13, 13};

double MemoryParameters::T_RFC[2] = {340, 260};

double MemoryParameters::T_REFI[2] = {7800, 7800};

int MemoryParameters::bandwidth_load[2][4] = {{400, 533, 667, 800}, {800, 933, 1066, 1200}};

double MemoryParameters::cost[2][3][5] = {{{40.38, 76.13, INF, INF, INF}, {42.24, 64.17, 122.6, 304.3, INF}, {INF, INF, 211.3, 287.5, 1079.5}},
                                          {{25.99, 45.99, INF, INF, INF}, {32.99, 60.45, 126, 296.3, INF}, {INF, INF, 278.99, 333, 1474}}};
