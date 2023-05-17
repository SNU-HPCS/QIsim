module readout_tx_signal_gen_unit #(
    parameter NCO_N                     = 22,
    parameter PHASE_WIDTH               = 10,
    parameter SIN_LUT_NUM_ENTRY         = 1024,
    parameter SIN_LUT_ADDR_WIDTH        = PHASE_WIDTH,
    parameter SIN_LUT_DATA_WIDTH        = 16
)(
    clk,
    rst,

    nco_ftw_wr_en,
    nco_ftw_in,

    sin_lut_wr_en,
    sin_lut_wr_addr,
    sin_lut_wr_data,

    valid_inst_in,

    valid_sin_wave_out,
    sin_wave_out

    // sin_lut_rd_addr_out,
    // sin_lut_rd_data_in
);

/* localparam declaration */
localparam NCO_OUTPUT_WIDTH = PHASE_WIDTH;

localparam MUX_NUM_INPUT = 2;
localparam MUX_SEL_WIDTH = 1;

/* Port declaration */
input                                           clk;
input                                           rst;
input                                           nco_ftw_wr_en;
input   [NCO_N-1:0]                             nco_ftw_in;

input                                           sin_lut_wr_en;
input   [SIN_LUT_ADDR_WIDTH-1:0]                sin_lut_wr_addr;
input   [SIN_LUT_DATA_WIDTH-1:0]                sin_lut_wr_data;

input                                           valid_inst_in;

output  [0:0]                                   valid_sin_wave_out;
output  [SIN_LUT_DATA_WIDTH-1:0]                sin_wave_out;

// output  [SIN_LUT_ADDR_WIDTH-1:0]                sin_lut_rd_addr_out;
// input   [SIN_LUT_DATA_WIDTH-1:0]                sin_lut_rd_data_in;

// nco
wire                                            nco_phase_wr_en;
wire    [NCO_OUTPUT_WIDTH-1:0]                  nco_phase_out;

// nco_mux
wire    [MUX_NUM_INPUT*NCO_OUTPUT_WIDTH-1:0]    nco_mux_data_in;
wire    [MUX_SEL_WIDTH-1:0]                     nco_mux_sel;
wire    [NCO_OUTPUT_WIDTH-1:0]                  nco_mux_data_out;

reg     [NCO_OUTPUT_WIDTH-1:0]                  selected_nco_phase;
reg                                             valid_selected_nco_phase;

// sin_lut
wire    [SIN_LUT_ADDR_WIDTH-1:0]                sin_lut_rd_addr;
wire    [SIN_LUT_DATA_WIDTH-1:0]                sin_lut_rd_data;

reg     [SIN_LUT_DATA_WIDTH-1:0]                sin_wave;
reg                                             valid_sin_wave;
/* Declaration end */

// nco
assign nco_phase_wr_en = valid_inst_in;

nco_no_z_corr #(
    .N(NCO_N),
    .OUTPUT_WIDTH(NCO_OUTPUT_WIDTH)
) nco_instance (
    .clk(clk),
    .rst(rst),
    .ftw_wr_en(nco_ftw_wr_en),
    .ftw_in(nco_ftw_in),
    .phase_wr_en(nco_phase_wr_en),
    .phase_out(nco_phase_out)
);


// nco_mux
assign nco_mux_data_in = {nco_phase_out, {NCO_OUTPUT_WIDTH{1'b0}}};
assign nco_mux_sel = valid_inst_in;

mux_param #(
    .NUM_INPUT(MUX_NUM_INPUT),
    .SEL_WIDTH(MUX_SEL_WIDTH),
    .DATA_WIDTH(NCO_OUTPUT_WIDTH)
) nco_mux (
    .data_in(nco_mux_data_in),
    .sel(nco_mux_sel),
    .data_out(nco_mux_data_out)
);

always @(posedge clk) begin
    selected_nco_phase <= nco_mux_data_out;
    valid_selected_nco_phase <= valid_inst_in;
end

// sin_lut
assign sin_lut_rd_addr = selected_nco_phase;
// /*
sin_lut_param #(
    .NUM_ENTRY(SIN_LUT_NUM_ENTRY),
    .ADDR_WIDTH(SIN_LUT_ADDR_WIDTH),
    .DATA_WIDTH(SIN_LUT_DATA_WIDTH)
) sin_lut (
    .clk(clk),
    .wr_en(sin_lut_wr_en),
    .wr_addr(sin_lut_wr_addr), 
    .wr_data(sin_lut_wr_data), 
    .rd_addr(sin_lut_rd_addr),
    .rd_data(sin_lut_rd_data)
);
// */
// assign sin_lut_rd_addr_out = sin_lut_rd_addr;
// assign sin_lut_rd_data = sin_lut_rd_data_in;

always @(posedge clk) begin
    sin_wave <= sin_lut_rd_data;
    valid_sin_wave <= valid_selected_nco_phase;
end

assign sin_wave_out = sin_wave;
assign valid_sin_wave_out = valid_sin_wave;

endmodule
