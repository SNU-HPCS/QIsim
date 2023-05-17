module random_access_mem_valid #(
    parameter NUM_ENTRY = 16, 
    parameter ADDR_WIDTH = 4
)(
    clk,
    rst,
    wr_en,
    wr_addr, 
    wr_data, 
    rd_addr,
    rd_data 
);

input clk; 
input rst;
input wr_en;
input [ADDR_WIDTH-1:0] wr_addr; 
input [0:0] wr_data; 
input [ADDR_WIDTH-1:0] rd_addr;
output [0:0] rd_data; 

reg [NUM_ENTRY-1:0] valid_bits;

// Sequential write
always @ (posedge clk)
begin
    if (rst)
        valid_bits <= 0;
    else if (wr_en)
        valid_bits[wr_addr] <= wr_data;
end

// Combinational read
assign rd_data = valid_bits[rd_addr];

endmodule 
