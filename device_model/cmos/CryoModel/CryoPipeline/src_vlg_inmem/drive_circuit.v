// Drive circuit (based on Horse Ridge I)

`include "define_drive_circuit.v"

module drive_circuit (
    clk,
    rst,
    trigger,
    //
    valid_out,
    i_out,
    q_out,
    //
    bank_wr_sel,
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
    nco_ftw_wr_en,
    nco_ftw_in,
    z_corr_memory_wr_en,
    z_corr_memory_wr_addr,
    z_corr_memory_wr_data,
    sin_lut_wr_en,
    cos_lut_wr_en,
    sinusoidal_lut_wr_addr,
    sinusoidal_lut_wr_data
);

// Port declaration
input                                               clk;
input                                               rst;
input                                               trigger;

output                                              valid_out;
output  [`DRIVE_IQ_SUM_WIDTH-1:0]                         i_out;
output  [`DRIVE_IQ_SUM_WIDTH-1:0]                         q_out;

input   [`DRIVE_NUM_BANK-1:0]                             bank_wr_sel;
input                                               inst_list_wr_en;
input   [`DRIVE_INST_LIST_ADDR_WIDTH-1:0]                 inst_list_wr_addr;
input   [`DRIVE_INST_LIST_DATA_WIDTH-1:0]                 inst_list_wr_data;
input   [`DRIVE_NUM_QUBIT_PER_BANK-1:0]                   inst_table_wr_sel;
input                                               inst_table_wr_en;
input   [`DRIVE_INST_TABLE_ADDR_WIDTH-1:0]                inst_table_wr_addr;
input   [`DRIVE_INST_TABLE_DATA_WIDTH-1:0]                inst_table_wr_data;
input                                               enve_memory_wr_en;
input   [`DRIVE_ENVE_MEMORY_ADDR_WIDTH-1:0]               enve_memory_wr_addr;
input   [`DRIVE_ENVE_MEMORY_DATA_WIDTH-1:0]               enve_memory_wr_data;
input                                               cali_memory_wr_en;
input   [`DRIVE_CALI_MEMORY_ADDR_WIDTH-1:0]               cali_memory_wr_addr;
input   [`DRIVE_CALI_MEMORY_DATA_WIDTH-1:0]               cali_memory_wr_data;
input   [`DRIVE_NUM_NCO-1:0]                              nco_ftw_wr_en;
input   [`DRIVE_NUM_NCO*`DRIVE_NCO_N-1:0]                       nco_ftw_in;
input                                               z_corr_memory_wr_en;
input   [`DRIVE_Z_CORR_MEMORY_ADDR_WIDTH-1:0]             z_corr_memory_wr_addr;
input   [`DRIVE_Z_CORR_MEMORY_DATA_WIDTH-1:0]             z_corr_memory_wr_data;
input                                               sin_lut_wr_en;
input                                               cos_lut_wr_en;
input   [`DRIVE_SIN_LUT_ADDR_WIDTH-1:0]                   sinusoidal_lut_wr_addr; 
input   [`DRIVE_SIN_LUT_DATA_WIDTH-1:0]                   sinusoidal_lut_wr_data;

// Internal connections
wire                                                update_pc;
wire    [`DRIVE_NUM_BANK-1:0]                             start_read_addr;
wire    [`DRIVE_NUM_BANK-1:0]                             set_enve_memory_addr;
wire    [`DRIVE_NUM_BANK-1:0]                             increment_enve_memory_addr;
wire    [`DRIVE_NUM_BANK-1:0]                             local_is_read_env_fin;
wire    [`DRIVE_NUM_BANK*`DRIVE_NUM_QUBIT_PER_BANK-1:0]         nco_z_corr_wr_en;
wire    [`DRIVE_NUM_BANK*`DRIVE_NUM_QUBIT_PER_BANK-1:0]         nco_phase_wr_en;
wire    [`DRIVE_NUM_BANK*`DRIVE_NUM_QUBIT_PER_BANK-1:0]         nco_z_corr_mode;
wire    [`DRIVE_NUM_BANK-1:0]                             valid_inst_table;
wire    [`DRIVE_NUM_BANK-1:0]                             is_read_env_fin;
wire    [`DRIVE_NUM_BANK*`DRIVE_QUBIT_ADDR_WIDTH_PER_BANK-1:0]  qubit_sel;
wire    [`DRIVE_NUM_BANK-1:0]                             is_rz_fin;
wire    [`DRIVE_NUM_BANK-1:0]                                   valid_addr;
// Module instantiations

drive_control_unit #(
    .NUM_BANK(`DRIVE_NUM_BANK),
    .NUM_QUBIT_PER_BANK(`DRIVE_NUM_QUBIT_PER_BANK),
    .QUBIT_ADDR_WIDTH_PER_BANK(`DRIVE_QUBIT_ADDR_WIDTH_PER_BANK)
) control_unit_0 (
    .clk(clk),
    .rst(rst),
    .trigger(trigger),
    .is_read_env_fin_in(is_read_env_fin),
    .valid_inst_table_in(valid_inst_table),
    .qubit_sel(qubit_sel),
    .update_pc(update_pc),
    .start_read_addr(start_read_addr),
    .set_enve_memory_addr(set_enve_memory_addr),
    .increment_enve_memory_addr(increment_enve_memory_addr),
    .nco_z_corr_wr_en(nco_z_corr_wr_en),
    .nco_phase_wr_en(nco_phase_wr_en),
    .nco_z_corr_mode(nco_z_corr_mode),
    .local_is_read_env_fin(local_is_read_env_fin),
    .valid_addr_in(valid_addr),
    .is_rz_fin_in(is_rz_fin)
);

drive_datapath #(
    .NUM_BANK(`DRIVE_NUM_BANK),
    .NUM_QUBIT_PER_BANK(`DRIVE_NUM_QUBIT_PER_BANK),
    .QUBIT_ADDR_WIDTH_PER_BANK(`DRIVE_QUBIT_ADDR_WIDTH_PER_BANK),
    .IQ_OUT_WIDTH(`DRIVE_IQ_OUT_WIDTH),
    .IQ_SUM_WIDTH(`DRIVE_IQ_SUM_WIDTH),

    .PC_WIDTH(`DRIVE_PC_WIDTH),
    
    .INST_LIST_NUM_ENTRY(`DRIVE_INST_LIST_NUM_ENTRY),
    .INST_LIST_ADDR_WIDTH(`DRIVE_INST_LIST_ADDR_WIDTH),
    .INST_LIST_DATA_WIDTH(`DRIVE_INST_LIST_DATA_WIDTH),
    
    .INST_TABLE_NUM_ENTRY(`DRIVE_INST_TABLE_NUM_ENTRY),
    .INST_TABLE_ADDR_WIDTH(`DRIVE_INST_TABLE_ADDR_WIDTH),
    .INST_TABLE_DATA_WIDTH(`DRIVE_INST_TABLE_DATA_WIDTH),
    .AXIS_WIDTH(`DRIVE_AXIS_WIDTH),

    .ENVE_MEMORY_NUM_ENTRY(`DRIVE_ENVE_MEMORY_NUM_ENTRY),
    .ENVE_MEMORY_ADDR_WIDTH(`DRIVE_ENVE_MEMORY_ADDR_WIDTH),
    .PHASE_WIDTH(`DRIVE_PHASE_WIDTH),
    .AMP_WIDTH(`DRIVE_AMP_WIDTH),

    .CALI_MEMORY_NUM_ENTRY(`DRIVE_CALI_MEMORY_NUM_ENTRY),
    .CALI_MEMORY_ADDR_WIDTH(`DRIVE_CALI_MEMORY_ADDR_WIDTH),
    .CALI_MEMORY_DATA_WIDTH(`DRIVE_CALI_MEMORY_DATA_WIDTH),

    .NCO_N(`DRIVE_NCO_N),
    .Z_CORR_WIDTH(`DRIVE_Z_CORR_WIDTH),
    .SIN_LUT_NUM_ENTRY(`DRIVE_SIN_LUT_NUM_ENTRY),
    .SIN_LUT_ADDR_WIDTH(`DRIVE_SIN_LUT_ADDR_WIDTH),
    .SIN_LUT_DATA_WIDTH(`DRIVE_SIN_LUT_DATA_WIDTH),

    .IQ_CALI_WIDTH(`DRIVE_IQ_CALI_WIDTH)
) datapath_0 (
    .clk(clk),
    .rst(rst),
    .update_pc(update_pc),
    .start_read_addr(start_read_addr),
    .set_enve_memory_addr(set_enve_memory_addr),
    .increment_enve_memory_addr(increment_enve_memory_addr),
    .local_is_read_env_fin(local_is_read_env_fin),
    .valid_addr_out(valid_addr),
    .nco_z_corr_wr_en(nco_z_corr_wr_en),
    .nco_phase_wr_en(nco_phase_wr_en),
    .nco_z_corr_mode(nco_z_corr_mode),
    .valid_inst_table_out(valid_inst_table),
    .is_read_env_fin_out(is_read_env_fin),
    .qubit_sel(qubit_sel),
    .is_rz_fin_out(is_rz_fin),
    .valid_out(valid_out),
    .i_out(i_out),
    .q_out(q_out),
    .bank_wr_sel(bank_wr_sel),
    .inst_list_wr_en(inst_list_wr_en),
    .inst_list_wr_addr(inst_list_wr_addr),
    .inst_list_wr_data(inst_list_wr_data),
    .inst_table_wr_sel(inst_table_wr_sel),
    .inst_table_wr_en(inst_table_wr_en),
    .inst_table_wr_addr(inst_table_wr_addr),
    .inst_table_wr_data(inst_table_wr_data),
    .enve_memory_wr_en(enve_memory_wr_en),
    .enve_memory_wr_addr(enve_memory_wr_addr),
    .enve_memory_wr_data(enve_memory_wr_data),
    .cali_memory_wr_en(cali_memory_wr_en),
    .cali_memory_wr_addr(cali_memory_wr_addr),
    .cali_memory_wr_data(cali_memory_wr_data),
    .nco_ftw_wr_en(nco_ftw_wr_en),
    .nco_ftw_in(nco_ftw_in),
    .z_corr_memory_wr_en(z_corr_memory_wr_en),
    .z_corr_memory_wr_addr(z_corr_memory_wr_addr),
    .z_corr_memory_wr_data(z_corr_memory_wr_data),
    .sin_lut_wr_en(sin_lut_wr_en),
    .cos_lut_wr_en(cos_lut_wr_en),
    .sinusoidal_lut_wr_addr(sinusoidal_lut_wr_addr),
    .sinusoidal_lut_wr_data(sinusoidal_lut_wr_data)
);

endmodule
