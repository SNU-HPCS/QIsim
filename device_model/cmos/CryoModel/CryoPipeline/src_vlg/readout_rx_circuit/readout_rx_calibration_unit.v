`ifndef DEFINE_READOUT_RX_CIRCUIT_V
`include "define_readout_rx_circuit.v"
`endif

module readout_rx_calibration_unit #(
    parameter IQ_CALI_WIDTH = 9,
    parameter IQ_CALI_OUT_WIDTH = 16
)(
    clk,

    i_in,
    q_in,
  
    alpha_i,
    beta_i,
    alpha_q,
    beta_q,
    dc_correction,
    valid_in,

    i_out,
    q_out,
    valid_out
);

localparam DC_CORRECTION_OUT_WIDTH = IQ_CALI_WIDTH +1;
localparam MULT_OUT_WIDTH = IQ_CALI_OUT_WIDTH -1;

input                                     clk;

input      signed [IQ_CALI_WIDTH-1:0]     i_in;
input      signed [IQ_CALI_WIDTH-1:0]     q_in;

input      signed [IQ_CALI_WIDTH-1:0]     alpha_i;
input      signed [IQ_CALI_WIDTH-1:0]     beta_i;
input      signed [IQ_CALI_WIDTH-1:0]     alpha_q;
input      signed [IQ_CALI_WIDTH-1:0]     beta_q; 
input      signed [IQ_CALI_WIDTH-1:0]     dc_correction; 
input                                     valid_in;

output reg signed [IQ_CALI_OUT_WIDTH-1:0] i_out;
output reg signed [IQ_CALI_OUT_WIDTH-1:0] q_out;
output reg                                valid_out;

// Port declaration

wire signed [MULT_OUT_WIDTH-1:0]              i_alpha_i_multiplier_out;
wire signed [MULT_OUT_WIDTH-1:0]              i_beta_i_multiplier_out;
wire signed [MULT_OUT_WIDTH-1:0]              q_alpha_q_multiplier_out;
wire signed [MULT_OUT_WIDTH-1:0]              q_beta_q_multiplier_out;
reg  signed [MULT_OUT_WIDTH-1:0]              i_alpha_i_multiplier;
reg  signed [MULT_OUT_WIDTH-1:0]              i_beta_i_multiplier;
reg  signed [MULT_OUT_WIDTH-1:0]              q_alpha_q_multiplier;
reg  signed [MULT_OUT_WIDTH-1:0]              q_beta_q_multiplier;

wire signed [IQ_CALI_OUT_WIDTH-1:0]           i_alpha_beta_adder_out;
wire signed [IQ_CALI_OUT_WIDTH-1:0]           q_alpha_beta_adder_out;

wire signed [DC_CORRECTION_OUT_WIDTH-1:0]     i_dc_adder_out;
wire signed [DC_CORRECTION_OUT_WIDTH-1:0]     q_dc_adder_out;
reg  signed [DC_CORRECTION_OUT_WIDTH-1:0]     i_dc_adder;
reg  signed [DC_CORRECTION_OUT_WIDTH-1:0]     q_dc_adder;

// wire signed [DC_CORRECTION_OUT_WIDTH-1:0]     alpha_i_sign_extend;
// wire signed [DC_CORRECTION_OUT_WIDTH-1:0]     beta_i_sign_extend;
// wire signed [DC_CORRECTION_OUT_WIDTH-1:0]     alpha_q_sign_extend;
// wire signed [DC_CORRECTION_OUT_WIDTH-1:0]     beta_q_sign_extend;
reg  signed [DC_CORRECTION_OUT_WIDTH-1:0]     alpha_i_sign_extend;
reg  signed [DC_CORRECTION_OUT_WIDTH-1:0]     beta_i_sign_extend;
reg  signed [DC_CORRECTION_OUT_WIDTH-1:0]     alpha_q_sign_extend;
reg  signed [DC_CORRECTION_OUT_WIDTH-1:0]     beta_q_sign_extend;

// Combinational Logic

// add dc_correction
adder_signed_param #(
    .DATA_IN_WIDTH(IQ_CALI_WIDTH),
    .DATA_OUT_WIDTH(DC_CORRECTION_OUT_WIDTH),
    .TAKE_MSB(1)
) i_dc_correction_adder (
    .data_in_1(i_in),
    .data_in_2(dc_correction),
    .data_out(i_dc_adder_out)
);

adder_signed_param #(
    .DATA_IN_WIDTH(IQ_CALI_WIDTH),
    .DATA_OUT_WIDTH(DC_CORRECTION_OUT_WIDTH),
    .TAKE_MSB(1)
) q_dc_correction_adder (
    .data_in_1(q_in),
    .data_in_2(dc_correction),
    .data_out(q_dc_adder_out)
);

// assign alpha_i_sign_extend = {alpha_i[IQ_CALI_WIDTH-1], alpha_i};
// assign beta_i_sign_extend = {beta_i[IQ_CALI_WIDTH-1], beta_i};
// assign alpha_q_sign_extend = {alpha_q[IQ_CALI_WIDTH-1], alpha_q};
// assign beta_q_sign_extend = {beta_q[IQ_CALI_WIDTH-1], beta_q};

reg valid_dc_adder;
always @(posedge clk) begin
    i_dc_adder <= i_dc_adder_out;
    q_dc_adder <= q_dc_adder_out;

    alpha_i_sign_extend <= {alpha_i[IQ_CALI_WIDTH-1], alpha_i};
    beta_i_sign_extend <= {beta_i[IQ_CALI_WIDTH-1], beta_i};
    alpha_q_sign_extend <= {alpha_q[IQ_CALI_WIDTH-1], alpha_q};
    beta_q_sign_extend <= {beta_q[IQ_CALI_WIDTH-1], beta_q};
    
    valid_dc_adder <= valid_in;
end

// multiply alpha_i, beta_i, alpha_q, beta_q
/*
multiplier_signed_param #(
    .DATA_IN_WIDTH(DC_CORRECTION_OUT_WIDTH),
    .DATA_OUT_WIDTH(MULT_OUT_WIDTH),
    .TAKE_MSB(1)
) i_alpha_i_multiplier_instance (
    .data_in_1(i_dc_adder),
    .data_in_2(alpha_i_sign_extend),
    .data_out(i_alpha_i_multiplier_out)
);

multiplier_signed_param #(
    .DATA_IN_WIDTH(DC_CORRECTION_OUT_WIDTH),
    .DATA_OUT_WIDTH(MULT_OUT_WIDTH),
    .TAKE_MSB(1)
) i_beta_i_multiplier_instance (
    .data_in_1(i_dc_adder),
    .data_in_2(beta_i_sign_extend),
    .data_out(i_beta_i_multiplier_out)
);

multiplier_signed_param #(
    .DATA_IN_WIDTH(DC_CORRECTION_OUT_WIDTH),
    .DATA_OUT_WIDTH(MULT_OUT_WIDTH),
    .TAKE_MSB(1)
) q_alpha_q_multiplier_instance (
    .data_in_1(q_dc_adder),
    .data_in_2(alpha_q_sign_extend),
    .data_out(q_alpha_q_multiplier_out)
);

multiplier_signed_param #(
    .DATA_IN_WIDTH(DC_CORRECTION_OUT_WIDTH),
    .DATA_OUT_WIDTH(MULT_OUT_WIDTH),
    .TAKE_MSB(1)
) q_beta_q_multiplier_instance (
    .data_in_1(q_dc_adder),
    .data_in_2(beta_q_sign_extend),
    .data_out(q_beta_q_multiplier_out)
);

reg valid_alpha_beta_adder;
always @(posedge clk) begin
    i_alpha_i_multiplier <= i_alpha_i_multiplier_out;
    i_beta_i_multiplier <= i_beta_i_multiplier_out;
    q_alpha_q_multiplier <= q_alpha_q_multiplier_out;
    q_beta_q_multiplier <= q_beta_q_multiplier_out;

    valid_alpha_beta_adder <= valid_dc_adder;
end
*/

multiplier_signed_opt_param #(
    .DATA_IN_WIDTH(DC_CORRECTION_OUT_WIDTH),
    .DATA_OUT_WIDTH(MULT_OUT_WIDTH)
) i_alpha_i_multiplier_instance (
    .data_in_1(i_dc_adder),
    .data_in_2(alpha_i_sign_extend),
    .data_out(i_alpha_i_multiplier_out)
);

multiplier_signed_opt_param #(
    .DATA_IN_WIDTH(DC_CORRECTION_OUT_WIDTH),
    .DATA_OUT_WIDTH(MULT_OUT_WIDTH)
) i_beta_i_multiplier_instance (
    .data_in_1(i_dc_adder),
    .data_in_2(beta_i_sign_extend),
    .data_out(i_beta_i_multiplier_out)
);

multiplier_signed_opt_param #(
    .DATA_IN_WIDTH(DC_CORRECTION_OUT_WIDTH),
    .DATA_OUT_WIDTH(MULT_OUT_WIDTH)
) q_alpha_q_multiplier_instance (
    .data_in_1(q_dc_adder),
    .data_in_2(alpha_q_sign_extend),
    .data_out(q_alpha_q_multiplier_out)
);

multiplier_signed_opt_param #(
    .DATA_IN_WIDTH(DC_CORRECTION_OUT_WIDTH),
    .DATA_OUT_WIDTH(MULT_OUT_WIDTH)
) q_beta_q_multiplier_instance (
    .data_in_1(q_dc_adder),
    .data_in_2(beta_q_sign_extend),
    .data_out(q_beta_q_multiplier_out)
);

reg valid_alpha_beta_adder;
always @(posedge clk) begin
    i_alpha_i_multiplier <= i_alpha_i_multiplier_out;
    i_beta_i_multiplier <= i_beta_i_multiplier_out;
    q_alpha_q_multiplier <= q_alpha_q_multiplier_out;
    q_beta_q_multiplier <= q_beta_q_multiplier_out;

    valid_alpha_beta_adder <= valid_dc_adder;
end

//
adder_signed_param #(
    .DATA_IN_WIDTH(MULT_OUT_WIDTH),
    .DATA_OUT_WIDTH(IQ_CALI_OUT_WIDTH),
    .TAKE_MSB(1)
) i_alpha_beta_adder_instance (
    .data_in_1(i_alpha_i_multiplier),
    .data_in_2(q_beta_q_multiplier),
    .data_out(i_alpha_beta_adder_out)
);

adder_signed_param #(
    .DATA_IN_WIDTH(MULT_OUT_WIDTH),
    .DATA_OUT_WIDTH(IQ_CALI_OUT_WIDTH),
    .TAKE_MSB(1)
) q_alpha_beta_adder_instance (
    .data_in_1(q_alpha_q_multiplier),
    .data_in_2(i_beta_i_multiplier),
    .data_out(q_alpha_beta_adder_out)
);

// reg valid_iq_adder;
// always @(posedge clk) begin
//     i_alpha_beta_adder <= i_alpha_beta_adder_out;
//     q_alpha_beta_adder <= q_alpha_beta_adder_out;

//     valid_iq_adder <= valid_alpha_beta_adder;
// end

// Combinational read
always @(*) begin
    i_out = i_alpha_beta_adder_out;
    q_out = q_alpha_beta_adder_out;

    valid_out = valid_alpha_beta_adder;
end

endmodule
