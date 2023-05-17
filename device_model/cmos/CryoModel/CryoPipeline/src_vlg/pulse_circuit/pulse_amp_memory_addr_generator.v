
`include "define_pulse_circuit.v"

module pulse_amp_memory_addr_generator #(
    parameter DIRECTION_WIDTH = 2,
    parameter AMP_MEMORY_ADDR_WIDTH = 9
)(
    clk,
    rst,

    reset_addr,
    update_addr,

    direction_in,

    amp_memory_addr_out

);

localparam COUNTER_WIDTH = (AMP_MEMORY_ADDR_WIDTH - DIRECTION_WIDTH);

/* Port declaration */
input                               clk;
input                               rst;

input                               reset_addr;
input                               update_addr;

input   [DIRECTION_WIDTH-1:0]       direction_in;

output  [AMP_MEMORY_ADDR_WIDTH-1:0] amp_memory_addr_out;

/* Wire/reg declaration */

// /*
wire [COUNTER_WIDTH-1:0] current_count;

wire reset_amp_memory_addr_counter;
wire update_amp_memory_addr_counter;

assign reset_amp_memory_addr_counter = reset_addr | rst;
assign update_amp_memory_addr_counter = update_addr;

counter_param #(
    .COUNT_WIDTH(COUNTER_WIDTH)
) amp_memory_addr_counter (
    .clk(clk), 
    .rst(reset_amp_memory_addr_counter),
    .en(update_amp_memory_addr_counter),
    .count(current_count)
);
// */

/*
reg [COUNTER_WIDTH-1:0] current_count;

always @(posedge clk) begin
    if (rst) begin
        current_count <= 0;
    end
    else if (reset_addr) begin
        current_count <= 0;
    end
    else if (update_addr) begin
        current_count <= current_count +1;
    end
end
*/

assign amp_memory_addr_out = {direction_in, current_count};

endmodule
