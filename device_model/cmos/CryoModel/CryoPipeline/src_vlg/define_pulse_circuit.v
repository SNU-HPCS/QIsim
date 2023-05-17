// `ifndef DEFINE_PULSE_CIRCUIT_V
// `define DEFINE_PULSE_CIRCUIT_V


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

// `define INCLUDE_MEMORY_IN_MODULE

`define PULSE_NUM_QUBIT                 1
// `define PULSE_NUM_QUBIT                 32
// `define PULSE_NUM_QUBIT                 1152

`define PULSE_GLB_COUNTER_WIDTH         24
`define PULSE_QUBIT_ADDR_WIDTH          (`log2(`PULSE_NUM_QUBIT))
`define PULSE_MASK_WIDTH                3
`define PULSE_DIRECTION_WIDTH           (`PULSE_MASK_WIDTH-1)

`define PULSE_AMP_WIDTH                 12
`define PULSE_LENGTH_WIDTH              7

`define PULSE_AMP_MEMORY_NUM_ENTRY      512
`define PULSE_AMP_MEMORY_ADDR_WIDTH     (`log2(`PULSE_AMP_MEMORY_NUM_ENTRY))
`define PULSE_AMP_MEMORY_DATA_WIDTH     (`PULSE_AMP_WIDTH+`PULSE_LENGTH_WIDTH)

`define PULSE_INST_LIST_NUM_ENTRY       32
`define PULSE_INST_LIST_ADDR_WIDTH      (`log2(`PULSE_INST_LIST_NUM_ENTRY))
`define PULSE_INST_LIST_DATA_WIDTH      (`PULSE_GLB_COUNTER_WIDTH+`PULSE_DIRECTION_WIDTH)
`define PULSE_PC_WIDTH                  (`PULSE_INST_LIST_ADDR_WIDTH)