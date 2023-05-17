module ff #(
    parameter DATA_WIDTH = 16
)(
    clk,
    rst,
    wr_en, 
    wr_data, 
    rd_data
);

input clk; 
input rst; 
input wr_en;
input [DATA_WIDTH-1:0] wr_data; 
output [DATA_WIDTH-1:0] rd_data; 

reg [DATA_WIDTH-1:0] register;

// Sequential write
always @ (posedge clk)
begin
    if (rst)
        register <= 0;
    else if (wr_en)
        register <= wr_data;
end

// Combinational read
assign rd_data = register;

endmodule