module readout_rx_bin_accumulator_google #(
    parameter DATA_WIDTH = 8,
    parameter ACCUMULATOR_WIDTH = (DATA_WIDTH + 10) // ACCUMULATOR_WIDTH >= DATA_WIDTH
)(
    clk,
    rst,

    start_count,

    valid_in,
    i_in,
    q_in,
    
    i_sum_out,
    q_sum_out
);

`ifdef POWER_OPTIMIZED_MULTIPLIER
    localparam DATA_INTERMEDIATE = DATA_WIDTH >> 1;
`else
    localparam DATA_INTERMEDIATE = DATA_WIDTH;
`endif


input clk;
input rst;

input start_count;

input valid_in;
input signed [DATA_WIDTH-1:0] i_in;
input signed [DATA_WIDTH-1:0] q_in;

output signed [(ACCUMULATOR_WIDTH-1):0] i_sum_out;
output signed [(ACCUMULATOR_WIDTH-1):0] q_sum_out;

wire signed [DATA_INTERMEDIATE-1:0] i_in_intermediate;
wire signed [DATA_INTERMEDIATE-1:0] q_in_intermediate;

wire signed [ACCUMULATOR_WIDTH-1:0] sign_extend_i_in;
wire signed [ACCUMULATOR_WIDTH-1:0] sign_extend_q_in;

reg signed [(ACCUMULATOR_WIDTH-1):0] i_sum;
reg signed [(ACCUMULATOR_WIDTH-1):0] q_sum;
wire signed [(ACCUMULATOR_WIDTH-1):0] i_sum_next;
wire signed [(ACCUMULATOR_WIDTH-1):0] q_sum_next;

// Value accumulation
assign i_in_intermediate = i_in[DATA_WIDTH-1 -: DATA_INTERMEDIATE]; // Take MSB
assign q_in_intermediate = q_in[DATA_WIDTH-1 -: DATA_INTERMEDIATE]; // Take MSB
assign sign_extend_i_in = {{(ACCUMULATOR_WIDTH-DATA_INTERMEDIATE){i_in_intermediate[DATA_INTERMEDIATE-1]}}, i_in_intermediate};
assign sign_extend_q_in = {{(ACCUMULATOR_WIDTH-DATA_INTERMEDIATE){q_in_intermediate[DATA_INTERMEDIATE-1]}}, q_in_intermediate};

// assign sign_extend_i_in = {{(ACCUMULATOR_WIDTH-DATA_WIDTH){i_in[DATA_WIDTH-1]}}, i_in};
// assign sign_extend_q_in = {{(ACCUMULATOR_WIDTH-DATA_WIDTH){q_in[DATA_WIDTH-1]}}, q_in};

adder_signed_param #(
    .DATA_IN_WIDTH (ACCUMULATOR_WIDTH),
    .DATA_INTERMEDIATE_WIDTH(ACCUMULATOR_WIDTH),
    .DATA_OUT_WIDTH (ACCUMULATOR_WIDTH),
    .TAKE_MSB (0)
) i_adder (
    .data_in_1 (sign_extend_i_in),
    .data_in_2 (i_sum),
    .data_out (i_sum_next)
);

adder_signed_param #(
    .DATA_IN_WIDTH (ACCUMULATOR_WIDTH),
    .DATA_INTERMEDIATE_WIDTH(ACCUMULATOR_WIDTH),
    .DATA_OUT_WIDTH (ACCUMULATOR_WIDTH),
    .TAKE_MSB (0)
) q_adder (
    .data_in_1 (sign_extend_q_in),
    .data_in_2 (q_sum),
    .data_out (q_sum_next)
);

always @(posedge clk) begin
    if (rst) begin
        i_sum <= 0;
        q_sum <= 0;
    end
    else if (start_count) begin
        i_sum <= sign_extend_i_in;
        q_sum <= sign_extend_q_in;
    end
    else if (valid_in) begin
        i_sum <= i_sum_next;
        q_sum <= q_sum_next;
    end
    else begin
        i_sum <= i_sum;
        q_sum <= q_sum;
    end
end

assign i_sum_out = i_sum;
assign q_sum_out = q_sum;

endmodule