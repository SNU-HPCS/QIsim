module readout_rx_state_decision_unit_intel_opt_1 #(
    parameter DATA_WIDTH = 16,
    parameter NUM_THRESHOLD = 0, // N(count_cont) - N(!count_cond)
    parameter BIN_COUNTER_WIDTH = 16,
    
    parameter STATE_DECISION_DATA_WIDTH = DATA_WIDTH,
    parameter STATE_DECISION_ADDR_WIDTH = 1
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

output valid_meas_result_out;
output meas_result_out;

wire start_count_classifier;
wire finish_count_classifier;
wire valid_classifier;
wire count_condition;

wire [BIN_COUNTER_WIDTH-1:0] bin_count;

wire valid_meas_result;
wire meas_result;

readout_rx_bin_classifier_intel_opt #(
    .DATA_WIDTH(DATA_WIDTH),
    .STATE_DECISION_DATA_WIDTH(STATE_DECISION_DATA_WIDTH),
    .STATE_DECISION_ADDR_WIDTH(STATE_DECISION_ADDR_WIDTH)
) readout_rx_bin_classifier_intel_opt_instance (
    .clk(clk),
    .rst(rst),
    .state_decision_coeff_wr_en(state_decision_coeff_wr_en),
    .state_decision_coeff_wr_addr(state_decision_coeff_wr_addr),
    .state_decision_coeff_wr_data(state_decision_coeff_wr_data),
    .start_count_in(start_count),
    .finish_count_in(finish_count),
    .valid_in(valid_in),
    .i_in(i_in),
    .q_in(q_in),
    .start_count_out(start_count_classifier),
    .finish_count_out(finish_count_classifier),
    .valid_out(valid_classifier),
    .count_condition(count_condition)
);

readout_rx_bin_accumulator_intel_opt #(
    .BIN_COUNTER_WIDTH(BIN_COUNTER_WIDTH)
) readout_rx_bin_accumulator_intel_opt_instance (
    .clk(clk),
    .rst(rst),
    .count_condition(count_condition),
    .start_count(start_count_classifier),
    .valid_in(valid_classifier),
    .bin_count_out(bin_count)
);

readout_rx_state_decision_output_logic_intel_opt_1 #(
    .NUM_THRESHOLD(NUM_THRESHOLD),
    .BIN_COUNTER_WIDTH(BIN_COUNTER_WIDTH)
) readout_rx_state_decision_output_logic_intel_opt_instance (
    .clk(clk),
    .rst(rst),
    .bin_count_in(bin_count),
    .finish_count_in(finish_count_classifier),
    .valid_meas_result_out(valid_meas_result),
    .meas_result_out(meas_result)
);

assign valid_meas_result_out = valid_meas_result;
assign meas_result_out = meas_result;


endmodule