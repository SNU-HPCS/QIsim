// `ifndef DEFINE_READOUT_RX_CIRCUIT_V
`define DEFINE_READOUT_RX_CIRCUIT_V


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

`define READRX_NUM_QUBIT                        8
`define READRX_QUBIT_ADDR_WIDTH                 3

`define READRX_INPUT_IQ_WIDTH                   8 // round up 7.5-bit to 8-bit

`define READRX_GLB_COUNTER_WIDTH                24
`define READRX_AVG_WINDOW_WIDTH                 3
`define READRX_LOGGING_SRC_WIDTH                4

`define READRX_PC_WIDTH                         `READRX_INST_LIST_ADDR_WIDTH

// inst_list
`define READRX_SIGNAL_LENGTH_WIDTH              20

`define READRX_INST_LIST_NUM_ENTRY              32 // ** not specified in the paper
`define READRX_INST_LIST_ADDR_WIDTH             5
`define READRX_INST_LIST_DATA_WIDTH             (`READRX_GLB_COUNTER_WIDTH+`READRX_SIGNAL_LENGTH_WIDTH+`READRX_NUM_QUBIT+`READRX_AVG_WINDOW_WIDTH+`READRX_LOGGING_SRC_WIDTH)

// calibration
// `define READRX_IQ_CALI_WIDTH                    9
// `define READRX_IQ_CALI_OUT_WIDTH                16
`define READRX_IQ_CALI_WIDTH                    9
`define READRX_IQ_CALI_OUT_WIDTH                8
// `define READRX_IQ_CALI_OUT_WIDTH                16
`define READRX_NUM_CALI_COEFF                   5 // alpha_i, beta_i, alpha_q, beta_q, dc_correction

// readout_tx_signal_gen_unit
`define READRX_NCO_N                            22
`define READRX_PHASE_WIDTH                      10

`define READRX_SIN_LUT_NUM_ENTRY                1024
`define READRX_SIN_LUT_ADDR_WIDTH               `READRX_PHASE_WIDTH
`define READRX_SIN_LUT_DATA_WIDTH               `READRX_IQ_CALI_OUT_WIDTH

// `define READRX_AVG_FILTER_NUM_OPERAND           8
// `define READRX_AVG_FILTER_OPERAND_ADDR_WIDTH    3
`define READRX_AVG_FILTER_NUM_OPERAND           4
`define READRX_AVG_FILTER_OPERAND_ADDR_WIDTH    2

// multiplier type
`define POWER_OPTIMIZED_MULTIPLIER

// state decision

// state decision type
`define READRX_STATE_DECISION_BASELINE
// `define READRX_STATE_DECISION_INTEL_OPT_1
// `define READRX_STATE_DECISION_INTEL_OPT_2
// `define READRX_STATE_DECISION_GOOGLE

`define READRX_NUM_THRESHOLD                    128
`define READRX_BIN_COUNTER_WIDTH                16

// readout_rx_state_decision_unit_baseline
`ifdef READRX_STATE_DECISION_BASELINE
    `define READRX_STATE_DECISION_DATA_WIDTH        (1 << `READRX_SIN_LUT_DATA_WIDTH)
    `define READRX_STATE_DECISION_ADDR_WIDTH        (`READRX_SIN_LUT_DATA_WIDTH)
    `define READRX_BIN_COUNT_MEM_NUM_ENTRY          (1 << `READRX_BIN_COUNT_MEM_ADDR_WIDTH)
    `define READRX_BIN_COUNT_MEM_ADDR_WIDTH         (2*`READRX_SIN_LUT_DATA_WIDTH)
    `define READRX_BIN_COUNT_MEM_DATA_WIDTH         `READRX_BIN_COUNTER_WIDTH
// readout_rx_state_decision_unit_intel_opt_1
`elsif READRX_STATE_DECISION_INTEL_OPT_1
    `define READRX_STATE_DECISION_DATA_WIDTH        `READRX_SIN_LUT_DATA_WIDTH
    `define READRX_STATE_DECISION_ADDR_WIDTH        1
// readout_rx_state_decision_unit_intel_opt_2
`elsif READRX_STATE_DECISION_INTEL_OPT_2
    `define READRX_STATE_DECISION_DATA_WIDTH        `READRX_SIN_LUT_DATA_WIDTH
    `define READRX_STATE_DECISION_ADDR_WIDTH        1

    `define READRX_STEP_COUNTER_WIDTH               8
    `define READRX_TRIAL_COUNTER_WIDTH              4
    `define READRX_THRESHOLD_WIDTH                  16
    `define READRX_THRESHOLD_MEMORY_NUM_ENTRY       16
    `define READRX_THRESHOLD_MEMORY_ADDR_WIDTH      (`log2(`READRX_THRESHOLD_MEMORY_NUM_ENTRY))
    `define READRX_THRESHOLD_MEMORY_DATA_WIDTH      (2*`READRX_THRESHOLD_WIDTH)
    `define READRX_STEP_LIMIT_THRESHOLD             125 // num samples per trial
    `define READRX_MAX_TRIAL                        5

// readout_rx_state_decision_unit_google
`elsif READRX_STATE_DECISION_GOOGLE
    `define READRX_STATE_DECISION_DATA_WIDTH        `READRX_SIN_LUT_DATA_WIDTH
    `define READRX_STATE_DECISION_ADDR_WIDTH        1
    `ifdef POWER_OPTIMIZED_MULTIPLIER
        `define READRX_ACCUMULATOR_WIDTH                ((`READRX_SIN_LUT_DATA_WIDTH>>1)+`READRX_BIN_COUNTER_WIDTH) // take half MSB bits for the value accumulation
    `else
        `define READRX_ACCUMULATOR_WIDTH                (`READRX_SIN_LUT_DATA_WIDTH+`READRX_BIN_COUNTER_WIDTH) // take a whole number for the value accumulation
    `endif
`endif
