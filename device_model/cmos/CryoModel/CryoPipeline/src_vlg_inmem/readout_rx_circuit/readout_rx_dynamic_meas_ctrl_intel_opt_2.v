module readout_rx_dynamic_meas_ctrl_intel_opt_2 #(
    parameter STEP_COUNTER_WIDTH = 8, // can handle a single trial with maximum 256 cycles (102ns)
    parameter TRIAL_COUNTER_WIDTH = 4, // == THRESHOLD_MEMORY_ADDR_WIDTH

    parameter STEP_LIMIT_THRESHOLD = 125, // 50ns for 2.5GHz device
    parameter MAX_TRIAL = 10,

    parameter THRESHOLD_MEMORY_ADDR_WIDTH = 4,
    parameter THRESHOLD_WIDTH = 16
)(
    clk,
    rst,

    // step_limit_wr_en,
    // step_limit_wr_data,

    start_count_in,
    finish_count_in,
    decision_fin_in,

    finish_trial_out,
    last_trial_out,
    threshold_addr_out,
    bin_count_wr_en,
    bin_count_rst
);

input clk;
input rst;

// input step_limit_wr_en;
// input [STEP_COUNTER_WIDTH-1:0] step_limit_wr_data;

input start_count_in;
input finish_count_in;
input decision_fin_in;

output finish_trial_out;
output last_trial_out;
output [THRESHOLD_MEMORY_ADDR_WIDTH-1:0] threshold_addr_out;
output bin_count_wr_en;
output bin_count_rst;

//

reg decision_running;

wire step_counter_en;
wire step_counter_rst;
wire [STEP_COUNTER_WIDTH-1:0] step_counter_count;

wire finish_trial;
wire last_trial;

wire trial_counter_en;
wire [TRIAL_COUNTER_WIDTH-1:0] trial_counter_count;
//

/*
reg [STEP_COUNTER_WIDTH-1:0] step_limit;
always @(posedge clk) begin
    if (rst) begin
        step_limit <= 0;
    end
    else if (step_limit_wr_en) begin
        step_limit <= step_limit_wr_data;
    end
end
*/
wire [STEP_COUNTER_WIDTH-1:0] step_limit;
assign step_limit = STEP_LIMIT_THRESHOLD[STEP_COUNTER_WIDTH-1:0];

always @(posedge clk) begin
    if (rst) begin
        decision_running <= 1'b0;
    end
    else if (start_count_in) begin
        decision_running <= 1'b1;
    end
    else if (decision_fin_in) begin
        decision_running <= 1'b0;
    end
end

assign step_counter_en = decision_running;
assign step_counter_rst = rst | finish_trial;
counter_param #(
    .COUNT_WIDTH(STEP_COUNTER_WIDTH)
) step_counter (
    .clk(clk), 
    .rst(step_counter_rst),
    .en(step_counter_en),
    .count(step_counter_count)
);


assign finish_trial = (step_counter_count > step_limit) ? 1'b1 : 1'b0;
assign trial_counter_en = finish_trial;
counter_param #(
    .COUNT_WIDTH(TRIAL_COUNTER_WIDTH)
) trial_counter (
    .clk(clk), 
    .rst(rst),
    .en(trial_counter_en),
    .count(trial_counter_count)
);

assign last_trial = (decision_running & finish_count_in) | ((trial_counter_count >= MAX_TRIAL) & finish_trial);

// output
assign finish_trial_out = finish_trial;
assign last_trial_out = last_trial;
assign bin_count_wr_en = decision_running;
assign threshold_addr_out = trial_counter_count;
assign bin_count_rst = start_count_in;

endmodule