`ifndef DEFINE_DRIVE_CIRCUIT_V
`define DEFINE_DRIVE_CIRCUIT_V


/*** CONSTANT or DEPENDENT_VARS ***/
// Arithmetic
`define log2(n)   ((n) <= (1<<0) ? 0 : (n) <= (1<<1) ? 1 :\
                   (n) <= (1<<2) ? 2 : (n) <= (1<<3) ? 3 :\
                   (n) <= (1<<4) ? 4 : (n) <= (1<<5) ? 5 :\
                   (n) <= (1<<6) ? 6 : (n) <= (1<<7) ? 7 :\
                   (n) <= (1<<8) ? 8 : (n) <= (1<<9) ? 9 :\
                   (n) <= (1<<10) ? 10 : (n) <= (1<<11) ? 11 :\
                   (n) <= (1<<12) ? 12 : (n) <= (1<<13) ? 13 :\
                   (n) <= (1<<14) ? 14 : (n) <= (1<<15) ? 15 :\
                   (n) <= (1<<16) ? 16 : (n) <= (1<<17) ? 17 :\
                   (n) <= (1<<18) ? 18 : (n) <= (1<<19) ? 19 :\
                   (n) <= (1<<20) ? 20 : (n) <= (1<<21) ? 21 :\
                   (n) <= (1<<22) ? 22 : (n) <= (1<<23) ? 23 :\
                   (n) <= (1<<24) ? 24 : (n) <= (1<<25) ? 25 :\
                   (n) <= (1<<26) ? 26 : (n) <= (1<<27) ? 27 :\
                   (n) <= (1<<28) ? 28 : (n) <= (1<<29) ? 29 :\
                   (n) <= (1<<30) ? 30 : (n) <= (1<<31) ? 31 : 32)

`endif

`define NUM_BANK                    2
`define NUM_QUBIT_PER_BANK          16
`define QUBIT_ADDR_WIDTH_PER_BANK   4
`define IQ_OUT_WIDTH                9   // Usually IQ_OUT_WIDTH == IQ_CALI_WIDTH
`define IQ_SUM_WIDTH                (`IQ_OUT_WIDTH+`log2(`NUM_BANK))
// pc
`define PC_WIDTH                    `INST_LIST_ADDR_WIDTH  // Usually PC_WIDTH == INST_LIST_ADDR_WIDTH
// nco
`define NUM_NCO                     `NUM_QUBIT_PER_BANK
`define NCO_OUTPUT_WIDTH            `PHASE_WIDTH
`define NCO_ADDR_WIDTH              `QUBIT_ADDR_WIDTH_PER_BANK
`define NCO_N                       22
`define Z_CORR_WIDTH                12
`define SIN_LUT_NUM_ENTRY           1024
// z_corr memory
`define Z_CORR_MEMORY_NUM_ENTRY     `NUM_QUBIT_PER_BANK
`define Z_CORR_MEMORY_ADDR_WIDTH    `QUBIT_ADDR_WIDTH_PER_BANK
`define Z_CORR_MEMORY_DATA_WIDTH    (`Z_CORR_WIDTH*`NUM_QUBIT_PER_BANK*`NUM_BANK)
// enve_memory
`define AMP_WIDTH                   8
`define PHASE_WIDTH                 10
`define ENVE_MEMORY_NUM_ENTRY       40960
`define ENVE_MEMORY_ADDR_WIDTH      16
`define ENVE_MEMORY_DATA_WIDTH      (`PHASE_WIDTH+`AMP_WIDTH)
// inst_table
`define AXIS_WIDTH                  2
`define INST_TABLE_NUM_ENTRY        8
`define INST_TABLE_ADDR_WIDTH       3 // INST_LIST_DATA_WIDTH - 5 (log2(32))
`define INST_TABLE_DATA_WIDTH       (`ENVE_MEMORY_ADDR_WIDTH*2+`AXIS_WIDTH)
// inst_list
`define INST_LIST_NUM_ENTRY         2048
`define INST_LIST_ADDR_WIDTH        11
`define INST_LIST_DATA_WIDTH        (`QUBIT_ADDR_WIDTH_PER_BANK+1+`Z_CORR_WIDTH) // qubit_sel, z_corr_mode, phase_imm
// cali_memory
`define IQ_CALI_WIDTH               `IQ_OUT_WIDTH
`define CALI_MEMORY_NUM_ENTRY       `NUM_QUBIT_PER_BANK
`define CALI_MEMORY_ADDR_WIDTH      `QUBIT_ADDR_WIDTH_PER_BANK
`define CALI_MEMORY_DATA_WIDTH      (4*`IQ_CALI_WIDTH)
