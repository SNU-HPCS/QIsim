`timescale 1ns/100ps

module down_mixer_tb();

parameter INPUT_WIDTH = 16;
parameter OUTPUT_WIDTH = 16;

//
reg clk;
//
reg   [INPUT_WIDTH-1:0]   i_in_1;
reg   [INPUT_WIDTH-1:0]   q_in_1;
reg   [INPUT_WIDTH-1:0]   i_in_2;
reg   [INPUT_WIDTH-1:0]   q_in_2;
wire  [OUTPUT_WIDTH-1:0]  i_out;
wire  [OUTPUT_WIDTH-1:0]  q_out;

//
localparam SIN_LUT_DATA_WIDTH_0   = 8;
localparam SIN_LUT_DATA_WIDTH_1   = 16;
localparam SIN_LUT_NUM_ENTRY_0  = 1024;
localparam SIN_LUT_NUM_ENTRY_1  = 1536;

localparam NUM_ITER             = 3072;

reg [SIN_LUT_DATA_WIDTH_0-1:0]          sin_lut_n1024_mem_0 [0:SIN_LUT_NUM_ENTRY_0-1];
reg [SIN_LUT_DATA_WIDTH_1-1:0]          sin_lut_n1024_mem_1 [0:SIN_LUT_NUM_ENTRY_0-1];
reg [SIN_LUT_DATA_WIDTH_0-1:0]          cos_lut_n1024_mem_0 [0:SIN_LUT_NUM_ENTRY_0-1];
reg [SIN_LUT_DATA_WIDTH_1-1:0]          cos_lut_n1024_mem_1 [0:SIN_LUT_NUM_ENTRY_0-1];

reg [SIN_LUT_DATA_WIDTH_0-1:0]          sin_lut_n1536_mem_0 [0:SIN_LUT_NUM_ENTRY_1-1];
reg [SIN_LUT_DATA_WIDTH_1-1:0]          sin_lut_n1536_mem_1 [0:SIN_LUT_NUM_ENTRY_1-1];
reg [SIN_LUT_DATA_WIDTH_0-1:0]          cos_lut_n1536_mem_0 [0:SIN_LUT_NUM_ENTRY_1-1];
reg [SIN_LUT_DATA_WIDTH_1-1:0]          cos_lut_n1536_mem_1 [0:SIN_LUT_NUM_ENTRY_1-1];

reg [9:0] addr_0;
reg [10:0] addr_1;

down_mixer #(
    .INPUT_WIDTH(INPUT_WIDTH),
    .OUTPUT_WIDTH(OUTPUT_WIDTH)
) UUT (
    .i_in_1(i_in_1),
    .q_in_1(q_in_1),
    .i_in_2(i_in_2),
    .q_in_2(q_in_2),
    .i_out(i_out),
    .q_out(q_out)
);

integer I, J;

always #10 clk = ~clk;

initial begin
    $dumpfile("down_mixer.vcd");
    $dumpvars(0, down_mixer_tb);

    clk = 0;
    i_in_1 = 0;
    q_in_1 = 0;
    i_in_2 = 0;
    q_in_2 = 0;
    #20; 
    
    addr_0 = 0;
    addr_1 = 0;

    for (J=0; J< 4; J=J+1) begin
        addr_0 = J*128;
        addr_1 = 0;
        for (I=0; I< NUM_ITER; I=I+1) begin
            i_in_1 = {{(SIN_LUT_DATA_WIDTH_1-SIN_LUT_DATA_WIDTH_0){cos_lut_n1024_mem_0[addr_0][SIN_LUT_DATA_WIDTH_0-1]}}, cos_lut_n1024_mem_0[addr_0]};
            q_in_1 = {{(SIN_LUT_DATA_WIDTH_1-SIN_LUT_DATA_WIDTH_0){sin_lut_n1024_mem_0[addr_0][SIN_LUT_DATA_WIDTH_0-1]}}, sin_lut_n1024_mem_0[addr_0]};
            i_in_2 = cos_lut_n1024_mem_1[addr_1];
            q_in_2 = sin_lut_n1024_mem_1[addr_1];
            #20;
            if (addr_0 >= SIN_LUT_NUM_ENTRY_0-1) addr_0 = 0;
            else addr_0 = addr_0 +1;

            // if (addr_1 >= SIN_LUT_NUM_ENTRY_1-1) addr_1 = 0;
            if (addr_1 >= SIN_LUT_NUM_ENTRY_0-1) addr_1 = 0;
            else addr_1 = addr_1 +1;
        end
    end

    #20;
    $finish;
end

// memory initialization
initial begin
    $readmemh("signed_sin_n1024_8b.mem", sin_lut_n1024_mem_0, 0, SIN_LUT_NUM_ENTRY_0-1);
    $readmemh("signed_sin_n1024_16b.mem", sin_lut_n1024_mem_1, 0, SIN_LUT_NUM_ENTRY_0-1);
    $readmemh("signed_cos_n1024_8b.mem", cos_lut_n1024_mem_0, 0, SIN_LUT_NUM_ENTRY_0-1);
    $readmemh("signed_cos_n1024_16b.mem", cos_lut_n1024_mem_1, 0, SIN_LUT_NUM_ENTRY_0-1);

    // $readmemh("signed_sin_n1536_16b.mem", sin_lut_n1536_mem_0, 0, SIN_LUT_NUM_ENTRY_1-1);
    // $readmemh("signed_sin_n1536_16b.mem", sin_lut_n1536_mem_1, 0, SIN_LUT_NUM_ENTRY_1-1);
    // $readmemh("signed_cos_n1536_16b.mem", cos_lut_n1536_mem_0, 0, SIN_LUT_NUM_ENTRY_1-1);
    // $readmemh("signed_cos_n1536_16b.mem", cos_lut_n1536_mem_1, 0, SIN_LUT_NUM_ENTRY_1-1);
end

endmodule

/* Expected result */
/*
*/