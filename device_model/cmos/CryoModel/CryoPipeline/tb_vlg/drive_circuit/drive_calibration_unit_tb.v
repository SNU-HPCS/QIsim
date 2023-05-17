`timescale 1ns/100ps

`define IQ_CALI_WIDTH 9
`define IQ_OUT_WIDTH 9

module drive_calibration_unit_tb();

parameter IQ_CALI_WIDTH = `IQ_CALI_WIDTH;
parameter IQ_OUT_WIDTH = `IQ_OUT_WIDTH;

localparam CALI_MEMORY_DATA_WIDTH = IQ_CALI_WIDTH*4;

parameter NUM_ENTRY = 1024;
parameter NUM_ITER = 4096;

reg                           clk;
reg                           rst;

reg     [IQ_CALI_WIDTH-1:0]   i_in;
reg     [IQ_CALI_WIDTH-1:0]   q_in;

reg     [IQ_CALI_WIDTH-1:0]   alpha_i;
reg     [IQ_CALI_WIDTH-1:0]   beta_i;
reg     [IQ_CALI_WIDTH-1:0]   alpha_q;
reg     [IQ_CALI_WIDTH-1:0]   beta_q; 
reg     [IQ_CALI_WIDTH-1:0]   dc_correction; 

wire    [IQ_OUT_WIDTH-1:0]    i_out;
wire    [IQ_OUT_WIDTH-1:0]    q_out;

reg     [IQ_CALI_WIDTH-1:0]   sin_mem [0:NUM_ENTRY-1];
reg     [IQ_CALI_WIDTH-1:0]   cos_mem [0:NUM_ENTRY-1];


drive_calibration_unit #(
    .IQ_CALI_WIDTH(IQ_CALI_WIDTH),
    .IQ_OUT_WIDTH(IQ_OUT_WIDTH)
) UUT (
    .i_in(i_in),
    .q_in(q_in),
    .alpha_i(alpha_i),
    .beta_i(beta_i),
    .alpha_q(alpha_q),
    .beta_q(beta_q),
    .dc_correction(dc_correction),
    .i_out(i_out),
    .q_out(q_out)
);

integer I, J;

always #10 clk = ~clk;

initial begin
    $dumpfile("drive_calibration_unit.vcd");
    $dumpvars(0, drive_calibration_unit_tb);

    clk = 1'b0;
    rst = 1'b0;

    i_in = `IQ_CALI_WIDTH'b0_0000_0000;
    q_in = `IQ_CALI_WIDTH'b0_0000_0000;
    alpha_i = `IQ_CALI_WIDTH'b0_0000_0000;
    beta_i = `IQ_CALI_WIDTH'b0_0000_0000;
    alpha_q = `IQ_CALI_WIDTH'b0_0000_0000;
    beta_q = `IQ_CALI_WIDTH'b0_0000_0000;
    dc_correction = `IQ_CALI_WIDTH'b0_0000_0000;
    
    #5;
    rst = 1;
    #10;
    rst = 0;
    #5;
    
    // Without correction
    alpha_i = `IQ_CALI_WIDTH'b1_1111_1111;
    beta_i = `IQ_CALI_WIDTH'b0_0000_0000;
    alpha_q = `IQ_CALI_WIDTH'b1_1111_1111;
    beta_q = `IQ_CALI_WIDTH'b0_0000_0000;
    dc_correction = `IQ_CALI_WIDTH'b0_0000_0000;

    for (I=0; I<NUM_ITER; I=I+1)
    begin
        i_in = sin_mem[I[9:0]];
        q_in = cos_mem[I[9:0]];
        #20;
    end

    // With correction
    alpha_i = `IQ_CALI_WIDTH'b1_0000_0000;
    beta_i = `IQ_CALI_WIDTH'b1_0000_0000;
    alpha_q = `IQ_CALI_WIDTH'b1_0000_0000;
    beta_q = `IQ_CALI_WIDTH'b1_0000_0000;
    dc_correction = `IQ_CALI_WIDTH'b0_0000_0000;

    for (I=0; I<NUM_ITER; I=I+1)
    begin
        i_in = sin_mem[I[9:0]];
        q_in = cos_mem[I[9:0]];
        #20;
    end


    #20;
    $finish;
end

// memory initialization
initial begin
    $readmemh("sin_n1024_9b.mem", sin_mem, 0, NUM_ENTRY-1);
    $readmemh("cos_n1024_9b.mem", cos_mem, 0, NUM_ENTRY-1);
end

endmodule

/* Expected result */
/*
1) Without correction
-> i_in == i_out
-> q_in == q_out

2) With correction
-> i_out == q_out
*/