// Numerically controlled oscillator (NCO)

module nco_no_z_corr #(
	parameter N = 22, // N-bit NCO
	parameter OUTPUT_WIDTH = 10
)(
    clk,
    rst,
    //
    ftw_wr_en,
    ftw_in,
    //
    phase_wr_en,
    phase_out
);

// Normally FTW_WIDTH == PHASE_WIDTH == N 
localparam FTW_WIDTH = N;
localparam PHASE_WIDTH = N;

input                       clk;
input                       rst;
input                       ftw_wr_en;
input   [FTW_WIDTH-1:0]     ftw_in;
input                       phase_wr_en;

output  [OUTPUT_WIDTH-1:0]  phase_out;

reg     [FTW_WIDTH-1:0]     ftw;
reg     [PHASE_WIDTH-1:0]   phase;

wire    [PHASE_WIDTH-1:0]   next_phase;

always @(posedge clk) begin
    if (rst) begin
        ftw <= 0;
        phase <= 0;
    end
    else begin
        if (ftw_wr_en) ftw <= ftw_in;
        else ftw <= ftw;

        if (phase_wr_en) phase <= next_phase;
        else phase <= phase;
    end
end

assign next_phase = ftw + phase;
assign phase_out = phase[(PHASE_WIDTH-1) -: OUTPUT_WIDTH]; // MSB

endmodule
