module readout_rx_bin_accumulator_intel_opt #(
    parameter BIN_COUNTER_WIDTH = 16
)(
    clk,
    rst,

    count_condition,

    start_count,
    valid_in,

    bin_count_out
);

input clk;
input rst;

input count_condition;

input start_count;
input valid_in;

output [BIN_COUNTER_WIDTH-1:0] bin_count_out;


wire [BIN_COUNTER_WIDTH-1:0] bin_count_p1;
wire [BIN_COUNTER_WIDTH-1:0] bin_count_m1;

wire [BIN_COUNTER_WIDTH-1:0] next_bin_count;

wire bin_count_ff_wr_en;
wire [BIN_COUNTER_WIDTH-1:0] bin_count_ff_wr_data;
wire [BIN_COUNTER_WIDTH-1:0] bin_count_ff_rd_data;

adder_param #(
    .DATA_IN_WIDTH(BIN_COUNTER_WIDTH),
    .DATA_INTERMEDIATE_WIDTH(BIN_COUNTER_WIDTH),
    .DATA_OUT_WIDTH(BIN_COUNTER_WIDTH),
    .TAKE_MSB(0)
) bin_count_p1_adder (
    .data_in_1(bin_count_ff_rd_data),
    .data_in_2({{(BIN_COUNTER_WIDTH-1){1'b0}}, 1'b1}),
    .data_out(bin_count_p1)
);
subtractor_param #(
    .DATA_IN_WIDTH(BIN_COUNTER_WIDTH),
    .DATA_INTERMEDIATE_WIDTH(BIN_COUNTER_WIDTH),
    .DATA_OUT_WIDTH(BIN_COUNTER_WIDTH),
    .TAKE_MSB(0)
) bin_count_m1_subtractor (
    .data_in_1(bin_count_ff_rd_data),
    .data_in_2({{(BIN_COUNTER_WIDTH-1){1'b0}}, 1'b1}),
    .data_out(bin_count_m1)
);
assign next_bin_count = count_condition ? (bin_count_p1) : (bin_count_m1);

assign bin_count_ff_wr_en = (start_count | valid_in);
assign bin_count_ff_wr_data = start_count ? {1'b1, {(BIN_COUNTER_WIDTH-1){1'b0}}} : next_bin_count;
ff #(
    .DATA_WIDTH(BIN_COUNTER_WIDTH)
) bin_count_ff (
    .clk(clk),
    .rst(rst),
    .wr_en(bin_count_ff_wr_en), 
    .wr_data(bin_count_ff_wr_data), 
    .rd_data(bin_count_ff_rd_data)
);
assign bin_count_out = bin_count_ff_rd_data;

endmodule