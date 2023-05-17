module sin_lut_param #(
    parameter NUM_ENTRY = 1024, 
    parameter ADDR_WIDTH = 10, 
    parameter DATA_WIDTH = 16
)(
    clk,
    wr_en,
    wr_addr, 
    wr_data, 
    rd_addr,
    rd_data
);

input clk; 
input wr_en;
input [ADDR_WIDTH-1:0] wr_addr; 
input [DATA_WIDTH-1:0] wr_data; 
input [ADDR_WIDTH-1:0] rd_addr;
output [DATA_WIDTH-1:0] rd_data; 

reg [DATA_WIDTH-1:0] register [0:NUM_ENTRY-1];

// Sequential write
always @ (posedge clk)
begin
    if (wr_en)
        register[wr_addr] <= wr_data;
end

// Combinational read
assign rd_data = register[rd_addr];

// initial begin
    // $readmemh("sin_n1024_8b.mem", register, 0, NUM_ENTRY-1); // File with the signal
    // $readmemh("signed_sin_n1024_16b.mem", register, 0, NUM_ENTRY-1); // File with the signal
// end    

endmodule