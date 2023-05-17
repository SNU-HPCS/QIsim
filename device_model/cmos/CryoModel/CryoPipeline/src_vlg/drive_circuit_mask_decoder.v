
`include "define_drive_circuit_mask_decoder.v"

module drive_circuit_mask_decoder (
    clk,
    rst,

    valid_in,
    start_time_in,
    bs_select_in,
    mask_in,

    inst_out,
    inst_wr_en_out
);

// Port declaration
input                                               clk;
input                                               rst;

input                                               valid_in;
input   [`DRIVE_START_TIME_WIDTH-1:0]               start_time_in;
input   [`DRIVE_BS_SELECT_WIDTH-1:0]                bs_select_in;
input   [`DRIVE_NUM_TOTAL_QUBIT-1:0]                mask_in;

output  [`DRIVE_INST_WIDTH_TOTAL_GROUP-1:0]         inst_out;
output  [`DRIVE_NUM_BANK_PER_GROUP*`DRIVE_NUM_GROUP-1:0]            inst_wr_en_out;

// Internal connections

reg wr_en_y;
reg [`DRIVE_START_TIME_WIDTH-1:0] start_time;
reg [`DRIVE_Z_PHASE_WIDTH-1:0] phase;

wire [`DRIVE_Z_PHASE_WIDTH-1:0] inst_y;

reg wr_en_z;

wire global_wr_en;

wire [`DRIVE_NUM_PHASE*`DRIVE_Z_PHASE_WIDTH-1:0]  mux_phase_data_in;
wire [`DRIVE_BS_SELECT_WIDTH-1:0]               mux_phase_sel;
wire [`DRIVE_Z_PHASE_WIDTH-1:0]                   mux_phase_data_out;

wire [2*`DRIVE_Z_PHASE_WIDTH-1:0] mux_inst_data_in;
wire                            mux_inst_sel;
wire [`DRIVE_Z_PHASE_WIDTH-1:0]   mux_inst_data_out;

// Module instantiations

always @(posedge clk) begin
    wr_en_y <= valid_in;
    if (rst) begin
        start_time <= 0;
        phase <= 0;
    end
    else if (valid_in) begin
        start_time <= start_time_in;
        phase <= mux_phase_data_out;
    end
end

always @(posedge clk) begin
    wr_en_z <= wr_en_y;
end

//

assign mux_phase_sel = bs_select_in;
assign mux_phase_data_in = {
    `DRIVE_CONST_PHASE_0,
    `DRIVE_CONST_PHASE_1,
    `DRIVE_CONST_PHASE_2,
    `DRIVE_CONST_PHASE_3,
    `DRIVE_CONST_PHASE_4,
    `DRIVE_CONST_PHASE_5,
    `DRIVE_CONST_PHASE_6,
    `DRIVE_CONST_PHASE_7
};

mux_param #(
    .NUM_INPUT(`DRIVE_NUM_PHASE),
    .SEL_WIDTH(`DRIVE_BS_SELECT_WIDTH),
    .DATA_WIDTH(`DRIVE_Z_PHASE_WIDTH)
) mux_phase (
    .data_in(mux_phase_data_in),
    .sel(mux_phase_sel),
    .data_out(mux_phase_data_out)
);

//

assign inst_y = `DRIVE_CONST_Y_INST;
assign mux_inst_data_in = {phase, inst_y};
assign mux_inst_sel = wr_en_y;

mux_param #(
    .NUM_INPUT(2),
    .SEL_WIDTH(1),
    .DATA_WIDTH(`DRIVE_Z_PHASE_WIDTH)
) mux_inst (
    .data_in(mux_inst_data_in),
    .sel(mux_inst_sel),
    .data_out(mux_inst_data_out)
);

assign global_wr_en = wr_en_z | wr_en_y;

genvar i;
generate
    for(i = 0; i < `DRIVE_NUM_GROUP; i = i +1) begin: genblk_inst_decoder
        wire [`DRIVE_NUM_QUBIT_PER_GROUP-1:0] mask_in_i;

        wire [`DRIVE_INST_WIDTH_PER_GROUP-1:0] inst_out_i;
        wire [`DRIVE_NUM_BANK_PER_GROUP-1:0] inst_wr_en_out_i;

        assign inst_wr_en_out[`DRIVE_NUM_BANK_PER_GROUP*i +: `DRIVE_NUM_BANK_PER_GROUP] = inst_wr_en_out_i;
        assign mask_in_i = mask_in[`DRIVE_NUM_QUBIT_PER_GROUP*i +: `DRIVE_NUM_QUBIT_PER_GROUP];
        assign inst_out[`DRIVE_INST_WIDTH_PER_GROUP*i +: `DRIVE_INST_WIDTH_PER_GROUP] = inst_out_i;

        drive_circuit_qubit_addr_decoder #(
            .NUM_QUBIT(`DRIVE_NUM_QUBIT_PER_GROUP),
            .NUM_QUBIT_PER_BANK(`DRIVE_NUM_QUBIT_PER_BANK),
            .NUM_BANK(`DRIVE_NUM_BANK_PER_GROUP),
            .BANK_ADDR_WIDTH(`DRIVE_BANK_ADDR_WIDTH_PER_GROUP),
            .QUBIT_ADDR_WIDTH(`DRIVE_QUBIT_ADDR_WIDTH_PER_GROUP),
            .QUBIT_ADDR_WIDTH_PER_BANK(`DRIVE_QUBIT_ADDR_WIDTH_PER_BANK),
            .START_TIME_WIDTH(`DRIVE_START_TIME_WIDTH),
            .PHASE_WIDTH(`DRIVE_Z_PHASE_WIDTH),
            .INST_WIDTH_PER_BANK(`DRIVE_INST_WIDTH_PER_BANK)
        ) qubit_addr_decoder_instance (
            .clk(clk),
            .rst(rst),
            .mask_in(mask_in_i),
            .valid_in(valid_in),
            .global_wr_en_in(global_wr_en),
            .start_time_in(start_time),
            .z_corr_mode_in(~wr_en_y),
            .phase_in(mux_inst_data_out),
            .inst_out(inst_out_i),
            .inst_wr_en_out(inst_wr_en_out_i)
        );
    end
endgenerate
endmodule
