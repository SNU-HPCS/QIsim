// `ifndef DEFINE_READOUT_TX_CIRCUIT_V
// `define DEFINE_READOUT_TX_CIRCUIT_V


// /*** CONSTANT or DEPENDENT_VARS ***/
// // Arithmetic
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

`define READTX_NUM_QUBIT                   8
`define READTX_QUBIT_ADDR_WIDTH            3
`define READTX_GLB_COUNTER_WIDTH           24
// pc
`define READTX_PC_WIDTH                    `READTX_INST_LIST_ADDR_WIDTH // PC_WIDTH == INST_LIST_ADDR_WIDTH

// inst_list
`define READTX_SIGNAL_LENGTH_WIDTH         20

`define READTX_INST_LIST_NUM_ENTRY         32 // ** not specified in the paper
`define READTX_INST_LIST_ADDR_WIDTH        5
`define READTX_INST_LIST_DATA_WIDTH        (`READTX_GLB_COUNTER_WIDTH+`READTX_SIGNAL_LENGTH_WIDTH+`READTX_NUM_QUBIT) 

// readout_tx_signal_gen_unit
`define READTX_NCO_N                       22
`define READTX_PHASE_WIDTH                 10

`define READTX_SIN_LUT_NUM_ENTRY           1024
`define READTX_SIN_LUT_ADDR_WIDTH          `READTX_PHASE_WIDTH
// `define READTX_SIN_LUT_DATA_WIDTH          16
`define READTX_SIN_LUT_DATA_WIDTH          8

// output
`define READTX_OUTPUT_WIDTH                (`READTX_SIN_LUT_DATA_WIDTH+`READTX_QUBIT_ADDR_WIDTH)
