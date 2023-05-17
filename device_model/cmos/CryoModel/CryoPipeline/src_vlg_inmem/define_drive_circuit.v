// `ifndef DEFINE_DRIVE_CIRCUIT_V
// `define DEFINE_DRIVE_CIRCUIT_V

// `define log2(n)   ((n) <= (1<<0) ? 0 : (n) <= (1<<1) ? 1 :\
//                    (n) <= (1<<2) ? 2 : (n) <= (1<<3) ? 3 :\
//                    (n) <= (1<<4) ? 4 : (n) <= (1<<5) ? 5 :\
//                    (n) <= (1<<6) ? 6 : (n) <= (1<<7) ? 7 :\
//                    (n) <= (1<<8) ? 8 : (n) <= (1<<9) ? 9 :\
//                    (n) <= (1<<10) ? 10 : (n) <= (1<<11) ? 11 :\
//                    (n) <= (1<<12) ? 12 : (n) <= (1<<13) ? 13 :\
//                    (n) <= (1<<14) ? 14 : (n) <= (1<<15) ? 15 :\
//                    (n) <= (1<<16) ? 16 : (n) <= (1<<17) ? 17 :\
//                    (n) <= (1<<18) ? 18 : (n) <= (1<<19) ? 19 :\
//                    (n) <= (1<<20) ? 20 : (n) <= (1<<21) ? 21 :\
//                    (n) <= (1<<22) ? 22 : (n) <= (1<<23) ? 23 :\
//                    (n) <= (1<<24) ? 24 : (n) <= (1<<25) ? 25 :\
//                    (n) <= (1<<26) ? 26 : (n) <= (1<<27) ? 27 :\
//                    (n) <= (1<<28) ? 28 : (n) <= (1<<29) ? 29 :\
//                    (n) <= (1<<30) ? 30 : (n) <= (1<<31) ? 31 : 32)
// `endif
`include "define.v"

`define DRIVE_NUM_BANK                    2
`define DRIVE_NUM_QUBIT_PER_BANK          16
`define DRIVE_QUBIT_ADDR_WIDTH_PER_BANK   4
`define DRIVE_IQ_OUT_WIDTH                9   // Usually IQ_OUT_WIDTH == IQ_CALI_WIDTH
`define DRIVE_IQ_SUM_WIDTH                (`DRIVE_IQ_OUT_WIDTH+`log2(`DRIVE_NUM_BANK))
// pc
`define DRIVE_PC_WIDTH                    `DRIVE_INST_LIST_ADDR_WIDTH  // Usually PC_WIDTH == INST_LIST_ADDR_WIDTH
// nco
`define DRIVE_NUM_NCO                     `DRIVE_NUM_QUBIT_PER_BANK
`define DRIVE_NCO_OUTPUT_WIDTH            `DRIVE_PHASE_WIDTH
`define DRIVE_NCO_ADDR_WIDTH              `DRIVE_QUBIT_ADDR_WIDTH_PER_BANK
`define DRIVE_NCO_N                       22
`define DRIVE_Z_CORR_WIDTH                12
// z_corr memory
`define DRIVE_Z_CORR_MEMORY_NUM_ENTRY     `DRIVE_NUM_QUBIT_PER_BANK
`define DRIVE_Z_CORR_MEMORY_ADDR_WIDTH    `DRIVE_QUBIT_ADDR_WIDTH_PER_BANK
`define DRIVE_Z_CORR_MEMORY_DATA_WIDTH    (`DRIVE_Z_CORR_WIDTH*`DRIVE_NUM_QUBIT_PER_BANK*`DRIVE_NUM_BANK)
// enve_memory
`define DRIVE_AMP_WIDTH                   8
`define DRIVE_PHASE_WIDTH                 10
`define DRIVE_ENVE_MEMORY_NUM_ENTRY       40960
`define DRIVE_ENVE_MEMORY_ADDR_WIDTH      16
`define DRIVE_ENVE_MEMORY_DATA_WIDTH      (`DRIVE_PHASE_WIDTH+`DRIVE_AMP_WIDTH)
// inst_table
`define DRIVE_AXIS_WIDTH                  2
`define DRIVE_INST_TABLE_NUM_ENTRY        8
`define DRIVE_INST_TABLE_ADDR_WIDTH       3 // INST_LIST_DATA_WIDTH - 5 (log2(32))
`define DRIVE_INST_TABLE_DATA_WIDTH       (`DRIVE_ENVE_MEMORY_ADDR_WIDTH*2+`DRIVE_AXIS_WIDTH)
// inst_list
`define DRIVE_INST_LIST_NUM_ENTRY         2048
`define DRIVE_INST_LIST_ADDR_WIDTH        11
`define DRIVE_INST_LIST_DATA_WIDTH        (`DRIVE_QUBIT_ADDR_WIDTH_PER_BANK+1+`DRIVE_Z_CORR_WIDTH) // qubit_sel, z_corr_mode, phase_imm
// cali_memory
`define DRIVE_IQ_CALI_WIDTH               `DRIVE_IQ_OUT_WIDTH
`define DRIVE_CALI_MEMORY_NUM_ENTRY       `DRIVE_NUM_QUBIT_PER_BANK
`define DRIVE_CALI_MEMORY_ADDR_WIDTH      `DRIVE_QUBIT_ADDR_WIDTH_PER_BANK
`define DRIVE_CALI_MEMORY_DATA_WIDTH      (4*`DRIVE_IQ_CALI_WIDTH)
// sinusoidal lut
`define DRIVE_SIN_LUT_NUM_ENTRY           1024
`define DRIVE_SIN_LUT_ADDR_WIDTH          `DRIVE_PHASE_WIDTH
`define DRIVE_SIN_LUT_DATA_WIDTH          `DRIVE_AMP_WIDTH

