`ifndef DEFINE_READOUT_RX_CIRCUIT_V
`include "define_readout_rx_circuit.v"
`endif

module readout_rx_bin_classifier_google #(
    parameter DATA_WIDTH = 8,

    parameter STATE_DECISION_DATA_WIDTH = DATA_WIDTH,
    parameter STATE_DECISION_ADDR_WIDTH = 1,

    parameter ACCUMULATOR_WIDTH = (DATA_WIDTH + 10) // ACCUMULATOR_WIDTH >= DATA_WIDTH
)(
    clk,
    rst,

    state_decision_coeff_wr_en,
    state_decision_coeff_wr_addr,
    state_decision_coeff_wr_data,

    finish_count_in,

    i_sum_in,
    q_sum_in,

    finish_count_out,
    meas_result_condition
);

localparam I_SCALE_FACTOR = DATA_WIDTH-1;
localparam MULT_OUT_WIDTH = (DATA_WIDTH + ACCUMULATOR_WIDTH);
localparam IQ_COMPARE_WIDTH = (MULT_OUT_WIDTH-I_SCALE_FACTOR);

input clk;
input rst;

input                                   state_decision_coeff_wr_en;
input [STATE_DECISION_ADDR_WIDTH-1:0]   state_decision_coeff_wr_addr;
input [STATE_DECISION_DATA_WIDTH-1:0]   state_decision_coeff_wr_data; // [slope, y_intercept]

input finish_count_in;

input signed [ACCUMULATOR_WIDTH-1:0] i_sum_in;
input signed [ACCUMULATOR_WIDTH-1:0] q_sum_in;

output finish_count_out;
output meas_result_condition;

// State decision.
reg finish_count_0_1;
reg finish_count_1_1;

reg signed [DATA_WIDTH-1:0] slope; // Range: (2^(DATA_WIDTH-I_SCALE_FACTOR-1))*(-1.0) <= a <= (2^(DATA_WIDTH-I_SCALE_FACTOR-1))*(1.0-2^DATA_WIDTH)
reg signed [DATA_WIDTH-1:0] y_intercept; // Range: (2^(DATA_WIDTH-I_SCALE_FACTOR-1))*(-1.0) <= b <= (2^(DATA_WIDTH-I_SCALE_FACTOR-1))*(1.0-2^DATA_WIDTH)
wire signed [ACCUMULATOR_WIDTH-1:0] sign_extend_slope; // Range: (2^(DATA_WIDTH-I_SCALE_FACTOR-1))*(-1.0) <= a <= (2^(DATA_WIDTH-I_SCALE_FACTOR-1))*(1.0-2^DATA_WIDTH)
wire signed [MULT_OUT_WIDTH-1:0] sign_extend_y_intercept; // Range: (2^(DATA_WIDTH-I_SCALE_FACTOR-1))*(-1.0) <= b <= (2^(DATA_WIDTH-I_SCALE_FACTOR-1))*(1.0-2^DATA_WIDTH)

wire signed [MULT_OUT_WIDTH-1:0] decision_mult_out;
reg signed [MULT_OUT_WIDTH-1:0] decision_mult;

wire signed [IQ_COMPARE_WIDTH-1:0] decision_value_out;
reg signed [IQ_COMPARE_WIDTH-1:0] decision_value;

reg signed [ACCUMULATOR_WIDTH-1:0] q_sum_0_1;
reg signed [IQ_COMPARE_WIDTH-1:0] q_sum_1_1;

always @(posedge clk) begin
    if (rst) begin
        slope <= 0;
        y_intercept <= 0;
    end
    else if (state_decision_coeff_wr_en) begin
        if (state_decision_coeff_wr_addr == 1'b0) begin
            slope <= slope;
            y_intercept <= state_decision_coeff_wr_data;
        end
        else begin
            slope <= state_decision_coeff_wr_data;
            y_intercept <= y_intercept;
        end
    end
    else begin
        slope <= slope;
        y_intercept <= y_intercept;
    end 
end

assign sign_extend_slope = {{(ACCUMULATOR_WIDTH-DATA_WIDTH){slope[DATA_WIDTH-1]}}, slope};
assign sign_extend_y_intercept = {{(MULT_OUT_WIDTH-DATA_WIDTH){y_intercept[DATA_WIDTH-1]}}, y_intercept};
multiplier_signed_param #(
    .DATA_IN_WIDTH(ACCUMULATOR_WIDTH),
    .DATA_OUT_WIDTH(MULT_OUT_WIDTH),
    .TAKE_MSB(0)
) i_slope_multiplier (
    .data_in_1(i_sum_in),
    .data_in_2(sign_extend_slope),
    .data_out(decision_mult_out)
);

always @(posedge clk) begin
    decision_mult <= decision_mult_out;
    q_sum_0_1 <= q_sum_in;
    finish_count_0_1 <= finish_count_in;
end

adder_signed_param #(
    .DATA_IN_WIDTH(MULT_OUT_WIDTH),
    .DATA_INTERMEDIATE_WIDTH(MULT_OUT_WIDTH),
    .DATA_OUT_WIDTH(IQ_COMPARE_WIDTH),
    .TAKE_MSB(1)
) i_y_intercept_adder (
    .data_in_1(decision_mult),
    .data_in_2(sign_extend_y_intercept),
    .data_out(decision_value_out)
);

always @(posedge clk) begin
    decision_value <= decision_value_out;
    q_sum_1_1 <= {{(IQ_COMPARE_WIDTH-ACCUMULATOR_WIDTH){q_sum_0_1[ACCUMULATOR_WIDTH-1]}}, q_sum_0_1};
    finish_count_1_1 <= finish_count_0_1;
end

assign meas_result_condition = (decision_value > q_sum_1_1) ? 1'b1 : 1'b0;
assign finish_count_out = finish_count_1_1;

endmodule