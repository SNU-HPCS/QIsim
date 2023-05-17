module down_mixer #(
    parameter INPUT_WIDTH = 16,
    parameter OUTPUT_WIDTH = 16
)(
    i_in_1,
    q_in_1,
    i_in_2,
    q_in_2,
    i_out,
    q_out
);

localparam MULT_OUTPUT_WIDTH = OUTPUT_WIDTH;
// localparam MULT_OUTPUT_WIDTH = 2*INPUT_WIDTH;

// Port declaration
input  signed [INPUT_WIDTH-1:0]   i_in_1;
input  signed [INPUT_WIDTH-1:0]   q_in_1;
input  signed [INPUT_WIDTH-1:0]   i_in_2;
input  signed [INPUT_WIDTH-1:0]   q_in_2;
output signed [OUTPUT_WIDTH-1:0]  i_out;
output signed [OUTPUT_WIDTH-1:0]  q_out;

// wire   signed [INPUT_WIDTH-1:0]   i_in_1_offset;
// wire   signed [INPUT_WIDTH-1:0]   q_in_1_offset;
// wire   signed [INPUT_WIDTH-1:0]   i_in_2_offset;
// wire   signed [INPUT_WIDTH-1:0]   q_in_2_offset;
// wire   signed [OUTPUT_WIDTH-1:0]  i_out_offset;
// wire   signed [OUTPUT_WIDTH-1:0]  q_out_offset;

wire   signed [MULT_OUTPUT_WIDTH-1:0]  mult_out_i1_i2;
wire   signed [MULT_OUTPUT_WIDTH-1:0]  mult_out_q1_q2;
wire   signed [MULT_OUTPUT_WIDTH-1:0]  mult_out_q1_i2;
wire   signed [MULT_OUTPUT_WIDTH-1:0]  mult_out_i1_q2;

// assign i_in_1_offset = i_in_1 - {1'b1, {(INPUT_WIDTH-1){1'b0}}};
// assign q_in_1_offset = q_in_1 - {1'b1, {(INPUT_WIDTH-1){1'b0}}};
// assign i_in_2_offset = i_in_2 - {1'b1, {(INPUT_WIDTH-1){1'b0}}};
// assign q_in_2_offset = q_in_2 - {1'b1, {(INPUT_WIDTH-1){1'b0}}};
// assign i_out = i_out_offset + {1'b1, {(OUTPUT_WIDTH-1){1'b0}}};
// assign q_out = q_out_offset + {1'b1, {(OUTPUT_WIDTH-1){1'b0}}};

// multiply inputs each other
// multiplier_param #(
multiplier_signed_param #(
    .DATA_IN_WIDTH(INPUT_WIDTH),
    .DATA_OUT_WIDTH(MULT_OUTPUT_WIDTH),
    .TAKE_MSB(1)
) i1_i2_multiplier (
    .data_in_1(i_in_1),
    .data_in_2(i_in_2),
    .data_out(mult_out_i1_i2)
);

// multiplier_param #(
multiplier_signed_param #(
    .DATA_IN_WIDTH(INPUT_WIDTH),
    .DATA_OUT_WIDTH(MULT_OUTPUT_WIDTH),
    .TAKE_MSB(1)
) q1_q2_multiplier (
    .data_in_1(q_in_1),
    .data_in_2(q_in_2),
    .data_out(mult_out_q1_q2)
);

// multiplier_param #(
multiplier_signed_param #(
    .DATA_IN_WIDTH(INPUT_WIDTH),
    .DATA_OUT_WIDTH(MULT_OUTPUT_WIDTH),
    .TAKE_MSB(1)
) i1_q2_multiplier (
    .data_in_1(i_in_1),
    .data_in_2(q_in_2),
    .data_out(mult_out_i1_q2)
);

// multiplier_param #(
multiplier_signed_param #(
    .DATA_IN_WIDTH(INPUT_WIDTH),
    .DATA_OUT_WIDTH(MULT_OUTPUT_WIDTH),
    .TAKE_MSB(1)
) q1_i2_multiplier (
    .data_in_1(q_in_1),
    .data_in_2(i_in_2),
    .data_out(mult_out_q1_i2)
);

// add each multiplied pair
// adder_param #(
adder_signed_param #(
    .DATA_IN_WIDTH(MULT_OUTPUT_WIDTH),
    .DATA_OUT_WIDTH(OUTPUT_WIDTH),
    .TAKE_MSB(1)
) i_adder (
    .data_in_1(mult_out_i1_i2),
    .data_in_2(mult_out_q1_q2),
    .data_out(i_out)
);

// subtractor_param #(
// subtractor_param #(
subtractor_signed_param #(
    .DATA_IN_WIDTH(MULT_OUTPUT_WIDTH),
    .DATA_OUT_WIDTH(OUTPUT_WIDTH),
    .TAKE_MSB(1)
) q_subtractor (
    .data_in_1(mult_out_i1_q2),
    .data_in_2(mult_out_q1_i2),
    .data_out(q_out)
);

endmodule
