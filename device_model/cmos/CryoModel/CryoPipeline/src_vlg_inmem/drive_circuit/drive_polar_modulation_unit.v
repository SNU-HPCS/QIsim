module drive_polar_modulation_unit #(
    parameter SIN_LUT_NUM_ENTRY = 1024,
    parameter SIN_LUT_ADDR_WIDTH = 10,
    parameter SIN_LUT_DATA_WIDTH = 8,
    parameter OUTPUT_WIDTH = 9
)(
    clk,
    sin_lut_wr_en,
    cos_lut_wr_en,
    sinusoidal_lut_wr_addr, 
    sinusoidal_lut_wr_data, 
    valid_in,

    nco_phase,
    enve_memory_phase,
    enve_memory_amp,
    i_out,
    q_out,
    valid_out
);

localparam PHASE_WIDTH = SIN_LUT_ADDR_WIDTH;
localparam AMP_WIDTH = SIN_LUT_DATA_WIDTH;

// Port declaration

input                                   clk;
input                                   sin_lut_wr_en;
input                                   cos_lut_wr_en;
input       [SIN_LUT_ADDR_WIDTH-1:0]    sinusoidal_lut_wr_addr; 
input       [SIN_LUT_DATA_WIDTH-1:0]    sinusoidal_lut_wr_data;

input                                   valid_in;
input       [PHASE_WIDTH-1:0]           nco_phase;
input       [PHASE_WIDTH-1:0]           enve_memory_phase;
input       [AMP_WIDTH-1:0]             enve_memory_amp;
output reg  [OUTPUT_WIDTH-1:0]          i_out;
output reg  [OUTPUT_WIDTH-1:0]          q_out;
output reg  [0:0]                       valid_out;

wire        [OUTPUT_WIDTH-1:0]          i_enve_multiplier_out;
wire        [OUTPUT_WIDTH-1:0]          q_enve_multiplier_out;
reg         [OUTPUT_WIDTH-1:0]          i_enve_multiplier;
reg         [OUTPUT_WIDTH-1:0]          q_enve_multiplier;

wire        [SIN_LUT_ADDR_WIDTH-1:0]    phase_adder_out;
// wire        [SIN_LUT_ADDR_WIDTH-1:0]    sin_lut_rd_addr;
// wire        [SIN_LUT_ADDR_WIDTH-1:0]    cos_lut_rd_addr;
reg         [SIN_LUT_ADDR_WIDTH-1:0]    sin_lut_rd_addr;
reg         [SIN_LUT_ADDR_WIDTH-1:0]    cos_lut_rd_addr;

// wire        [SIN_LUT_DATA_WIDTH-1:0]    cos_lut_rd_data;
// wire        [SIN_LUT_DATA_WIDTH-1:0]    sin_lut_rd_data;
wire        [SIN_LUT_DATA_WIDTH-1:0]    cos_lut_rd_data_out;
wire        [SIN_LUT_DATA_WIDTH-1:0]    sin_lut_rd_data_out;
reg         [SIN_LUT_DATA_WIDTH-1:0]    cos_lut_rd_data;
reg         [SIN_LUT_DATA_WIDTH-1:0]    sin_lut_rd_data;


// phase shift
adder_param #(
    .DATA_IN_WIDTH(SIN_LUT_ADDR_WIDTH),
    .DATA_OUT_WIDTH(SIN_LUT_ADDR_WIDTH),
    .TAKE_MSB(0)
) phase_adder (
    .data_in_1(nco_phase),
    .data_in_2(enve_memory_phase),
    .data_out(phase_adder_out)
);

// sin/cos lut
reg                                     valid_phase_adder;
reg         [AMP_WIDTH-1:0]             enve_memory_amp_0_1;
always @(posedge clk) begin
    sin_lut_rd_addr <= phase_adder_out;
    cos_lut_rd_addr <= phase_adder_out;
    valid_phase_adder <= valid_in;
    enve_memory_amp_0_1 <= enve_memory_amp;
end
// assign sin_lut_rd_addr = phase_adder_out;
// assign cos_lut_rd_addr = phase_adder_out;

cos_lut_param #(
    .NUM_ENTRY(SIN_LUT_NUM_ENTRY),
    .ADDR_WIDTH(SIN_LUT_ADDR_WIDTH),
    .DATA_WIDTH(SIN_LUT_DATA_WIDTH)
) cos_lut (
    .clk(clk),
    .wr_en(cos_lut_wr_en),
    .wr_addr(sinusoidal_lut_wr_addr),
    .wr_data(sinusoidal_lut_wr_data),
    .rd_addr(cos_lut_rd_addr),
    .rd_data(cos_lut_rd_data_out)
);

sin_lut_param #(
    .NUM_ENTRY(SIN_LUT_NUM_ENTRY),
    .ADDR_WIDTH(SIN_LUT_ADDR_WIDTH),
    .DATA_WIDTH(SIN_LUT_DATA_WIDTH)
) sin_lut (
    .clk(clk),
    .wr_en(sin_lut_wr_en),
    .wr_addr(sinusoidal_lut_wr_addr),
    .wr_data(sinusoidal_lut_wr_data),
    .rd_addr(sin_lut_rd_addr),
    .rd_data(sin_lut_rd_data_out)
);

reg                                     valid_sinusoidal_lut;
reg         [AMP_WIDTH-1:0]             enve_memory_amp_1_1;
always @(posedge clk) begin
    cos_lut_rd_data <= cos_lut_rd_data_out;
    sin_lut_rd_data <= sin_lut_rd_data_out;
    valid_sinusoidal_lut <= valid_phase_adder;
    enve_memory_amp_1_1 <= enve_memory_amp_0_1;
end

// envelope multiplication
multiplier_param #(
    .DATA_IN_WIDTH(SIN_LUT_DATA_WIDTH),
    .DATA_OUT_WIDTH(OUTPUT_WIDTH),
    .TAKE_MSB(1)
) i_enve_multiplier_instance (
    .data_in_1(cos_lut_rd_data),
    .data_in_2(enve_memory_amp_1_1),
    .data_out(i_enve_multiplier_out)
);

multiplier_param #(
    .DATA_IN_WIDTH(SIN_LUT_DATA_WIDTH),
    .DATA_OUT_WIDTH(OUTPUT_WIDTH),
    .TAKE_MSB(1)
) q_enve_multiplier_instance (
    .data_in_1(sin_lut_rd_data),
    .data_in_2(enve_memory_amp_1_1),
    .data_out(q_enve_multiplier_out)
);

reg valid_iq_multiplier;
always @(posedge clk) begin
    i_enve_multiplier <= i_enve_multiplier_out;
    q_enve_multiplier <= q_enve_multiplier_out;
    valid_iq_multiplier <= valid_sinusoidal_lut;
end

// Combinational read
always @(*) begin
    i_out = i_enve_multiplier;
    q_out = q_enve_multiplier;
    valid_out = valid_iq_multiplier;
end

endmodule
