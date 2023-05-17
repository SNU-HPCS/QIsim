
`include "define_pulse_circuit.v"

module pulse_length_counter #(
    parameter LENGTH_WIDTH = 7
)(
    clk,
    rst,

    set_counter,
    length_in,

    cur_count_out,
    counter_running
);

localparam COUNTER_WIDTH = LENGTH_WIDTH;

/* Port declaration */
input                           clk;
input                           rst;

input                           set_counter;

input   [LENGTH_WIDTH-1:0]      length_in;

output  [COUNTER_WIDTH-1:0]     cur_count_out;
output                          counter_running;

/* Wire/reg declaration */

//
wire                            length_count_reg_wr_en;
wire    [COUNTER_WIDTH-1:0]     length_count_reg_wr_data;
wire    [COUNTER_WIDTH-1:0]     length_count_reg_rd_data;

wire [COUNTER_WIDTH-1:0] length_count_comparator_in_1;
wire [COUNTER_WIDTH-1:0] length_count_comparator_in_2;
wire length_count_comparator_out;

wire [COUNTER_WIDTH-1:0] length_count_m1;

wire [2*COUNTER_WIDTH-1:0]  mux_next_length_count_data_in;
wire                        mux_next_length_count_sel;
wire [COUNTER_WIDTH-1:0]    mux_next_length_count_data_out;


//
assign length_count_reg_wr_en = length_count_comparator_out | set_counter;
assign length_count_reg_wr_data = mux_next_length_count_data_out;

ff #(
    .DATA_WIDTH(COUNTER_WIDTH)
) length_count_reg (
    .clk(clk),
    .rst(rst),
    .wr_en(length_count_reg_wr_en), 
    .wr_data(length_count_reg_wr_data), 
    .rd_data(length_count_reg_rd_data)
);

//
assign length_count_m1 = length_count_reg_rd_data -1;

//

assign mux_next_length_count_data_in = {length_in, length_count_m1};
assign mux_next_length_count_sel = set_counter;

mux_param #(
    .NUM_INPUT(2),
    .SEL_WIDTH(1),
    .DATA_WIDTH(COUNTER_WIDTH)
) mux_next_length_count (
    .data_in(mux_next_length_count_data_in), 
    .sel(mux_next_length_count_sel),
    .data_out(mux_next_length_count_data_out)
);

//


assign length_count_comparator_in_1 = length_count_reg_rd_data;
assign length_count_comparator_in_2 = {COUNTER_WIDTH{1'b0}};

comparator_param #(
    .DATA_WIDTH(COUNTER_WIDTH)
) length_count_comparator (
    .data_in_1(length_count_comparator_in_1), 
    .data_in_2(length_count_comparator_in_2), 
    .data_out(length_count_comparator_out)
);


//
assign cur_count_out = length_count_reg_rd_data;
assign counter_running = length_count_comparator_out;

endmodule
