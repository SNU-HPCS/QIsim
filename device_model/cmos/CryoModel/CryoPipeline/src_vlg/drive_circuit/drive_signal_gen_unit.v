
`define DC_CORRECTION_VALUE 0

module drive_signal_gen_unit #(
    parameter NUM_QUBIT                 = 16, // number of qubits per bank
    parameter QUBIT_ADDR_WIDTH          = 4,
    parameter IQ_OUT_WIDTH              = 9, // Usually IQ_OUT_WIDTH == IQ_CALI_WIDTH

    /* Instruction decode */
    // inst_list
    parameter INST_LIST_NUM_ENTRY       = 2048,
    parameter INST_LIST_ADDR_WIDTH      = 11,
    parameter INST_LIST_DATA_WIDTH      = 17, // QUBIT_ADDR_WIDTH + RZ_MODE + PHASE_IMM, INST=PHASE_IMM[2:0]
    // inst_table
    parameter INST_TABLE_NUM_ENTRY      = 8,
    parameter INST_TABLE_ADDR_WIDTH     = 3,
    parameter INST_TABLE_DATA_WIDTH     = 34, // ENVE_MEMORY_ADDR_WIDTH *2 + AXIS_WIDTH
    parameter AXIS_WIDTH                = 2,
    // enve_memory
    parameter ENVE_MEMORY_NUM_ENTRY     = 40960,
    parameter ENVE_MEMORY_ADDR_WIDTH    = 16,
    parameter PHASE_WIDTH               = 10,
    parameter AMP_WIDTH                 = 8,
    // cali_memory
    parameter CALI_MEMORY_NUM_ENTRY     = 16,
    parameter CALI_MEMORY_ADDR_WIDTH    = 4,
    parameter CALI_MEMORY_DATA_WIDTH    = 36,

    /* NCO */
    parameter NCO_N                     = 22,
    parameter Z_CORR_WIDTH              = 12,
    parameter SIN_LUT_NUM_ENTRY         = 1024,
    parameter SIN_LUT_ADDR_WIDTH        = PHASE_WIDTH,
    parameter SIN_LUT_DATA_WIDTH        = AMP_WIDTH,

    /* Calibration */
    parameter IQ_CALI_WIDTH             = 9
)(
    clk,
    rst,
    PC,
    valid_PC_in,

    /* Instruction decode */
    start_read_addr,
    set_enve_memory_addr,
    increment_enve_memory_addr,

    valid_addr_out,
    valid_inst_list_out,
    phase_imm_out,

    valid_z_corr_in,
    rz_mode_in,
    rz_mode_out,

    /* Internal memory initialization */
    inst_list_wr_en,
    inst_list_wr_addr,
    inst_list_wr_data,

    inst_table_wr_sel,
    inst_table_wr_en,
    inst_table_wr_addr,
    inst_table_wr_data,

    enve_memory_wr_en,
    enve_memory_wr_addr,
    enve_memory_wr_data,

    cali_memory_wr_en,
    cali_memory_wr_addr,
    cali_memory_wr_data,
    dc_correction,

    sin_lut_wr_en,
    cos_lut_wr_en,
    sinusoidal_lut_wr_addr,
    sinusoidal_lut_wr_data,

    //
    qubit_sel_out,
    valid_inst_table_out,
    is_read_env_fin,
    is_rz_fin_out,

    /* NCO */
    nco_ftw_wr_en,
    nco_ftw_in,
    nco_z_corr_wr_en,
    nco_z_corr_in,
    nco_phase_wr_en,
    nco_z_corr_mode,

    /* Result */
    valid_out,
    i_out,
    q_out,

    inst_list_rd_addr_out,
    inst_list_rd_data_in,
    inst_table_rd_addr_out,
    inst_table_rd_data_in,
    enve_memory_rd_addr_out,
    enve_memory_rd_data_in,
    cali_memory_rd_addr_out,
    cali_memory_rd_data_in,
    cos_lut_rd_addr_out,
    cos_lut_rd_data_in,
    sin_lut_rd_addr_out,
    sin_lut_rd_data_in
);

////////////////////////////////
//// Localparam declaration ////
////////////////////////////////

localparam ENVE_MEMORY_DATA_WIDTH = PHASE_WIDTH + AMP_WIDTH;
localparam PC_WIDTH = INST_LIST_ADDR_WIDTH;
/* NCO */
// NCO
localparam NUM_NCO = NUM_QUBIT;
localparam NCO_ADDR_WIDTH = QUBIT_ADDR_WIDTH;
localparam NCO_OUTPUT_WIDTH = PHASE_WIDTH;
localparam NCO_Z_CORR_WIDTH = Z_CORR_WIDTH;

// sin/cos lut
localparam POLAR_MOD_WIDTH = IQ_CALI_WIDTH;

/* Calibration */
// localparam CALI_MEMORY_NUM_ENTRY = NUM_QUBIT;
// localparam CALI_MEMORY_ADDR_WIDTH = QUBIT_ADDR_WIDTH;
// localparam CALI_MEMORY_DATA_WIDTH = IQ_CALI_WIDTH*4;

////////////////////////////
//// In/Out declaration ////
////////////////////////////

input                                               clk; 
input                                               rst;
input      [PC_WIDTH-1:0]                           PC;
input                                               valid_PC_in;

/* Instruction decode */
input                                               start_read_addr;
input                                               set_enve_memory_addr;
input                                               increment_enve_memory_addr;

output                                              valid_addr_out;
output                                              valid_inst_list_out;
output      [Z_CORR_WIDTH-1:0]                      phase_imm_out;

input                                               valid_z_corr_in;
input                                               rz_mode_in;
output                                              rz_mode_out;

input                                               inst_list_wr_en;
input       [INST_LIST_ADDR_WIDTH-1:0]              inst_list_wr_addr;
input       [INST_LIST_DATA_WIDTH-1:0]              inst_list_wr_data;

input       [NUM_QUBIT-1:0]                         inst_table_wr_sel;
input                                               inst_table_wr_en;
input       [INST_TABLE_ADDR_WIDTH-1:0]             inst_table_wr_addr;
input       [INST_TABLE_DATA_WIDTH-1:0]             inst_table_wr_data;

input                                               enve_memory_wr_en;
input       [ENVE_MEMORY_ADDR_WIDTH-1:0]            enve_memory_wr_addr;
input       [ENVE_MEMORY_DATA_WIDTH-1:0]            enve_memory_wr_data;

input                                               cali_memory_wr_en;
input       [CALI_MEMORY_ADDR_WIDTH-1:0]            cali_memory_wr_addr;
input       [CALI_MEMORY_DATA_WIDTH-1:0]            cali_memory_wr_data;
input       [IQ_CALI_WIDTH-1:0]                     dc_correction; 


input                                               sin_lut_wr_en;
input                                               cos_lut_wr_en;
input       [SIN_LUT_ADDR_WIDTH-1:0]                sinusoidal_lut_wr_addr; 
input       [SIN_LUT_DATA_WIDTH-1:0]                sinusoidal_lut_wr_data;

output      [QUBIT_ADDR_WIDTH-1:0]                  qubit_sel_out;
output                                              valid_inst_table_out;
output reg  [0:0]                                   is_read_env_fin;
output                                              is_rz_fin_out;

/* NCO */
input       [NUM_NCO-1:0]                           nco_ftw_wr_en;
input       [NUM_NCO*NCO_N-1:0]                     nco_ftw_in;
input       [NUM_NCO-1:0]                           nco_z_corr_wr_en;
input       [NUM_NCO*NCO_Z_CORR_WIDTH-1:0]          nco_z_corr_in;
input       [NUM_NCO-1:0]                           nco_phase_wr_en;
input       [NUM_NCO-1:0]                           nco_z_corr_mode;

/* IQ Result */
output      [0:0]                                   valid_out;
output      [IQ_OUT_WIDTH-1:0]                      i_out;
output      [IQ_OUT_WIDTH-1:0]                      q_out;


output [INST_LIST_ADDR_WIDTH-1:0] inst_list_rd_addr_out;
input  [INST_LIST_DATA_WIDTH-1:0] inst_list_rd_data_in;
output [NUM_QUBIT*INST_TABLE_ADDR_WIDTH-1:0] inst_table_rd_addr_out;
input  [NUM_QUBIT*INST_TABLE_DATA_WIDTH-1:0] inst_table_rd_data_in;
output [ENVE_MEMORY_ADDR_WIDTH-1:0] enve_memory_rd_addr_out;
input  [ENVE_MEMORY_DATA_WIDTH-1:0] enve_memory_rd_data_in;
output [CALI_MEMORY_ADDR_WIDTH-1:0] cali_memory_rd_addr_out;
input  [CALI_MEMORY_DATA_WIDTH-1:0] cali_memory_rd_data_in;
output [SIN_LUT_ADDR_WIDTH-1:0] cos_lut_rd_addr_out;
input  [SIN_LUT_DATA_WIDTH-1:0] cos_lut_rd_data_in;
output [SIN_LUT_ADDR_WIDTH-1:0] sin_lut_rd_addr_out;
input  [SIN_LUT_DATA_WIDTH-1:0] sin_lut_rd_data_in;

//////////////////////////
//// Port declaration ////
//////////////////////////

/* Instruction decode */
wire        [INST_LIST_ADDR_WIDTH-1:0]              inst_list_rd_addr;
wire        [INST_LIST_DATA_WIDTH-1:0]              inst_list_rd_data;
wire        [NUM_QUBIT*INST_TABLE_DATA_WIDTH-1:0]   inst_table_rd_data;
wire        [ENVE_MEMORY_ADDR_WIDTH-1:0]            enve_memory_rd_addr;
wire        [ENVE_MEMORY_DATA_WIDTH-1:0]            enve_memory_rd_data;

// inst_list
reg         [QUBIT_ADDR_WIDTH-1:0]                  qubit_sel;
reg                                                 rz_mode;
reg         [Z_CORR_WIDTH-1:0]                      phase_imm;
reg         [INST_TABLE_ADDR_WIDTH-1:0]             inst;
reg                                                 valid_inst_list;
// inst_table
wire        [QUBIT_ADDR_WIDTH-1:0]                  inst_table_mux_sel;
wire        [NUM_QUBIT*INST_TABLE_DATA_WIDTH-1:0]   inst_table_mux_data_in;
wire        [INST_TABLE_DATA_WIDTH-1:0]             inst_table_mux_data_out;

reg         [ENVE_MEMORY_ADDR_WIDTH-1:0]            start_addr_0_1;
reg         [ENVE_MEMORY_ADDR_WIDTH-1:0]            stop_addr_0_2;
reg         [ENVE_MEMORY_ADDR_WIDTH-1:0]            start_addr_1_1;
reg         [ENVE_MEMORY_ADDR_WIDTH-1:0]            stop_addr_1_2;
reg         [ENVE_MEMORY_ADDR_WIDTH-1:0]            stop_addr_2_2;

reg         [AXIS_WIDTH-1:0]                        axis;
reg                                                 valid_inst_table;
// enve_memory
wire        [ENVE_MEMORY_ADDR_WIDTH-1:0]            enve_memory_addr_p1;
wire        [ENVE_MEMORY_ADDR_WIDTH-1:0]            enve_memory_addr_p2;

reg                                                 valid_addr;
reg                                                 valid_enve_memory_0_1;
reg                                                 valid_enve_memory_1_1;
reg         [ENVE_MEMORY_ADDR_WIDTH-1:0]            enve_memory_addr;
reg         [PHASE_WIDTH-1:0]                       phase_0_1;
reg         [AMP_WIDTH-1:0]                         amplitude_0_1;
reg         [PHASE_WIDTH-1:0]                       phase_1_1;
reg         [AMP_WIDTH-1:0]                         amplitude_1_1;

/* NCO */
// NCO
wire        [NUM_NCO*NCO_OUTPUT_WIDTH-1:0]          nco_phase_out;

reg         [NUM_NCO-1:0]                           apply_phase_imm;
reg                                                 is_rz_fin;

// nco_mux
wire        [NCO_ADDR_WIDTH-1:0]                    nco_mux_sel;
wire        [NCO_OUTPUT_WIDTH*NUM_NCO-1:0]          nco_mux_data_in;
wire        [NCO_OUTPUT_WIDTH-1:0]                  nco_mux_data_out;

reg         [NCO_OUTPUT_WIDTH-1:0]                  selected_nco_phase;

/* Polar_modulation_unit */
wire        [POLAR_MOD_WIDTH-1:0]                   i_polar_mod_out;
wire        [POLAR_MOD_WIDTH-1:0]                   q_polar_mod_out;
wire                                                valid_polar_mod_out;

reg         [POLAR_MOD_WIDTH-1:0]                   i_polar_mod;
reg         [POLAR_MOD_WIDTH-1:0]                   q_polar_mod;
reg                                                 valid_polar_mod;

/* Calibration */
wire [CALI_MEMORY_ADDR_WIDTH-1:0]   cali_memory_rd_addr; 
wire [CALI_MEMORY_DATA_WIDTH-1:0]   cali_memory_rd_data; 

reg  [IQ_CALI_WIDTH-1:0]            alpha_i;
reg  [IQ_CALI_WIDTH-1:0]            beta_i;
reg  [IQ_CALI_WIDTH-1:0]            alpha_q;
reg  [IQ_CALI_WIDTH-1:0]            beta_q; 

wire [IQ_OUT_WIDTH-1:0]             i_cali_out;
wire [IQ_OUT_WIDTH-1:0]             q_cali_out;
wire                                valid_cali_out;

reg  [IQ_OUT_WIDTH-1:0]             i_cali;
reg  [IQ_OUT_WIDTH-1:0]             q_cali;
reg                                 valid_cali;

/////////////////////////////
//// Combinational Logic ////
/////////////////////////////

genvar i;

/* Instruction decode */
assign enve_memory_addr_p1 = enve_memory_addr +1;
assign enve_memory_addr_p2 = enve_memory_addr +2;

// inst_list
assign inst_list_rd_addr = PC;
assign qubit_sel_out = qubit_sel;

// inst_table
assign valid_inst_table_out = valid_inst_table;
assign is_rz_fin_out = is_rz_fin;

// inst_table_mux
assign inst_table_mux_sel = qubit_sel;
assign inst_table_mux_data_in = inst_table_rd_data;

mux_param #(
    .NUM_INPUT(NUM_QUBIT),
    .SEL_WIDTH(QUBIT_ADDR_WIDTH),
    .DATA_WIDTH(INST_TABLE_DATA_WIDTH)
) inst_table_mux (
    .data_in(inst_table_mux_data_in),
    .sel(inst_table_mux_sel),
    .data_out(inst_table_mux_data_out)
);


// enve_memory
assign enve_memory_rd_addr = enve_memory_addr;
always @(posedge clk) begin
    is_read_env_fin <= (increment_enve_memory_addr & (enve_memory_addr_p2 >= stop_addr_2_2)) ? 1'b1 : 1 'b0;
end
// assign is_read_env_fin = (increment_enve_memory_addr & (enve_memory_addr_p1 >= stop_addr_2_2)) ? 1'b1 : 1 'b0;
// assign is_read_env_fin = (enve_memory_addr >= stop_addr) ? 1'b1 : 1'b0;

/* NCO */

// NCO
assign nco_mux_data_in = nco_phase_out;
assign nco_mux_sel = qubit_sel;

// nco_mux
mux_param #(
    .NUM_INPUT(NUM_NCO),
    .SEL_WIDTH(NCO_ADDR_WIDTH),
    .DATA_WIDTH(NCO_OUTPUT_WIDTH)
) nco_mux (
    .data_in(nco_mux_data_in),
    .sel(nco_mux_sel),
    .data_out(nco_mux_data_out)
);

drive_polar_modulation_unit #(
    .SIN_LUT_NUM_ENTRY(SIN_LUT_NUM_ENTRY),
    .SIN_LUT_ADDR_WIDTH(PHASE_WIDTH),
    .SIN_LUT_DATA_WIDTH(AMP_WIDTH),
    .OUTPUT_WIDTH(IQ_CALI_WIDTH)
) polar_modulation_unit_instance (
    .clk(clk),
    .sin_lut_wr_en(sin_lut_wr_en),
    .cos_lut_wr_en(cos_lut_wr_en),
    .sinusoidal_lut_wr_addr(sinusoidal_lut_wr_addr),
    .sinusoidal_lut_wr_data(sinusoidal_lut_wr_data),
    .valid_in(valid_enve_memory_1_1),
    .nco_phase(selected_nco_phase),
    .enve_memory_phase(phase_1_1),
    .enve_memory_amp(amplitude_1_1),
    .i_out(i_polar_mod_out),
    .q_out(q_polar_mod_out),
    .valid_out(valid_polar_mod_out),

    .cos_lut_rd_addr_out(cos_lut_rd_addr_out),
    .cos_lut_rd_data_in(cos_lut_rd_data_in),
    .sin_lut_rd_addr_out(sin_lut_rd_addr_out),
    .sin_lut_rd_data_in(sin_lut_rd_data_in)
);

always @(posedge clk) begin
    phase_1_1 <= phase_0_1;
    amplitude_1_1 <= amplitude_0_1;
    valid_enve_memory_1_1 <= valid_enve_memory_0_1;
end

/* Calibration */
assign cali_memory_rd_addr = {inst, qubit_sel};

drive_calibration_unit #(
    .IQ_CALI_WIDTH(IQ_CALI_WIDTH),
    .IQ_OUT_WIDTH(IQ_OUT_WIDTH)
) drive_calibration_unit_instance (
    .clk(clk),
    .i_in(i_polar_mod),
    .q_in(q_polar_mod),
    .valid_in(valid_polar_mod),
    .alpha_i(alpha_i),
    .beta_i(beta_i),
    .alpha_q(alpha_q),
    .beta_q(beta_q),
    .dc_correction(dc_correction),
    .i_out(i_cali_out),
    .q_out(q_cali_out),
    .valid_out(valid_cali_out)
);

/* Output */
assign i_out = i_cali;
assign q_out = q_cali;
assign valid_out = valid_cali;

//////////////////////////
//// Sequential Logic ////
//////////////////////////

/* Instruction decode */
/*
random_access_mem #(
    .NUM_ENTRY(INST_LIST_NUM_ENTRY),
    .ADDR_WIDTH(INST_LIST_ADDR_WIDTH),
    .DATA_WIDTH(INST_LIST_DATA_WIDTH)
) inst_list (
    .clk(clk),
    .wr_en(inst_list_wr_en),
    .wr_addr(inst_list_wr_addr),
    .wr_data(inst_list_wr_data),
    .rd_addr(inst_list_rd_addr),
    .rd_data(inst_list_rd_data)
);
*/

// /*
/*
wire inst_list_csb0, inst_list_web0;
wire [INST_LIST_ADDR_WIDTH-1:0] inst_list_addr0;
assign inst_list_csb0 = ~(valid_PC_in || inst_list_wr_en);
assign inst_list_web0 = ~inst_list_wr_en;
assign inst_list_addr0 = inst_list_web0 ? inst_list_rd_addr : inst_list_wr_addr;
sram_1rw0r0w_param_freepdk45 #(
    .RAM_DEPTH(INST_LIST_NUM_ENTRY),
    .ADDR_WIDTH(INST_LIST_ADDR_WIDTH),
    .DATA_WIDTH(INST_LIST_DATA_WIDTH)
) inst_list (
    .clk0(clk),
    .csb0(inst_list_csb0),
    .web0(inst_list_web0),
    .addr0(inst_list_addr0),
    .din0(inst_list_wr_data),
    .dout0(inst_list_rd_data)
);
*/
assign inst_list_rd_addr_out = inst_list_rd_addr;
assign inst_list_rd_data = inst_list_rd_data_in;
// */

reg read_inst_list_0_0;
assign phase_imm_out = phase_imm;
assign valid_inst_list_out = valid_inst_list;
always @(posedge clk) begin
    // inst_list
    read_inst_list_0_0 <= valid_PC_in;
    valid_inst_list <= read_inst_list_0_0;
    if (read_inst_list_0_0) begin
        qubit_sel   <= inst_list_rd_data[(Z_CORR_WIDTH+1) +: QUBIT_ADDR_WIDTH];
        rz_mode     <= inst_list_rd_data[Z_CORR_WIDTH];
        phase_imm   <= inst_list_rd_data[0 +: Z_CORR_WIDTH];
        inst        <= inst_list_rd_data[0 +: INST_TABLE_ADDR_WIDTH];
    end
end

generate
    for(i = 0; i < NUM_QUBIT; i = i +1) begin: genblk_inst_table
        wire                                inst_table_wr_en_i;
        wire [INST_TABLE_ADDR_WIDTH-1:0]    inst_table_rd_addr_i;
        wire [INST_TABLE_DATA_WIDTH-1:0]    inst_table_rd_data_i;

        assign inst_table_wr_en_i   = inst_table_wr_en & inst_table_wr_sel[i];
        assign inst_table_rd_addr_i = inst;
        assign inst_table_rd_data[INST_TABLE_DATA_WIDTH*i +: INST_TABLE_DATA_WIDTH] = inst_table_rd_data_i;

        wire inst_table_csb0, inst_table_web0;
        wire [INST_TABLE_ADDR_WIDTH-1:0] inst_table_addr0;
        assign inst_table_csb0 = ~(valid_inst_list || inst_table_wr_en_i);
        assign inst_table_web0 = ~inst_table_wr_en_i;
        assign inst_table_addr0 = inst_table_web0 ? inst_table_rd_addr_i : inst_table_wr_addr;
        /*
        sram_1rw0r0w_param_freepdk45 #(
            .RAM_DEPTH(INST_TABLE_NUM_ENTRY),
            .ADDR_WIDTH(INST_TABLE_ADDR_WIDTH),
            .DATA_WIDTH(INST_TABLE_DATA_WIDTH)
        ) inst_table (
            .clk0(clk),
            .csb0(inst_table_csb0),
            .web0(inst_table_web0),
            .addr0(inst_table_addr0),
            .din0(inst_table_wr_data),
            .dout0(inst_table_rd_data_i)
        );
        */
        assign inst_table_rd_addr_out[i*INST_TABLE_ADDR_WIDTH +: INST_TABLE_ADDR_WIDTH] = inst_table_rd_addr_i;
        assign inst_table_rd_data_i = inst_table_rd_data_in[i*INST_TABLE_DATA_WIDTH +: INST_TABLE_DATA_WIDTH];
    end
endgenerate

reg read_inst_table_0_0;
always @(posedge clk) begin
    // inst_table
    if (read_inst_table_0_0) begin
        start_addr_0_1  <= inst_table_mux_data_out[(AXIS_WIDTH + ENVE_MEMORY_ADDR_WIDTH) +: ENVE_MEMORY_ADDR_WIDTH];
        stop_addr_0_2 <= inst_table_mux_data_out[AXIS_WIDTH +: ENVE_MEMORY_ADDR_WIDTH];
        axis <= inst_table_mux_data_out[0 +: AXIS_WIDTH];
    end

    read_inst_table_0_0 <= (valid_inst_list & (~rz_mode));
    valid_inst_table <= read_inst_table_0_0;
end

always @(posedge clk) begin
    start_addr_1_1 <= start_addr_0_1;
    stop_addr_1_2 <= stop_addr_0_2;
    stop_addr_2_2 <= stop_addr_1_2;
end

/*
random_access_mem #(
    .NUM_ENTRY(ENVE_MEMORY_NUM_ENTRY),
    .ADDR_WIDTH(ENVE_MEMORY_ADDR_WIDTH),
    .DATA_WIDTH(ENVE_MEMORY_DATA_WIDTH)
) enve_memory (
    .clk(clk),
    .wr_en(enve_memory_wr_en),
    .wr_addr(enve_memory_wr_addr),
    .wr_data(enve_memory_wr_data),
    .rd_addr(enve_memory_rd_addr),
    .rd_data(enve_memory_rd_data)
);
*/

// /*
/*
wire enve_memory_csb0, enve_memory_web0;
wire [ENVE_MEMORY_ADDR_WIDTH-1:0] enve_memory_addr0;
// assign enve_memory_csb0 = ~(start_read_addr || enve_memory_wr_en);
assign enve_memory_csb0 = ~(valid_addr || enve_memory_wr_en);
assign enve_memory_web0 = ~enve_memory_wr_en;
assign enve_memory_addr0 = enve_memory_web0 ? enve_memory_rd_addr : enve_memory_wr_addr;
sram_1rw0r0w_param_freepdk45 #(
    .RAM_DEPTH(ENVE_MEMORY_NUM_ENTRY),
    .ADDR_WIDTH(ENVE_MEMORY_ADDR_WIDTH),
    .DATA_WIDTH(ENVE_MEMORY_DATA_WIDTH)
) enve_memory (
    .clk0(clk),
    .csb0(enve_memory_csb0),
    .web0(enve_memory_web0),
    .addr0(enve_memory_addr0),
    .din0(enve_memory_wr_data),
    .dout0(enve_memory_rd_data)
);
*/
assign enve_memory_rd_addr_out = enve_memory_rd_addr;
assign enve_memory_rd_data = enve_memory_rd_data_in;

reg read_enve_memory_0_0;
always @(posedge clk) begin
    // enve_memory
    if (read_enve_memory_0_0) begin
        phase_0_1 <= enve_memory_rd_data[AMP_WIDTH +: PHASE_WIDTH];
        amplitude_0_1 <= enve_memory_rd_data[0 +: AMP_WIDTH];
    end

    // read_enve_memory_0_0 <= start_read_addr;
    read_enve_memory_0_0 <= valid_addr;
    valid_enve_memory_0_1 <= read_enve_memory_0_0;

    if (rst) begin
        enve_memory_addr <= 0;
    end
    else if (increment_enve_memory_addr) begin
        enve_memory_addr <= enve_memory_addr_p1;
    end
    else if (set_enve_memory_addr) begin
        enve_memory_addr <= start_addr_1_1;
    end
    else begin
        enve_memory_addr <= enve_memory_addr;
    end

    if (rst) begin
        valid_addr <= 0;
    end
    else if (start_read_addr) begin
        valid_addr <= 1;
    end
    else if (is_read_env_fin) begin
        valid_addr <= 0;
    end
    else begin
        valid_addr <= valid_addr;
    end
end
assign valid_addr_out = valid_addr;

/* NCO */
assign rz_mode_out = rz_mode;

generate
    for(i = 0; i < NUM_NCO; i = i +1) begin: genblk_nco
        wire                        nco_ftw_wr_en_i;
        wire [NCO_N-1:0]            nco_ftw_in_i;
        wire                        nco_z_corr_wr_en_i;
        wire [NCO_Z_CORR_WIDTH-1:0] nco_z_corr_in_i;
        wire                        nco_phase_wr_en_i;
        wire                        nco_z_corr_mode_i;
        wire [NCO_OUTPUT_WIDTH-1:0] nco_phase_out_i;

        assign nco_ftw_wr_en_i = nco_ftw_wr_en[i];
        assign nco_ftw_in_i = nco_ftw_in[NCO_N*i +: NCO_N];
        // assign nco_z_corr_wr_en_i = nco_z_corr_wr_en[i] | (rz_mode && valid_inst_list);
        assign nco_z_corr_wr_en_i = nco_z_corr_wr_en[i];
        assign nco_z_corr_in_i = nco_z_corr_in[NCO_Z_CORR_WIDTH*i +: NCO_Z_CORR_WIDTH];
        assign nco_phase_wr_en_i = nco_phase_wr_en[i] | apply_phase_imm[i];
        assign nco_z_corr_mode_i = nco_z_corr_mode[i] | apply_phase_imm[i];

        assign nco_phase_out[NCO_OUTPUT_WIDTH*i +: NCO_OUTPUT_WIDTH] = nco_phase_out_i;

        nco #(
            .N(NCO_N),
            .Z_CORR_WIDTH(NCO_Z_CORR_WIDTH),
            .OUTPUT_WIDTH(NCO_OUTPUT_WIDTH)
        ) nco_instance (
            .clk(clk),
            .rst(rst),
            .ftw_wr_en(nco_ftw_wr_en_i),
            .ftw_in(nco_ftw_in_i),
            .z_corr_wr_en(nco_z_corr_wr_en_i),
            .z_corr_in(nco_z_corr_in_i),
            .phase_wr_en(nco_phase_wr_en_i),
            .z_corr_mode(nco_z_corr_mode_i),
            .phase_out(nco_phase_out_i)
        );

    end
endgenerate

always @(posedge clk) begin
    // nco
    if (rz_mode_in & valid_z_corr_in) begin
        apply_phase_imm[qubit_sel] <= 1'b1;
    end
    else begin
        apply_phase_imm <= {NUM_NCO{1'b0}};
    end
    is_rz_fin <= |apply_phase_imm;

    // nco_mux
    selected_nco_phase <= nco_mux_data_out;
    
    // sin/cos lut
    i_polar_mod <= i_polar_mod_out;
    q_polar_mod <= q_polar_mod_out;
    valid_polar_mod <= valid_polar_mod_out;
end


/* Calibration */
// /*
wire cali_memory_csb0, cali_memory_web0;
wire [CALI_MEMORY_ADDR_WIDTH-1:0] cali_memory_addr0;
assign cali_memory_csb0 = ~(valid_inst_list || cali_memory_wr_en);
assign cali_memory_web0 = ~cali_memory_wr_en;
assign cali_memory_addr0 = cali_memory_web0 ? cali_memory_rd_addr : cali_memory_wr_addr;
sram_1rw0r0w_param_freepdk45 #(
    .RAM_DEPTH(CALI_MEMORY_NUM_ENTRY),
    .ADDR_WIDTH(CALI_MEMORY_ADDR_WIDTH),
    .DATA_WIDTH(CALI_MEMORY_DATA_WIDTH)
) cali_memory (
    .clk0(clk),
    .csb0(cali_memory_csb0),
    .web0(cali_memory_web0),
    .addr0(cali_memory_addr0),
    .din0(cali_memory_wr_data),
    .dout0(cali_memory_rd_data)
);
// */
/*
assign cali_memory_rd_addr_out = cali_memory_rd_addr;
assign cali_memory_rd_data = cali_memory_rd_data_in;
*/

always @(posedge clk) begin
    if (read_inst_table_0_0) begin
        alpha_i <= cali_memory_rd_data[(3*IQ_CALI_WIDTH) +: IQ_CALI_WIDTH];
        beta_i  <= cali_memory_rd_data[(2*IQ_CALI_WIDTH) +: IQ_CALI_WIDTH];
        alpha_q <= cali_memory_rd_data[(1*IQ_CALI_WIDTH) +: IQ_CALI_WIDTH];
        beta_q  <= cali_memory_rd_data[(0*IQ_CALI_WIDTH) +: IQ_CALI_WIDTH];
    end
    
    // dc_correction <= `DC_CORRECTION_VALUE;
end

/* IQ Result */
always @(posedge clk) begin
    i_cali <= i_cali_out;
    q_cali <= q_cali_out;
    valid_cali <= valid_cali_out;
end

endmodule 
