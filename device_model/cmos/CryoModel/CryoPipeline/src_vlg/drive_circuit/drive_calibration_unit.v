module drive_calibration_unit #(
    parameter IQ_CALI_WIDTH = 9,
    parameter IQ_OUT_WIDTH = 9
)(
    clk,
    
    i_in,
    q_in,
    valid_in,

    alpha_i,
    beta_i,
    alpha_q,
    beta_q,
    dc_correction,

    i_out,
    q_out,
    valid_out
);

localparam CALI_MEMORY_DATA_WIDTH = IQ_CALI_WIDTH*4;

input                               clk;

input       [IQ_CALI_WIDTH-1:0]     i_in;
input       [IQ_CALI_WIDTH-1:0]     q_in;
input                               valid_in;

input       [IQ_CALI_WIDTH-1:0]     alpha_i;
input       [IQ_CALI_WIDTH-1:0]     beta_i;
input       [IQ_CALI_WIDTH-1:0]     alpha_q;
input       [IQ_CALI_WIDTH-1:0]     beta_q; 
input       [IQ_CALI_WIDTH-1:0]     dc_correction; 

output reg  [IQ_OUT_WIDTH-1:0]      i_out;
output reg  [IQ_OUT_WIDTH-1:0]      q_out;
output reg  [0:0]                   valid_out;

// Port declaration

wire [IQ_CALI_WIDTH-1:0]            i_alpha_i_multiplier_out;
wire [IQ_CALI_WIDTH-1:0]            i_beta_i_multiplier_out;
wire [IQ_CALI_WIDTH-1:0]            q_alpha_q_multiplier_out;
wire [IQ_CALI_WIDTH-1:0]            q_beta_q_multiplier_out;
reg  [IQ_CALI_WIDTH-1:0]            i_alpha_i_multiplier;
reg  [IQ_CALI_WIDTH-1:0]            i_beta_i_multiplier;
reg  [IQ_CALI_WIDTH-1:0]            q_alpha_q_multiplier;
reg  [IQ_CALI_WIDTH-1:0]            q_beta_q_multiplier;

wire [IQ_CALI_WIDTH-1:0]            i_alpha_beta_adder_out;
wire [IQ_CALI_WIDTH-1:0]            q_alpha_beta_adder_out;
reg  [IQ_CALI_WIDTH-1:0]            i_alpha_beta_adder;
reg  [IQ_CALI_WIDTH-1:0]            q_alpha_beta_adder;

wire [IQ_OUT_WIDTH-1:0]             i_dc_adder_out;
wire [IQ_OUT_WIDTH-1:0]             q_dc_adder_out;
reg  [IQ_OUT_WIDTH-1:0]             i_dc_adder;
reg  [IQ_OUT_WIDTH-1:0]             q_dc_adder;

// Combinational Logic

// multiply alpha_i, beta_i, alpha_q, beta_q
multiplier_param #(
    .DATA_IN_WIDTH(IQ_CALI_WIDTH),
    .DATA_OUT_WIDTH(IQ_CALI_WIDTH),
    .TAKE_MSB(1)
) i_alpha_i_multiplier_instance (
    .data_in_1(i_in),
    .data_in_2(alpha_i),
    .data_out(i_alpha_i_multiplier_out)
);

multiplier_param #(
    .DATA_IN_WIDTH(IQ_CALI_WIDTH),
    .DATA_OUT_WIDTH(IQ_CALI_WIDTH),
    .TAKE_MSB(1)
) i_beta_i_multiplier_instance (
    .data_in_1(i_in),
    .data_in_2(beta_i),
    .data_out(i_beta_i_multiplier_out)
);

multiplier_param #(
    .DATA_IN_WIDTH(IQ_CALI_WIDTH),
    .DATA_OUT_WIDTH(IQ_CALI_WIDTH),
    .TAKE_MSB(1)
) q_alpha_q_multiplier_instance (
    .data_in_1(q_in),
    .data_in_2(alpha_q),
    .data_out(q_alpha_q_multiplier_out)
);

multiplier_param #(
    .DATA_IN_WIDTH(IQ_CALI_WIDTH),
    .DATA_OUT_WIDTH(IQ_CALI_WIDTH),
    .TAKE_MSB(1)
) q_beta_q_multiplier_instance (
    .data_in_1(q_in),
    .data_in_2(beta_q),
    .data_out(q_beta_q_multiplier_out)
);

reg valid_multiplier;
always @(posedge clk) begin
    i_alpha_i_multiplier <= i_alpha_i_multiplier_out;
    i_beta_i_multiplier <= i_beta_i_multiplier_out;
    q_alpha_q_multiplier <= q_alpha_q_multiplier_out;
    q_beta_q_multiplier <= q_beta_q_multiplier_out;
    valid_multiplier <= valid_in;
end

//
adder_param #(
    .DATA_IN_WIDTH(IQ_CALI_WIDTH),
    .DATA_OUT_WIDTH(IQ_CALI_WIDTH),
    .TAKE_MSB(1)
) i_alpha_beta_adder_instance (
    .data_in_1(i_alpha_i_multiplier),
    .data_in_2(q_beta_q_multiplier),
    .data_out(i_alpha_beta_adder_out)
);

adder_param #(
    .DATA_IN_WIDTH(IQ_CALI_WIDTH),
    .DATA_OUT_WIDTH(IQ_CALI_WIDTH),
    .TAKE_MSB(1)
) q_alpha_beta_adder_instance (
    .data_in_1(q_alpha_q_multiplier),
    .data_in_2(i_beta_i_multiplier),
    .data_out(q_alpha_beta_adder_out)
);

reg valid_adder;
always @(posedge clk) begin
    i_alpha_beta_adder <= i_alpha_beta_adder_out;
    q_alpha_beta_adder <= q_alpha_beta_adder_out;
    valid_adder <= valid_multiplier;
end

// add dc_correction
adder_param #(
    .DATA_IN_WIDTH(IQ_CALI_WIDTH),
    .DATA_OUT_WIDTH(IQ_OUT_WIDTH),
    .TAKE_MSB(1)
) i_dc_correction_adder (
    .data_in_1(i_alpha_beta_adder),
    .data_in_2(dc_correction),
    .data_out(i_dc_adder_out)
);

adder_param #(
    .DATA_IN_WIDTH(IQ_CALI_WIDTH),
    .DATA_OUT_WIDTH(IQ_OUT_WIDTH),
    .TAKE_MSB(1)
) q_dc_correction_adder (
    .data_in_1(q_alpha_beta_adder),
    .data_in_2(dc_correction),
    .data_out(q_dc_adder_out)
);

reg valid_dc_adder;
always @(posedge clk) begin
    i_dc_adder <= i_dc_adder_out;
    q_dc_adder <= q_dc_adder_out;
    valid_dc_adder <= valid_adder;
end

// Combinational read
always @(*) begin
    i_out = i_dc_adder;
    q_out = q_dc_adder;
    valid_out = valid_dc_adder;
end

endmodule
