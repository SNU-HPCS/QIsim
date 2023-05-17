`define NUM_ENTRY 1024
`define ADDR_WIDTH 10 
`define DATA_WIDTH 16

module sin_lut_n1024_16b_tb ();

reg clk; 
reg [`ADDR_WIDTH-1:0] rd_addr;
wire [`DATA_WIDTH-1:0] rd_data; 

integer I, J;

sin_lut_n1024_16b UUT (
    .clk(clk),
    .rd_addr(rd_addr),
    .rd_data(rd_data)
);

always #10 clk = ~clk;

initial begin
    $dumpfile("sin_lut_n1024_16b.vcd");
    $dumpvars(0, sin_lut_n1024_16b_tb);
    
    clk = 0;
    rd_addr = 0;
    #10;
    for (I=0; I<`NUM_ENTRY; I=I+1)
    begin
        #20;
        rd_addr = rd_addr + 1;
    end

    // Answer
    // one sine wave (0~2pi)
    
    #20;
    $finish;
end


endmodule

