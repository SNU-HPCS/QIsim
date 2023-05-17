`timescale 1ns/100ps

`define SIN_LUT_NUM_ENTRY 1024
`define SIN_LUT_ADDR_WIDTH 10
`define SIN_LUT_DATA_WIDTH 8
`define OUTPUT_WIDTH 9

module drive_polar_modulation_unit_tb();

parameter SIN_LUT_NUM_ENTRY = `SIN_LUT_NUM_ENTRY;
parameter SIN_LUT_ADDR_WIDTH = `SIN_LUT_ADDR_WIDTH;
parameter SIN_LUT_DATA_WIDTH = `SIN_LUT_DATA_WIDTH;
parameter OUTPUT_WIDTH = `OUTPUT_WIDTH;
localparam PHASE_WIDTH = SIN_LUT_ADDR_WIDTH;
localparam AMP_WIDTH = SIN_LUT_DATA_WIDTH;

parameter NUM_ENTRY = 16384;
// parameter NUM_ENTRY = 3072;

reg                               clk;
reg                               rst;
    
reg   [PHASE_WIDTH-1:0]           nco_phase;
reg   [PHASE_WIDTH-1:0]           enve_memory_phase;
reg   [AMP_WIDTH-1:0]             enve_memory_amp;
wire  [OUTPUT_WIDTH-1:0]          i_out;
wire  [OUTPUT_WIDTH-1:0]          q_out;

reg   [AMP_WIDTH-1:0]   enve_memory_gaussian [0:NUM_ENTRY-1];
reg   [PHASE_WIDTH-1:0]   phase_memory_const [0:NUM_ENTRY-1];
reg   [PHASE_WIDTH-1:0]   phase_memory_linear [0:NUM_ENTRY-1];


drive_polar_modulation_unit #(
    .SIN_LUT_NUM_ENTRY(SIN_LUT_NUM_ENTRY),
    .SIN_LUT_ADDR_WIDTH(SIN_LUT_ADDR_WIDTH),
    .SIN_LUT_DATA_WIDTH(SIN_LUT_DATA_WIDTH),
    .OUTPUT_WIDTH(OUTPUT_WIDTH)
) UUT (
    .nco_phase(nco_phase),
    .enve_memory_phase(enve_memory_phase),
    .enve_memory_amp(enve_memory_amp),
    .i_out(i_out),
    .q_out(q_out)
);

integer I, J;

always #10 clk = ~clk;

initial begin
    $dumpfile("drive_polar_modulation_unit.vcd");
    $dumpvars(0, drive_polar_modulation_unit_tb);

    clk = 1'b0;
    rst = 1'b0;

    nco_phase = `SIN_LUT_ADDR_WIDTH'b00_0000_0000;
    enve_memory_phase = `SIN_LUT_ADDR_WIDTH'b00_0000_0000;
    enve_memory_amp = `SIN_LUT_DATA_WIDTH'b0000_0000;

    #5;
    rst = 1;
    #10;
    rst = 0;
    #5;
    
    // envelope test
    for (I=0; I<NUM_ENTRY; I=I+1)
    begin
        enve_memory_amp = enve_memory_gaussian[I];
        enve_memory_phase = phase_memory_const[I];
        nco_phase = I[PHASE_WIDTH-1:0];
        #20;
    end

    // phase test
    for (I=0; I<NUM_ENTRY; I=I+1)
    begin
        enve_memory_amp = enve_memory_gaussian[I];
        // enve_memory_phase = phase_memory_linear[I];
        enve_memory_phase = I[PHASE_WIDTH-1:0];
        nco_phase = I[PHASE_WIDTH-1:0];
        #20;
    end


    #20;
    $finish;
end

// memory initialization
initial begin
    // $readmemh("gaussian_n3072_8b.mem", enve_memory_gaussian, 0, NUM_ENTRY-1);
    // $readmemh("const_n3072_10b.mem", phase_memory_const, 0, NUM_ENTRY-1);
    // $readmemh("linear_n3072_10b.mem", phase_memory_linear, 0, NUM_ENTRY-1);
    $readmemh("gaussian_n16384_8b.mem", enve_memory_gaussian, 0, NUM_ENTRY-1);
    $readmemh("const_n16384_10b.mem", phase_memory_const, 0, NUM_ENTRY-1);
    $readmemh("linear_n16384_10b.mem", phase_memory_linear, 0, NUM_ENTRY-1);
end

endmodule

/* Expected result */
/*
Cycle: 0 -> z_corr_out = 0x9999
Cycle: 1 -> z_corr_out = 0x9999
Cycle: 2 -> z_corr_out = 0x8888
Cycle: 3 -> z_corr_out = 0x0000

Cycle: 4 -> z_corr_out = 0x9999
Cycle: 5 -> z_corr_out = 0x9999
Cycle: 6 -> z_corr_out = 0x2222
Cycle: 7 -> z_corr_out = 0x0000
*/