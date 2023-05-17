`define MAX_COUNT 14
`define COUNT_WIDTH 4

module counter_param_tb();


reg clk, en, rst; 
wire [`COUNT_WIDTH-1:0] count;

counter_param #(
    .MAX_COUNT(`MAX_COUNT),
    .COUNT_WIDTH(`COUNT_WIDTH)
) UUT(
    .clk(clk),
    .en(en),
    .rst(rst),
    .count(count)
);

always #10 clk = ~clk;

initial begin
    $dumpfile("counter_param.vcd");
    $dumpvars(0, counter_param_tb);

    clk = 0;
    rst = 0;
    en = 0; 

    #5;
    rst = 1;
    #10; 
    rst = 0;
    #5; 

    en = 1;
    
    #320;
    $finish;
end

// Answer
// count sequentially changes from 0 to 14

endmodule
