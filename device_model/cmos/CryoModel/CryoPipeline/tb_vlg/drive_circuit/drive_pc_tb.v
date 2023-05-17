`timescale 1ns/100ps

`define PC_WIDTH 11

module drive_pc_tb();

reg                     clk;
reg                     rst;
reg                     update_pc;
reg     [`PC_WIDTH-1:0]  next_PC;

wire    [`PC_WIDTH-1:0]  PC;

drive_pc #(
    .PC_WIDTH(`PC_WIDTH)
) UUT (
    .clk(clk),
    .rst(rst),
    .update_pc(update_pc),
    .next_PC(next_PC),
    .PC(PC)
);

integer I, J;

always #10 clk = ~clk;

always @(*) begin
    next_PC = PC +1;
end

initial begin
    $dumpfile("drive_pc.vcd");
    $dumpvars(0, drive_pc_tb);

    clk = 1'b0;
    rst = 1'b0;
    update_pc = 1'b0;
    #5;
    rst = 1;
    #10;
    rst = 0;
    #5;
    
    for (I=0; I<100; I=I+1)
    begin
        if (PC == I) $display("PASS: PC == %d, ANS == %d", PC, I);
        else $display("FAIL: PC == %d, ANS == %d", PC, I);
        update_pc = 1;
        #20;

        for (J=0; J<I; J=J+1)
        begin
            update_pc = 0;
            #20;
        end
    end
    
    #20;
    $finish;
end
endmodule

/* Expected result */
/*
Cycle: 0 -> PC = 0
Cycle: 1 -> PC = 1
Cycle: 2 -> PC = 2
Cycle: 3 -> PC = 2
Cycle: 4 -> PC = 3
Cycle: 5 -> PC = 3
Cycle: 6 -> PC = 3
Cycle: 7 -> PC = 4
Cycle: 8 -> PC = 4
Cycle: 9 -> PC = 4
Cycle:10 -> PC = 4
Cycle:11 -> PC = 5
...
*/