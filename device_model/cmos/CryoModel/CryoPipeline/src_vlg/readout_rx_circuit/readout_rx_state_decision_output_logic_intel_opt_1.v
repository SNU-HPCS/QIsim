`ifndef DEFINE_READOUT_RX_CIRCUIT_V
`include "define_readout_rx_circuit.v"
`endif

module readout_rx_state_decision_output_logic_intel_opt_1 #(
    parameter NUM_THRESHOLD = 0, // N(count_cont) - N(!count_cond)
    parameter BIN_COUNTER_WIDTH = 16
)(
    clk,
    rst,

    bin_count_in,
    finish_count_in,

    valid_meas_result_out,
    meas_result_out
);

input clk;
input rst;

input [BIN_COUNTER_WIDTH-1:0] bin_count_in;
input finish_count_in;

output valid_meas_result_out;
output meas_result_out;

wire meas_result_condition;

reg valid_meas_result;
reg meas_result;

assign meas_result_condition = (bin_count_in >= {1'b1, NUM_THRESHOLD[BIN_COUNTER_WIDTH-2:0]}) ? 1'b1 : 1'b0;

always @(posedge clk) begin
    if (rst) begin
        valid_meas_result <= 1'b0;
        meas_result <= 1'b0;
    end
    else if (finish_count_in) begin
        valid_meas_result <= 1'b1;

        if (meas_result_condition) meas_result <= 1'b1;
        else meas_result <= 1'b0;
    end
    else begin
        valid_meas_result <= 1'b0;
        meas_result <= 1'b0;
    end
end

assign valid_meas_result_out = valid_meas_result;
assign meas_result_out = meas_result;
endmodule