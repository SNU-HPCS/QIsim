`ifndef DEFINE_READOUT_RX_CIRCUIT_V
`include "define_readout_rx_circuit.v"
`endif

module readout_rx_bin_classifier_intel_opt #(
    parameter DATA_WIDTH = 16,
    parameter STATE_DECISION_DATA_WIDTH = DATA_WIDTH,
    parameter STATE_DECISION_ADDR_WIDTH = 1
)(
    clk,
    rst,

    state_decision_coeff_wr_en,
    state_decision_coeff_wr_addr,
    state_decision_coeff_wr_data,

    start_count_in,
    finish_count_in,
    valid_in,
    i_in,
    q_in,

    start_count_out,
    finish_count_out,
    valid_out,
    count_condition
);

localparam I_SCALE_FACTOR = DATA_WIDTH-1;

`ifdef POWER_OPTIMIZED_MULTIPLIER
    localparam MULT_OUT_WIDTH = DATA_WIDTH;
    localparam IQ_COMPARE_WIDTH = DATA_WIDTH;
`else
    localparam MULT_OUT_WIDTH = 2*DATA_WIDTH;
    localparam IQ_COMPARE_WIDTH = (MULT_OUT_WIDTH-I_SCALE_FACTOR);
`endif

input clk;
input rst;

input                                   state_decision_coeff_wr_en;
input [STATE_DECISION_ADDR_WIDTH-1:0]   state_decision_coeff_wr_addr;
input [STATE_DECISION_DATA_WIDTH-1:0]   state_decision_coeff_wr_data; // [slope, y_intercept]

input start_count_in;
input finish_count_in;

input valid_in;
input signed [DATA_WIDTH-1:0] i_in;
input signed [DATA_WIDTH-1:0] q_in;

output start_count_out;
output finish_count_out;
output valid_out;
output count_condition;

// calculate count condition with a single line
reg valid_calc_cond_0_1;
reg valid_calc_cond_1_1;
reg start_count_0_0;
reg finish_count_0_1;
reg finish_count_1_1;

reg signed [DATA_WIDTH-1:0] slope; // Range: (2^(DATA_WIDTH-I_SCALE_FACTOR-1))*(-1.0) <= a <= (2^(DATA_WIDTH-I_SCALE_FACTOR-1))*(1.0-2^DATA_WIDTH)
reg signed [DATA_WIDTH-1:0] y_intercept; // Range: (2^(DATA_WIDTH-I_SCALE_FACTOR-1))*(-1.0) <= b <= (2^(DATA_WIDTH-I_SCALE_FACTOR-1))*(1.0-2^DATA_WIDTH)
wire signed [MULT_OUT_WIDTH-1:0] sign_extend_y_intercept;

wire signed [MULT_OUT_WIDTH-1:0] i_slope_mul_out;
reg signed [MULT_OUT_WIDTH-1:0] i_slope_mul;

wire signed [IQ_COMPARE_WIDTH-1:0] i_y_intercept_add_out;
reg signed [IQ_COMPARE_WIDTH-1:0] i_y_intercept_add;

reg signed [DATA_WIDTH-1:0] q_0_1;
reg signed [IQ_COMPARE_WIDTH-1:0] q_1_1;

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


`ifdef POWER_OPTIMIZED_MULTIPLIER
    multiplier_signed_opt_param #(
        .DATA_IN_WIDTH(DATA_WIDTH),
        .DATA_OUT_WIDTH(MULT_OUT_WIDTH)
    ) i_slope_multiplier (
        .data_in_1(i_in),
        .data_in_2(slope),
        .data_out(i_slope_mul_out)
    );
`else
    multiplier_signed_param #(
        .DATA_IN_WIDTH(DATA_WIDTH),
        .DATA_OUT_WIDTH(MULT_OUT_WIDTH),
        .TAKE_MSB(0)
    ) i_slope_multiplier (
        .data_in_1(i_in),
        .data_in_2(slope),
        .data_out(i_slope_mul_out)
    );
`endif

wire i_slope_mul_ff_wr_en;
wire [MULT_OUT_WIDTH-1:0] i_slope_mul_ff_wr_data;
wire [MULT_OUT_WIDTH-1:0] i_slope_mul_ff_rd_data;

assign i_slope_mul_ff_wr_en = 1'b1;
assign i_slope_mul_ff_wr_data = i_slope_mul_out;

ff #(
    .DATA_WIDTH(MULT_OUT_WIDTH)
) i_slope_mul_ff (
    .clk(clk),
    .rst(rst),
    .wr_en(i_slope_mul_ff_wr_en), 
    .wr_data(i_slope_mul_ff_wr_data), 
    .rd_data(i_slope_mul_ff_rd_data)
);

always @(posedge clk) begin
    // i_slope_mul <= i_slope_mul_out;
    q_0_1 <= q_in;
    valid_calc_cond_0_1 <= valid_in;
    start_count_0_0 <= start_count_in;
    finish_count_0_1 <= finish_count_in;
end

assign sign_extend_y_intercept = {{(MULT_OUT_WIDTH-DATA_WIDTH){y_intercept[DATA_WIDTH-1]}}, y_intercept};
adder_signed_param #(
    .DATA_IN_WIDTH(MULT_OUT_WIDTH),
    .DATA_INTERMEDIATE_WIDTH(MULT_OUT_WIDTH),
    .DATA_OUT_WIDTH(IQ_COMPARE_WIDTH),
    .TAKE_MSB(1)
) i_y_intercept_adder (
    .data_in_1(i_slope_mul_ff_rd_data),
    .data_in_2(sign_extend_y_intercept),
    .data_out(i_y_intercept_add_out)
);

always @(posedge clk) begin
    `ifdef POWER_OPTIMIZED_MULTIPLIER
        i_y_intercept_add <= (i_y_intercept_add_out << 1);
    `else
        i_y_intercept_add <= i_y_intercept_add_out;
    `endif
    q_1_1 <= {{(IQ_COMPARE_WIDTH-DATA_WIDTH){q_0_1[DATA_WIDTH-1]}}, q_0_1};
    valid_calc_cond_1_1 <= valid_calc_cond_0_1;
    finish_count_1_1 <= finish_count_0_1;
end

// assign count_condition = (i_y_intercept_add > q_1_1) ? 1'b1 : 1'b0; // |1> state condition
comparator_param #(
    .DATA_WIDTH(IQ_COMPARE_WIDTH)
) count_comparator (
    .data_in_1(i_y_intercept_add), 
    .data_in_2(q_1_1), 
    .data_out(count_condition)
);

assign start_count_out = start_count_0_0;
assign finish_count_out = finish_count_1_1;
assign valid_out = valid_calc_cond_1_1;

endmodule