`ifndef DEFINE_READOUT_RX_CIRCUIT_V
`include "define_readout_rx_circuit.v"
`endif

module readout_rx_state_decision_output_logic_google 
(
    clk,
    rst,

    finish_count_in,

    meas_result_condition,
    
    valid_meas_result_out,
    meas_result_out
);

input clk;
input rst;

input finish_count_in;

input meas_result_condition;

output valid_meas_result_out;
output meas_result_out;

reg valid_meas_result;
reg meas_result;


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