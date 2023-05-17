`timescale 1ns/100ps

`define N 22
`define Z_CORR_WIDTH 12
`define OUTPUT_WIDTH 10

module nco_tb();

reg                         clk;
reg                         rst;
reg                         ftw_wr_en;
reg   [`N-1:0]              ftw_in;
reg                         z_corr_wr_en;
reg   [`Z_CORR_WIDTH-1:0]   z_corr_in;
reg                         phase_wr_en;
reg                         z_corr_mode;

wire  [`OUTPUT_WIDTH-1:0]   phase_out;

nco #(
    .N(`N),
    .Z_CORR_WIDTH(`Z_CORR_WIDTH),
    .OUTPUT_WIDTH(`OUTPUT_WIDTH)
) UUT (
    .clk(clk),
    .rst(rst),
    .ftw_wr_en(ftw_wr_en),
    .ftw_in(ftw_in),
    .z_corr_wr_en(z_corr_wr_en),
    .z_corr_in(z_corr_in),
    .phase_wr_en(phase_wr_en),
    .z_corr_mode(z_corr_mode),
    .phase_out(phase_out)
);

integer I;

always #10 clk = ~clk;

initial begin
    $dumpfile("nco.vcd");
    $dumpvars(0, nco_tb);

    clk = 0;
    rst = 0;
    ftw_wr_en = 0;
    z_corr_wr_en = 0;
    phase_wr_en = 0;
    ftw_in = 0;
    z_corr_in = 0;
    z_corr_mode = 0;
    #5;
    rst = 1;
    #10;
    rst = 0;
    #5;

    #5;
    ftw_wr_en = 1;
    z_corr_wr_en = 1;
    ftw_in = `N'b100000000000;
    z_corr_in = `Z_CORR_WIDTH'b0;
    // ftw_in = `N'b100000000000;
    // z_corr_in = `N'b0;
    #10;
    ftw_wr_en = 0;
    z_corr_wr_en = 0;
    ftw_in = 0;
    z_corr_in = 0;
    #5;

    for (I=0; I<100; I=I+1)
    begin
        #20;
        phase_wr_en = 1;
    end
    for (I=0; I<10; I=I+1)
    begin
        #20;
        phase_wr_en = 0;
    end
    for (I=0; I<100; I=I+1)
    begin
        #20;
        phase_wr_en = 1;
    end

    #20;
    $finish;
end


endmodule
