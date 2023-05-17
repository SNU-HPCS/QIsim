module readout_rx_state_decision_unit_intel_opt_2 #(
    parameter DATA_WIDTH = 16,
    parameter NUM_THRESHOLD = 0, // N(count_cont) - N(!count_cond)
    parameter BIN_COUNTER_WIDTH = 16,
    
    parameter STATE_DECISION_DATA_WIDTH = DATA_WIDTH,
    parameter STATE_DECISION_ADDR_WIDTH = 1,

    parameter STEP_COUNTER_WIDTH = 8,
    parameter TRIAL_COUNTER_WIDTH = 4,
    parameter THRESHOLD_MEMORY_NUM_ENTRY = 16,
    parameter THRESHOLD_MEMORY_ADDR_WIDTH = 4,
    parameter THRESHOLD_MEMORY_DATA_WIDTH = 32,
    parameter THRESHOLD_WIDTH = 16,

    parameter STEP_LIMIT_THRESHOLD = 125,
    parameter MAX_TRIAL = 10
)(
    clk,
    rst,

    state_decision_coeff_wr_en,
    state_decision_coeff_wr_addr,
    state_decision_coeff_wr_data,

    threshold_memory_wr_en,
    threshold_memory_wr_addr,
    threshold_memory_wr_data,

    // step_limit_wr_en,
    // step_limit_wr_data,

    start_count,
    finish_count,

    valid_in,
    i_in,
    q_in,
    valid_meas_result_out,
    meas_result_out,

    threshold_memory_rd_addr_out,
    threshold_memory_rd_data_in
);

input clk;
input rst;

input                                       state_decision_coeff_wr_en;
input   [STATE_DECISION_ADDR_WIDTH-1:0]     state_decision_coeff_wr_addr;
input   [STATE_DECISION_DATA_WIDTH-1:0]     state_decision_coeff_wr_data; // [slope, y_intercept]

input                                       threshold_memory_wr_en;
input   [THRESHOLD_MEMORY_ADDR_WIDTH-1:0]   threshold_memory_wr_addr;
input   [THRESHOLD_MEMORY_DATA_WIDTH-1:0]   threshold_memory_wr_data;

// input                                       step_limit_wr_en;
// input   [STEP_COUNTER_WIDTH-1:0]            step_limit_wr_data;

input start_count;
input finish_count;

input valid_in;
input signed [DATA_WIDTH-1:0] i_in;
input signed [DATA_WIDTH-1:0] q_in;

output valid_meas_result_out;
output meas_result_out;

output   [THRESHOLD_MEMORY_ADDR_WIDTH-1:0]   threshold_memory_rd_addr_out;
input    [THRESHOLD_MEMORY_DATA_WIDTH-1:0]   threshold_memory_rd_data_in;

wire start_count_classifier;
wire finish_count_classifier;
wire valid_classifier;
wire count_condition;

wire [BIN_COUNTER_WIDTH-1:0] bin_count;

wire valid_meas_result;
wire meas_result;

wire decision_fin;
wire finish_trial;
wire last_trial;
wire [THRESHOLD_MEMORY_ADDR_WIDTH-1:0] threshold_addr;
wire bin_count_wr_en;
wire bin_count_rst;

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
    .start_count(bin_count_rst),
    .valid_in(bin_count_wr_en),
    .bin_count_out(bin_count)
);


readout_rx_dynamic_meas_ctrl_intel_opt_2 #(
    .STEP_COUNTER_WIDTH(STEP_COUNTER_WIDTH),
    .TRIAL_COUNTER_WIDTH(TRIAL_COUNTER_WIDTH),
    .STEP_LIMIT_THRESHOLD(STEP_LIMIT_THRESHOLD),
    .MAX_TRIAL(MAX_TRIAL),
    .THRESHOLD_MEMORY_ADDR_WIDTH(THRESHOLD_MEMORY_ADDR_WIDTH),
    .THRESHOLD_WIDTH(THRESHOLD_WIDTH)
) readout_rx_dynamic_meas_ctrl_intel_opt_instance (
    .clk(clk),
    .rst(rst),
    // .step_limit_wr_en(step_limit_wr_en),
    // .step_limit_wr_data(step_limit_wr_data),
    .start_count_in(start_count_classifier),
    .finish_count_in(finish_count_classifier),
    .decision_fin_in(decision_fin),
    .finish_trial_out(finish_trial),
    .last_trial_out(last_trial),
    .threshold_addr_out(threshold_addr),
    .bin_count_wr_en(bin_count_wr_en),
    .bin_count_rst(bin_count_rst)
);

readout_rx_state_decision_output_logic_intel_opt_2 #(
    .NUM_THRESHOLD(NUM_THRESHOLD),
    .BIN_COUNTER_WIDTH(BIN_COUNTER_WIDTH),
    .THRESHOLD_MEMORY_NUM_ENTRY(THRESHOLD_MEMORY_NUM_ENTRY),
    .THRESHOLD_MEMORY_ADDR_WIDTH(THRESHOLD_MEMORY_ADDR_WIDTH),
    .THRESHOLD_MEMORY_DATA_WIDTH(THRESHOLD_MEMORY_DATA_WIDTH),
    .THRESHOLD_WIDTH(THRESHOLD_WIDTH)
) readout_rx_state_decision_output_logic_intel_opt_2_instance (
    .clk(clk),
    .rst(rst),
    .threshold_memory_wr_en(threshold_memory_wr_en),
    .threshold_memory_wr_addr(threshold_memory_wr_addr),
    .threshold_memory_wr_data(threshold_memory_wr_data),
    .bin_count_in(bin_count),
    .finish_trial_in(finish_trial),
    .last_trial_in(last_trial),
    .threshold_addr_in(threshold_addr),
    .decision_fin_out(decision_fin),
    .valid_meas_result_out(valid_meas_result),
    .meas_result_out(meas_result),
    .threshold_memory_rd_addr_out(threshold_memory_rd_addr_out),
    .threshold_memory_rd_data_in(threshold_memory_rd_data_in)
);



assign valid_meas_result_out = valid_meas_result;
assign meas_result_out = meas_result;


endmodule