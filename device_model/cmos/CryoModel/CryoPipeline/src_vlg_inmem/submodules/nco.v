// Numerically controlled oscillator (NCO)

module nco #(
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
wire    [FTW_WIDTH-1:0]     ftw;
wire    [PHASE_WIDTH-1:0]   phase;
wire    [Z_CORR_WIDTH-1:0]  z_corr;

// wires
wire    [FTW_WIDTH-1:0]     ftw_operand;
wire    [PHASE_WIDTH-1:0]   next_phase;
wire    [PHASE_WIDTH-1:0]   next_step;

/*
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
*/
ff #(
    .DATA_WIDTH(FTW_WIDTH)
) ftw_ff (
    .clk(clk),
    .rst(rst),
    .wr_en(ftw_wr_en), 
    .wr_data(ftw_in), 
    .rd_data(ftw)
);
ff #(
    .DATA_WIDTH(Z_CORR_WIDTH)
) z_corr_ff (
    .clk(clk),
    .rst(rst),
    .wr_en(z_corr_wr_en), 
    .wr_data(z_corr_in), 
    .rd_data(z_corr)
);
ff #(
    .DATA_WIDTH(PHASE_WIDTH)
) phase_ff (
    .clk(clk),
    .rst(rst),
    .wr_en(phase_wr_en), 
    .wr_data(next_phase), 
    .rd_data(phase)
);

/*
always @(*) begin: ftw_sel_blk
    ftw_operand = z_corr_mode ? {FTW_WIDTH{1'b0}} : ftw;
end
*/

wire    [2*FTW_WIDTH-1:0]   ftw_mux_data_in;
wire    [0:0]               ftw_mux_sel;
wire    [FTW_WIDTH-1:0]     ftw_mux_data_out;

assign ftw_mux_data_in = {{FTW_WIDTH{1'b0}}, ftw};
assign ftw_mux_sel = z_corr_mode;
assign ftw_operand = ftw_mux_data_out;
mux_param #(
    .NUM_INPUT(2),
    .SEL_WIDTH(1),
    .DATA_WIDTH(FTW_WIDTH)
) ftw_mux (
    .data_in(ftw_mux_data_in),
    .sel(ftw_mux_sel),
    .data_out(ftw_mux_data_out)
);


// assign next_phase = ftw_operand + phase + {{(PHASE_WIDTH-Z_CORR_WIDTH){1'b0}}, z_corr};
/*
always @(*) begin: next_step_blk
    next_step = ftw_operand + {{(PHASE_WIDTH-Z_CORR_WIDTH){1'b0}}, z_corr};
end
*/
wire    [PHASE_WIDTH-1:0]     next_step_adder_data_in_1;
wire    [PHASE_WIDTH-1:0]     next_step_adder_data_in_2;
wire    [PHASE_WIDTH-1:0]   next_step_adder_data_out;

assign next_step_adder_data_in_1 = {{(PHASE_WIDTH-FTW_WIDTH){1'b0}}, ftw_operand};
assign next_step_adder_data_in_2 = {{(PHASE_WIDTH-Z_CORR_WIDTH){1'b0}}, z_corr};
assign next_step = next_step_adder_data_out;
adder_param #(
	.DATA_IN_WIDTH(PHASE_WIDTH),
	.DATA_OUT_WIDTH(PHASE_WIDTH),
    .TAKE_MSB(0)
) next_step_adder (
    .data_in_1(next_step_adder_data_in_1),
    .data_in_2(next_step_adder_data_in_2),
    .data_out(next_step_adder_data_out)
);

/*
always @(*) begin: next_phase_blk
    next_phase = next_step + phase;
end
*/

wire    [PHASE_WIDTH-1:0]   next_phase_adder_data_in_1;
wire    [PHASE_WIDTH-1:0]   next_phase_adder_data_in_2;
wire    [PHASE_WIDTH-1:0]   next_phase_adder_data_out;

assign next_phase_adder_data_in_1 = next_step;
assign next_phase_adder_data_in_2 = phase;
assign next_phase = next_phase_adder_data_out;
adder_param #(
	.DATA_IN_WIDTH(PHASE_WIDTH),
	.DATA_OUT_WIDTH(PHASE_WIDTH),
    .TAKE_MSB(0)
) next_phase_adder (
    .data_in_1(next_phase_adder_data_in_1),
    .data_in_2(next_phase_adder_data_in_2),
    .data_out(next_phase_adder_data_out)
);

always @(*) begin: phase_out_blk
    phase_out = phase[(PHASE_WIDTH-1) -: OUTPUT_WIDTH]; // MSB
end

endmodule
