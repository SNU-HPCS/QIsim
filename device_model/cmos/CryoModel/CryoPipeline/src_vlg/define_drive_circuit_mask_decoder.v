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

//////////////////////////////////

// multiplexing: 32
/*
`define DRIVE_START_TIME_WIDTH 24
`define DRIVE_BS_SELECT_WIDTH 3
`define DRIVE_NUM_GROUP 36

`define DRIVE_NUM_QUBIT_PER_GROUP 32
`define DRIVE_NUM_QUBIT_PER_BANK 16
`define DRIVE_NUM_BANK_PER_GROUP 2
`define DRIVE_BANK_ADDR_WIDTH_PER_GROUP 1

`define DRIVE_NUM_TOTAL_QUBIT (`DRIVE_NUM_GROUP*`DRIVE_NUM_QUBIT_PER_GROUP)

`define DRIVE_Z_PHASE_WIDTH 12
`define DRIVE_NUM_PHASE 8

`define DRIVE_CONST_PHASE_0    (`DRIVE_Z_PHASE_WIDTH'b000000000000)
`define DRIVE_CONST_PHASE_1    (`DRIVE_Z_PHASE_WIDTH'b000000010000)
`define DRIVE_CONST_PHASE_2    (`DRIVE_Z_PHASE_WIDTH'b000000100000)
`define DRIVE_CONST_PHASE_3    (`DRIVE_Z_PHASE_WIDTH'b000000110000)
`define DRIVE_CONST_PHASE_4    (`DRIVE_Z_PHASE_WIDTH'b000001000000)
`define DRIVE_CONST_PHASE_5    (`DRIVE_Z_PHASE_WIDTH'b000001010000)
`define DRIVE_CONST_PHASE_6    (`DRIVE_Z_PHASE_WIDTH'b000001100000)
`define DRIVE_CONST_PHASE_7    (`DRIVE_Z_PHASE_WIDTH'b000001110000)

`define DRIVE_CONST_Y_INST     (`DRIVE_Z_PHASE_WIDTH'b000000000111)

`define DRIVE_QUBIT_ADDR_WIDTH_PER_GROUP 5
`define DRIVE_QUBIT_ADDR_WIDTH_PER_BANK 4

`define DRIVE_INST_WIDTH_PER_BANK (`DRIVE_START_TIME_WIDTH+`DRIVE_QUBIT_ADDR_WIDTH_PER_GROUP+1+`DRIVE_Z_PHASE_WIDTH)
`define DRIVE_INST_WIDTH_PER_GROUP (2*`DRIVE_INST_WIDTH_PER_BANK)
`define DRIVE_INST_WIDTH_TOTAL_GROUP (`DRIVE_NUM_GROUP*`DRIVE_INST_WIDTH_PER_GROUP)
*/

// multiplexing: 16
// /*
`define DRIVE_START_TIME_WIDTH 24
`define DRIVE_BS_SELECT_WIDTH 3
`define DRIVE_NUM_GROUP 72

`define DRIVE_NUM_QUBIT_PER_GROUP 16
`define DRIVE_NUM_QUBIT_PER_BANK 8
`define DRIVE_NUM_BANK_PER_GROUP 2
`define DRIVE_BANK_ADDR_WIDTH_PER_GROUP 1

`define DRIVE_NUM_TOTAL_QUBIT (`DRIVE_NUM_GROUP*`DRIVE_NUM_QUBIT_PER_GROUP)

`define DRIVE_Z_PHASE_WIDTH 12
`define DRIVE_NUM_PHASE 8

`define DRIVE_CONST_PHASE_0    (`DRIVE_Z_PHASE_WIDTH'b000000000000)
`define DRIVE_CONST_PHASE_1    (`DRIVE_Z_PHASE_WIDTH'b000000010000)
`define DRIVE_CONST_PHASE_2    (`DRIVE_Z_PHASE_WIDTH'b000000100000)
`define DRIVE_CONST_PHASE_3    (`DRIVE_Z_PHASE_WIDTH'b000000110000)
`define DRIVE_CONST_PHASE_4    (`DRIVE_Z_PHASE_WIDTH'b000001000000)
`define DRIVE_CONST_PHASE_5    (`DRIVE_Z_PHASE_WIDTH'b000001010000)
`define DRIVE_CONST_PHASE_6    (`DRIVE_Z_PHASE_WIDTH'b000001100000)
`define DRIVE_CONST_PHASE_7    (`DRIVE_Z_PHASE_WIDTH'b000001110000)

`define DRIVE_CONST_Y_INST     (`DRIVE_Z_PHASE_WIDTH'b000000000111)

`define DRIVE_QUBIT_ADDR_WIDTH_PER_GROUP 4
`define DRIVE_QUBIT_ADDR_WIDTH_PER_BANK 3

`define DRIVE_INST_WIDTH_PER_BANK (`DRIVE_START_TIME_WIDTH+`DRIVE_QUBIT_ADDR_WIDTH_PER_GROUP+1+`DRIVE_Z_PHASE_WIDTH)
`define DRIVE_INST_WIDTH_PER_GROUP (2*`DRIVE_INST_WIDTH_PER_BANK)
`define DRIVE_INST_WIDTH_TOTAL_GROUP (`DRIVE_NUM_GROUP*`DRIVE_INST_WIDTH_PER_GROUP)
// */