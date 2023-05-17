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
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.”
 *
 ***************************************************************************/

#ifndef __IO_H__
#define __IO_H__

#include <string>

class uca_org_t;

double scan_single_input_double(char* line, const char* name, const char* unit_name, bool print);
double scan_five_input_double(char* line, const char* name, const char* unit_name, int flavor, bool print);
void scan_five_input_double_temperature(char* line, const char* name, const char* unit_name, int flavor, unsigned int temperature, bool print, double& result);
double scan_input_double_inter_type(char* line, const char* name, const char* unit_name, int proj_type, int tech_flavor, bool print);
void scan_five_input_double_mem_type(char* line, const char* name, const char* unit_name, int flavor, int cell_type, bool print, double& result);
double scan_input_double_tsv_type(char* line, const char* name, const char* unit_name, int proj_type, int tsv_type, bool print);

void output_data_csv(const uca_org_t& fin_res, std::string fn = "out.csv");
void output_UCA(uca_org_t* fin_res);
void output_data_csv_3dd(const uca_org_t& fin_res);

#endif
