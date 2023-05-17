module readout_rx_state_decision_output_logic_intel_opt_2 #(
    parameter NUM_THRESHOLD = 0,
    parameter BIN_COUNTER_WIDTH = 16,

    parameter THRESHOLD_MEMORY_NUM_ENTRY = 16,
    parameter THRESHOLD_MEMORY_ADDR_WIDTH = 4,
    parameter THRESHOLD_MEMORY_DATA_WIDTH = 32, // == 2*THRESHOLD_WIDTH
    parameter THRESHOLD_WIDTH = 16 // == BIN_COUNTER_WIDTH
)(
    clk,
    rst,

    threshold_memory_wr_en,
    threshold_memory_wr_addr,
    threshold_memory_wr_data,

    bin_count_in,
    finish_trial_in,
    last_trial_in,

    threshold_addr_in,

    decision_fin_out,

    valid_meas_result_out,
    meas_result_out
);

input clk;
input rst;

input [BIN_COUNTER_WIDTH-1:0] bin_count_in;
input finish_trial_in;
input last_trial_in;

input [THRESHOLD_MEMORY_ADDR_WIDTH-1:0] threshold_addr_in;

output decision_fin_out;
output valid_meas_result_out;
output meas_result_out;


input                                       threshold_memory_wr_en;
input   [THRESHOLD_MEMORY_ADDR_WIDTH-1:0]   threshold_memory_wr_addr;
input   [THRESHOLD_MEMORY_DATA_WIDTH-1:0]   threshold_memory_wr_data;

wire    [THRESHOLD_MEMORY_ADDR_WIDTH-1:0]   threshold_memory_rd_addr;
wire    [THRESHOLD_MEMORY_DATA_WIDTH-1:0]   threshold_memory_rd_data;

wire    [THRESHOLD_WIDTH-1:0] lower_threshold;
wire    [THRESHOLD_WIDTH-1:0] upper_threshold;

wire decision_0_condition;
wire decision_1_condition;
wire decision_fin;

reg valid_meas_result;
reg meas_result;

assign threshold_memory_rd_addr = threshold_addr_in;

random_access_mem #(
    .NUM_ENTRY(THRESHOLD_MEMORY_NUM_ENTRY),
    .ADDR_WIDTH(THRESHOLD_MEMORY_ADDR_WIDTH),
    .DATA_WIDTH(THRESHOLD_MEMORY_DATA_WIDTH)
) threshold_memory (
    .clk(clk),
    .wr_en(threshold_memory_wr_en),
    .wr_addr(threshold_memory_wr_addr),
    .wr_data(threshold_memory_wr_data),
    .rd_addr(threshold_memory_rd_addr),
    .rd_data(threshold_memory_rd_data)
);
// Threshold determination condition
// |1> state if "samples(|1>) - samples(|0>) >= upper_threshold" 
// Try next round if "upper_threshold > samples(|1>) - samples(|0>) >= lower_threshold" 
// |0> state if "lower_threshold > samples(|1>) - samples(|0>)" 
assign upper_threshold = threshold_memory_rd_data[1*THRESHOLD_WIDTH +: THRESHOLD_WIDTH];
assign lower_threshold = threshold_memory_rd_data[0*THRESHOLD_WIDTH +: THRESHOLD_WIDTH];

assign decision_0_condition = (bin_count_in < lower_threshold) ? 1'b1 : 1'b0;
assign decision_1_condition = (bin_count_in >= upper_threshold) ? 1'b1 : 1'b0;
assign decision_fin = ((decision_0_condition | decision_1_condition) & finish_trial_in) | last_trial_in;

always @(posedge clk) begin
    if (rst) begin
        valid_meas_result <= 1'b0;
        meas_result <= 1'b0;
    end
    else if (decision_fin) begin
        valid_meas_result <= decision_fin;
        if (last_trial_in) begin
            meas_result <= (bin_count_in >= {1'b1, NUM_THRESHOLD[BIN_COUNTER_WIDTH-2:0]});
        end
        else begin
            meas_result <= (decision_1_condition | (~decision_0_condition));
        end
    end
    else begin
        valid_meas_result <= 1'b0;
        meas_result <= 1'b0;
    end
end

assign decision_fin_out = decision_fin;
assign valid_meas_result_out = valid_meas_result;
assign meas_result_out = meas_result;


endmodule