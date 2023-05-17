`ifndef DEFINE_READOUT_RX_CIRCUIT_V
`include "define_readout_rx_circuit.v"
`endif

module readout_rx_state_decision_unit_google #(
    parameter DATA_WIDTH = 8,

    // parameter THRESHOLD_A = 0,
    // parameter THRESHOLD_B = 0,
    parameter STATE_DECISION_DATA_WIDTH = DATA_WIDTH,
    parameter STATE_DECISION_ADDR_WIDTH = 1,

    parameter ACCUMULATOR_WIDTH = (DATA_WIDTH + 10) // ACCUMULATOR_WIDTH >= DATA_WIDTH
)(
    clk,
    rst,

    state_decision_coeff_wr_en,
    state_decision_coeff_wr_addr,
    state_decision_coeff_wr_data,

    start_count,
    finish_count,

    valid_in,
    i_in,
    q_in,
    valid_meas_result_out,
    meas_result_out
);

localparam I_SCALE_FACTOR = DATA_WIDTH-1;
localparam MULT_OUT_WIDTH = (DATA_WIDTH + ACCUMULATOR_WIDTH);
localparam IQ_COMPARE_WIDTH = (MULT_OUT_WIDTH-I_SCALE_FACTOR);
localparam DATA_INTERMEDIATE = DATA_WIDTH >> 1;


input clk;
input rst;

input                                   state_decision_coeff_wr_en;
input [STATE_DECISION_ADDR_WIDTH-1:0]   state_decision_coeff_wr_addr;
input [STATE_DECISION_DATA_WIDTH-1:0]   state_decision_coeff_wr_data; // [slope, y_intercept]

input start_count;
input finish_count;

input valid_in;
input signed [DATA_WIDTH-1:0] i_in;
input signed [DATA_WIDTH-1:0] q_in;

wire signed [DATA_INTERMEDIATE-1:0] i_in_intermediate;
wire signed [DATA_INTERMEDIATE-1:0] q_in_intermediate;

wire signed [ACCUMULATOR_WIDTH-1:0] sign_extend_i_in;
wire signed [ACCUMULATOR_WIDTH-1:0] sign_extend_q_in;

output valid_meas_result_out;
output meas_result_out;

wire signed [(ACCUMULATOR_WIDTH-1):0] i_sum;
wire signed [(ACCUMULATOR_WIDTH-1):0] q_sum;

wire meas_result_condition;

reg valid_meas_result;
reg meas_result;

readout_rx_bin_accumulator_google #(
    .DATA_WIDTH(DATA_WIDTH),
    .ACCUMULATOR_WIDTH(ACCUMULATOR_WIDTH)
) readout_rx_bin_accumulator_instance (
    .clk(clk),
    .rst(rst),
    .start_count(start_count),
    .valid_in(valid_in),
    .i_in(i_in),
    .q_in(q_in),
    .i_sum_out(i_sum),
    .q_sum_out(q_sum)
);

// State decision.
wire finish_count_classifier;
readout_rx_bin_classifier_google #(
    .DATA_WIDTH(DATA_WIDTH),
    .STATE_DECISION_DATA_WIDTH(STATE_DECISION_DATA_WIDTH),
    .STATE_DECISION_ADDR_WIDTH(STATE_DECISION_ADDR_WIDTH),
    .ACCUMULATOR_WIDTH(ACCUMULATOR_WIDTH)
) readout_rx_bin_classifier_instance (
    .clk(clk),
    .rst(rst),
    .state_decision_coeff_wr_en(state_decision_coeff_wr_en),
    .state_decision_coeff_wr_addr(state_decision_coeff_wr_addr),
    .state_decision_coeff_wr_data(state_decision_coeff_wr_data),
    .finish_count_in(finish_count),
    .i_sum_in(i_sum),
    .q_sum_in(q_sum),
    .finish_count_out(finish_count_classifier),
    .meas_result_condition(meas_result_condition)
);

readout_rx_state_decision_output_logic_google readout_rx_state_decision_output_logic_instance (
    .clk(clk),
    .rst(rst),
    .finish_count_in(finish_count_classifier),
    .meas_result_condition(meas_result_condition),
    .valid_meas_result_out(valid_meas_result_out),
    .meas_result_out(meas_result_out)
);

endmodule