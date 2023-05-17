module drive_control_unit #(
    parameter NUM_BANK = 2,
    parameter NUM_QUBIT_PER_BANK = 16,
    parameter QUBIT_ADDR_WIDTH_PER_BANK = 4
    // FILLME
)(
    clk,
    rst,
    trigger,

    is_read_env_fin_in,
    
    valid_inst_table_in,
    qubit_sel,

    is_rz_fin_in,

    update_pc,

    start_read_addr,
    set_enve_memory_addr,
    increment_enve_memory_addr,

    nco_z_corr_wr_en,
    nco_phase_wr_en,
    nco_z_corr_mode,

    local_is_read_env_fin,
    valid_addr_in
);

////////////////////////////////
//// Localparam declaration ////
////////////////////////////////


////////////////////////////////
////// In/Out declaration //////
////////////////////////////////
input                                                   clk;
input                                                   rst;
input                                                   trigger;

input       [NUM_BANK-1:0]                              is_read_env_fin_in;

input       [NUM_BANK-1:0]                              valid_inst_table_in;
input       [NUM_BANK*QUBIT_ADDR_WIDTH_PER_BANK-1:0]    qubit_sel;

input       [NUM_BANK-1:0]                              is_rz_fin_in;
input       [NUM_BANK-1:0]                              valid_addr_in;

output                                                  update_pc;

output      [NUM_BANK-1:0]                              start_read_addr;
output      [NUM_BANK-1:0]                              set_enve_memory_addr;
output      [NUM_BANK-1:0]                              increment_enve_memory_addr;

output      [NUM_BANK*NUM_QUBIT_PER_BANK-1:0]           nco_z_corr_wr_en;
output      [NUM_BANK*NUM_QUBIT_PER_BANK-1:0]           nco_phase_wr_en;
output      [NUM_BANK*NUM_QUBIT_PER_BANK-1:0]           nco_z_corr_mode;
output reg  [NUM_BANK-1:0]                              local_is_read_env_fin;

////////////////////////////////
/////// Port declaration ///////
////////////////////////////////
wire                            glb_is_read_env_fin;
wire                            glb_is_rz_fin;


////////////////////////////////
////// Combinational Logic /////
////////////////////////////////
assign glb_is_read_env_fin = &(local_is_read_env_fin);
assign glb_is_rz_fin = |(is_rz_fin_in);
////////////////////////////////
/////// Sequential Logic ///////
////////////////////////////////

always @(posedge clk) begin
    /*
    if (rst) begin
        local_is_read_env_fin <= 0;
    end
    else if (update_pc) begin
        local_is_read_env_fin <= 0;
    end
    // else if (|set_enve_memory_addr) begin
    //     local_is_read_env_fin <= 0;
    // end
    else begin
        local_is_read_env_fin <= local_is_read_env_fin | is_read_env_fin_in;
    end
    */
    if (rst) begin
        local_is_read_env_fin <= {NUM_BANK{1'b1}};
    end
    else begin
        // local_is_read_env_fin <= is_read_env_fin_in;
        local_is_read_env_fin <= ~valid_addr_in;
    end
end

drive_control_signal_gen_unit drive_control_signal_gen_unit_instance
(
    .clk(clk),
    .rst(rst),
    .glb_is_read_env_fin(glb_is_read_env_fin),
    .trigger(trigger),
    .is_rz_fin(glb_is_rz_fin),
    .update_pc(update_pc)
);

genvar i;
generate
    for(i = 0; i < NUM_BANK; i = i +1) begin: genblk_enve_memory_unit
        wire valid_inst_table_in_i;
        wire is_read_env_fin_in_i;
        wire start_read_addr_i;
        wire set_enve_memory_addr_i;
        wire increment_enve_memory_addr_i;

        assign valid_inst_table_in_i = valid_inst_table_in[i];
        assign is_read_env_fin_in_i = is_read_env_fin_in[i];
        assign start_read_addr[i] = start_read_addr_i;
        assign set_enve_memory_addr[i] = set_enve_memory_addr_i;
        assign increment_enve_memory_addr[i] = increment_enve_memory_addr_i;

        drive_control_enve_memory_unit drive_control_enve_memory_unit_instance
        (
            
            .clk(clk),
            .rst(rst),
            .valid_inst_table_in(valid_inst_table_in_i),
            .is_read_env_fin(is_read_env_fin_in_i),
            .start_read_addr(start_read_addr_i),
            .set_enve_memory_addr(set_enve_memory_addr_i),
            .increment_enve_memory_addr(increment_enve_memory_addr_i)
        );
    end
endgenerate

generate
    for(i = 0; i < NUM_BANK; i = i +1) begin: genblk_z_corr_unit
        wire valid_inst_table_in_i;
        wire [QUBIT_ADDR_WIDTH_PER_BANK-1:0] qubit_sel_i;
        wire [NUM_QUBIT_PER_BANK-1:0]        nco_z_corr_wr_en_i;
        wire [NUM_QUBIT_PER_BANK-1:0]        nco_phase_wr_en_i;
        wire [NUM_QUBIT_PER_BANK-1:0]        nco_z_corr_mode_i;
        wire local_is_read_env_fin_i;
        wire valid_z_corr_in_i;

        assign valid_inst_table_in_i = valid_inst_table_in[i];
        assign qubit_sel_i = qubit_sel[i*QUBIT_ADDR_WIDTH_PER_BANK +: QUBIT_ADDR_WIDTH_PER_BANK];
        assign local_is_read_env_fin_i = local_is_read_env_fin[i];

        assign nco_z_corr_wr_en[i*NUM_QUBIT_PER_BANK +: NUM_QUBIT_PER_BANK] = nco_z_corr_wr_en_i;
        assign nco_phase_wr_en[i*NUM_QUBIT_PER_BANK +: NUM_QUBIT_PER_BANK] = nco_phase_wr_en_i;
        assign nco_z_corr_mode[i*NUM_QUBIT_PER_BANK +: NUM_QUBIT_PER_BANK] = nco_z_corr_mode_i;

        drive_control_z_corr_unit drive_control_z_corr_unit_instance
        (
            .clk(clk),
            .rst(rst),
            .valid_inst_table_in(valid_inst_table_in_i),
            .glb_is_read_env_fin(glb_is_read_env_fin),
            .local_is_read_env_fin(local_is_read_env_fin_i),
            .qubit_sel(qubit_sel_i),
            .nco_z_corr_wr_en(nco_z_corr_wr_en_i),
            .nco_phase_wr_en(nco_phase_wr_en_i),
            .nco_z_corr_mode(nco_z_corr_mode_i)
        );
    end
endgenerate

endmodule 
