// Numerically controlled oscillator (NCO)

module nco_backup #(
	parameter N = 22, // N-bit NCO
    parameter Z_CORR_WIDTH = 12,
	parameter OUTPUT_WIDTH = 10
)(
    clk,
    rst,
    //
    ftw_wr_en,
    ftw_in,
    //
    z_corr_wr_en,
    z_corr_in,
    //
    phase_wr_en,
    z_corr_mode,
    phase_out
);

// Normally FTW_WIDTH == PHASE_WIDTH == N 
localparam FTW_WIDTH = N;
localparam PHASE_WIDTH = 24;
localparam Z_CORR_PAD = PHASE_WIDTH-Z_CORR_WIDTH;

input                       clk;
input                       rst;
input                       ftw_wr_en;
input   [FTW_WIDTH-1:0]     ftw_in;
input                       z_corr_wr_en;
input   [Z_CORR_WIDTH-1:0]  z_corr_in;
input                       phase_wr_en;
input                       z_corr_mode;

/*
output  [OUTPUT_WIDTH-1:0]  phase_out;

reg     [FTW_WIDTH-1:0]     ftw;
reg     [PHASE_WIDTH-1:0]   phase;
reg     [Z_CORR_WIDTH-1:0]  z_corr;

wire    [FTW_WIDTH-1:0]     ftw_operand;
wire    [PHASE_WIDTH-1:0]   next_phase;

wire    [PHASE_WIDTH-1:0]   next_step;

always @(posedge clk) begin: wr_en_blk
    if (rst) begin
        ftw <= 0;
        z_corr <= 0;
        phase <= 0;
    end
    else begin
        if (ftw_wr_en) ftw <= ftw_in;
        else ftw <= ftw;

        if (z_corr_wr_en) z_corr <= z_corr_in;
        else z_corr <= z_corr;

        if (phase_wr_en) phase <= next_phase;
        else phase <= phase;
    end
end

assign ftw_operand = z_corr_mode ? {FTW_WIDTH{1'b0}} : ftw;
// assign next_phase = ftw_operand + phase + {{(PHASE_WIDTH-Z_CORR_WIDTH){1'b0}}, z_corr};
assign next_step = ftw_operand + {{(PHASE_WIDTH-Z_CORR_WIDTH){1'b0}}, z_corr};
assign next_phase = next_step + phase;
assign phase_out = phase[(PHASE_WIDTH-1) -: OUTPUT_WIDTH]; // MSB
*/

output reg [OUTPUT_WIDTH-1:0]  phase_out;

// DFFs
reg     [FTW_WIDTH-1:0]     ftw;
reg     [PHASE_WIDTH-1:0]   phase;
reg     [Z_CORR_WIDTH-1:0]  z_corr;

// wires
reg     [FTW_WIDTH-1:0]     ftw_operand;
reg     [PHASE_WIDTH-1:0]   next_phase;
reg     [PHASE_WIDTH-1:0]   next_step;

always @(posedge clk) begin: wr_en_blk
    if (rst) begin
        ftw <= 0;
        z_corr <= 0;
        phase <= 0;
    end
    else begin
        if (ftw_wr_en) ftw <= ftw_in;
        else ftw <= ftw;

        if (z_corr_wr_en) z_corr <= z_corr_in;
        else z_corr <= z_corr;

        if (phase_wr_en) phase <= next_phase;
        else phase <= phase;
    end
end

always @(*) begin: ftw_sel_blk
    ftw_operand = z_corr_mode ? {FTW_WIDTH{1'b0}} : ftw;
end
// assign next_phase = ftw_operand + phase + {{(PHASE_WIDTH-Z_CORR_WIDTH){1'b0}}, z_corr};
always @(*) begin: next_step_blk
    next_step = ftw_operand + {{(PHASE_WIDTH-Z_CORR_WIDTH){1'b0}}, z_corr};
end
always @(*) begin: next_phase_blk
    next_phase = next_step + phase;
end
always @(*) begin: phase_out_blk
    phase_out = phase[(PHASE_WIDTH-1) -: OUTPUT_WIDTH]; // MSB
end

endmodule
