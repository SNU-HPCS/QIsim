
module drive_datapath #(
    parameter NUM_BANK = 2,
    parameter NUM_QUBIT_PER_BANK = 16,
    parameter QUBIT_ADDR_WIDTH_PER_BANK = 4,
    parameter IQ_OUT_WIDTH              = 9, // Usually IQ_OUT_WIDTH == IQ_CALI_WIDTH
    parameter IQ_SUM_WIDTH              = 10,
    // pc
    parameter PC_WIDTH = 11, // Usually PC_WIDTH == INST_LIST_ADDR_WIDTH
    // inst_list
    parameter INST_LIST_NUM_ENTRY       = 2048,
    parameter INST_LIST_ADDR_WIDTH      = 11,
    parameter INST_LIST_DATA_WIDTH      = 17, // QUBIT_ADDR_WIDTH + INST_TABLE_ADDR_WIDTH
    // inst_table
    parameter INST_TABLE_NUM_ENTRY      = 8,
    parameter INST_TABLE_ADDR_WIDTH     = 3, // INST_LIST_DATA_WIDTH - 5 (log2(32))
    parameter INST_TABLE_DATA_WIDTH     = 34, // ENVE_MEMORY_ADDR_WIDTH *2 + AXIS_WIDTH
    parameter AXIS_WIDTH                = 2,
    // enve_memory
    parameter ENVE_MEMORY_NUM_ENTRY     = 40960,
    parameter ENVE_MEMORY_ADDR_WIDTH    = 16,
    parameter PHASE_WIDTH               = 10,
    parameter AMP_WIDTH                 = 8,
    // cali_memory
    parameter CALI_MEMORY_NUM_ENTRY     = 16,
    parameter CALI_MEMORY_ADDR_WIDTH    = 4, // == QUBIT_ADDR_WIDTH_PER_BANK
    parameter CALI_MEMORY_DATA_WIDTH    = 36,
    // nco
    parameter NCO_N                     = 22,
    parameter Z_CORR_WIDTH              = 12,
    parameter SIN_LUT_NUM_ENTRY         = 1024,
    parameter SIN_LUT_ADDR_WIDTH        = PHASE_WIDTH,
    parameter SIN_LUT_DATA_WIDTH        = AMP_WIDTH,
    // calibration
    parameter IQ_CALI_WIDTH             = 9
)(
    clk,
    rst,

    update_pc,

    start_read_addr, // start_read_addr from drive_control_enve_memory_unit
    set_enve_memory_addr,
    increment_enve_memory_addr,
    valid_addr_out,

    local_is_read_env_fin,

    nco_z_corr_wr_en,
    nco_phase_wr_en,
    nco_z_corr_mode,

    valid_inst_table_out,
    is_read_env_fin_out,
    qubit_sel,

    is_rz_fin_out,

    valid_out,
    i_out,
    q_out,

    // For memory initialization
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


localparam NUM_NCO = NUM_QUBIT_PER_BANK;
localparam ENVE_MEMORY_DATA_WIDTH = PHASE_WIDTH + AMP_WIDTH;
localparam Z_CORR_MEMORY_ADDR_WIDTH = QUBIT_ADDR_WIDTH_PER_BANK;
localparam Z_CORR_MEMORY_DATA_WIDTH = Z_CORR_WIDTH*NUM_QUBIT_PER_BANK*NUM_BANK;

////////////////////////////////
////// In/Out declaration //////
////////////////////////////////

input                                           clk; 
input                                           rst;

/* PC */
input                                           update_pc;

/* Instruction fetch */
input       [NUM_BANK-1:0]                      start_read_addr;
input       [NUM_BANK-1:0]                      set_enve_memory_addr;
input       [NUM_BANK-1:0]                      increment_enve_memory_addr;
input       [NUM_BANK-1:0]                      local_is_read_env_fin;

output      [NUM_BANK-1:0]                      valid_addr_out;

input       [NUM_BANK*NUM_QUBIT_PER_BANK-1:0]   nco_z_corr_wr_en;
input       [NUM_BANK*NUM_QUBIT_PER_BANK-1:0]   nco_phase_wr_en;
input       [NUM_BANK*NUM_QUBIT_PER_BANK-1:0]   nco_z_corr_mode;

output      [NUM_BANK-1:0]                      valid_inst_table_out;
output      [NUM_BANK-1:0]                      is_read_env_fin_out;
output      [NUM_BANK*QUBIT_ADDR_WIDTH_PER_BANK-1:0]  qubit_sel;

output      [NUM_BANK-1:0]                      is_rz_fin_out;

output                                          valid_out;
output      [IQ_SUM_WIDTH-1:0]                  i_out;
output      [IQ_SUM_WIDTH-1:0]                  q_out;

// for memory initialization
input       [NUM_BANK-1:0]                      bank_wr_sel;

input                                           inst_list_wr_en;
input       [INST_LIST_ADDR_WIDTH-1:0]          inst_list_wr_addr;
input       [INST_LIST_DATA_WIDTH-1:0]          inst_list_wr_data;

input       [NUM_QUBIT_PER_BANK-1:0]            inst_table_wr_sel;
input                                           inst_table_wr_en;
input       [INST_TABLE_ADDR_WIDTH-1:0]         inst_table_wr_addr;
input       [INST_TABLE_DATA_WIDTH-1:0]         inst_table_wr_data;

input                                           enve_memory_wr_en;
input       [ENVE_MEMORY_ADDR_WIDTH-1:0]        enve_memory_wr_addr;
input       [ENVE_MEMORY_DATA_WIDTH-1:0]        enve_memory_wr_data;

input                                           cali_memory_wr_en;
input       [CALI_MEMORY_ADDR_WIDTH-1:0]        cali_memory_wr_addr;
input       [CALI_MEMORY_DATA_WIDTH-1:0]        cali_memory_wr_data;

input       [NUM_NCO-1:0]                       nco_ftw_wr_en;
input       [NUM_NCO*NCO_N-1:0]                 nco_ftw_in;

input                                           z_corr_memory_wr_en;
input       [Z_CORR_MEMORY_ADDR_WIDTH-1:0]      z_corr_memory_wr_addr;
input       [Z_CORR_MEMORY_DATA_WIDTH-1:0]      z_corr_memory_wr_data;

input                                           sin_lut_wr_en;
input                                           cos_lut_wr_en;
input       [SIN_LUT_ADDR_WIDTH-1:0]            sinusoidal_lut_wr_addr; 
input       [SIN_LUT_DATA_WIDTH-1:0]            sinusoidal_lut_wr_data;

////////////////////////////////
/////// Port declaration ///////
////////////////////////////////

wire        [PC_WIDTH-1:0]                                  PC;
wire        [PC_WIDTH-1:0]                                  next_PC; // next_PC = PC + 1

reg                                                         valid_PC;

wire        [Z_CORR_WIDTH*NUM_QUBIT_PER_BANK*NUM_BANK-1:0]  z_corr_out;

wire        [NUM_BANK-1:0]                                  valid_out_per_bank;
wire        [NUM_BANK*IQ_OUT_WIDTH-1:0]                     i_out_per_bank;
wire        [NUM_BANK*IQ_OUT_WIDTH-1:0]                     q_out_per_bank;

reg                                                         valid_sum;
reg         [IQ_SUM_WIDTH-1:0]                              i_sum;
reg         [IQ_SUM_WIDTH-1:0]                              q_sum;

wire        [NUM_BANK-1:0]                                  valid_inst_list;
wire        [NUM_BANK*Z_CORR_WIDTH-1:0]                     phase_imm;
wire        [NUM_BANK-1:0]                                  rz_mode_in;

wire        [NUM_BANK-1:0]                                  rz_mode_out;
wire        [NUM_BANK-1:0]                                  valid_z_corr;

//// Combinational Logic ////

/* Instruction fetch */
assign next_PC = PC + 1;

/* Output */
assign i_out = i_sum;
assign q_out = q_sum;
assign valid_out = valid_sum;

//// Sequential Logic ////

/* Instruction fetch */
drive_pc #(
    .PC_WIDTH(PC_WIDTH)
) pc_0 (
    .clk(clk),
    .rst(rst),
    .update_pc(update_pc),
    .next_PC(next_PC),
    .PC(PC)
);

always @(posedge clk) begin
    if (update_pc) begin
        valid_PC <= 1'b1;
    end
    else begin
        valid_PC <= 1'b0;
    end
end

/* signal_gen_unit */

genvar i;
generate
    for(i = 0; i < NUM_BANK; i = i +1) begin: genblk_signal_gen_unit
        wire set_enve_memory_addr_i;
        wire increment_enve_memory_addr_i;
        wire [NUM_QUBIT_PER_BANK-1:0] nco_z_corr_wr_en_i;
        wire [NUM_QUBIT_PER_BANK-1:0] nco_phase_wr_en_i;
        wire [NUM_QUBIT_PER_BANK-1:0] nco_z_corr_mode_i;
        wire [Z_CORR_WIDTH*NUM_QUBIT_PER_BANK-1:0] z_corr_out_i;

        wire [QUBIT_ADDR_WIDTH_PER_BANK-1:0] qubit_sel_i;
        wire valid_inst_table_out_i;
        wire is_read_env_fin_out_i;

        wire valid_addr_out_i;

        wire rz_mode_out_i;
        wire rz_mode_in_i;
        wire [Z_CORR_WIDTH-1:0] phase_imm_i;
        wire valid_inst_list_i;

        wire valid_z_corr_i;
        wire is_rz_fin_out_i;

        wire valid_out_i;
        wire [IQ_OUT_WIDTH-1:0] i_out_i;
        wire [IQ_OUT_WIDTH-1:0] q_out_i;

        wire inst_list_wr_en_i;
        wire inst_table_wr_en_i;
        wire enve_memory_wr_en_i;
        wire cali_memory_wr_en_i;
        wire [NUM_NCO-1:0] nco_ftw_wr_en_i;
        wire start_read_addr_i;

        // input
        assign set_enve_memory_addr_i = set_enve_memory_addr[i];
        assign increment_enve_memory_addr_i = increment_enve_memory_addr[i];
        assign nco_z_corr_wr_en_i = nco_z_corr_wr_en[i*NUM_QUBIT_PER_BANK +: NUM_QUBIT_PER_BANK];
        assign nco_phase_wr_en_i = nco_phase_wr_en[i*NUM_QUBIT_PER_BANK +: NUM_QUBIT_PER_BANK];
        assign nco_z_corr_mode_i = nco_z_corr_mode[i*NUM_QUBIT_PER_BANK +: NUM_QUBIT_PER_BANK];
        assign z_corr_out_i = z_corr_out[i*Z_CORR_WIDTH*NUM_QUBIT_PER_BANK +: Z_CORR_WIDTH*NUM_QUBIT_PER_BANK];
        assign start_read_addr_i = start_read_addr[i];
        assign rz_mode_out_i = rz_mode_out[i];
        // output
        assign qubit_sel[i*QUBIT_ADDR_WIDTH_PER_BANK +: QUBIT_ADDR_WIDTH_PER_BANK] = qubit_sel_i;
        assign valid_inst_table_out[i] = valid_inst_table_out_i;
        assign is_read_env_fin_out[i] = is_read_env_fin_out_i;
        assign valid_out_per_bank[i] = valid_out_i;
        assign i_out_per_bank[i*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] = i_out_i;
        assign q_out_per_bank[i*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] = q_out_i;
        assign valid_addr_out[i] = valid_addr_out_i;
        assign rz_mode_in[i] = rz_mode_in_i;
        assign valid_inst_list[i] = valid_inst_list_i;
        assign phase_imm[i*Z_CORR_WIDTH +: Z_CORR_WIDTH] = phase_imm_i;

        assign valid_z_corr_i = valid_z_corr[i];
        assign is_rz_fin_out[i] = is_rz_fin_out_i;

        // memory initialization
        assign inst_list_wr_en_i = inst_list_wr_en & bank_wr_sel[i];
        assign inst_table_wr_en_i = inst_table_wr_en & bank_wr_sel[i];
        assign enve_memory_wr_en_i = enve_memory_wr_en & bank_wr_sel[i];
        assign cali_memory_wr_en_i = cali_memory_wr_en & bank_wr_sel[i];
        assign nco_ftw_wr_en_i = nco_ftw_wr_en & {NUM_NCO{bank_wr_sel[i]}};

        drive_signal_gen_unit #(
            .NUM_QUBIT(NUM_QUBIT_PER_BANK),
            .QUBIT_ADDR_WIDTH(QUBIT_ADDR_WIDTH_PER_BANK),
            .IQ_OUT_WIDTH(IQ_OUT_WIDTH),

            .INST_LIST_NUM_ENTRY(INST_LIST_NUM_ENTRY),
            .INST_LIST_ADDR_WIDTH(INST_LIST_ADDR_WIDTH),
            .INST_LIST_DATA_WIDTH(INST_LIST_DATA_WIDTH),

            .INST_TABLE_NUM_ENTRY(INST_TABLE_NUM_ENTRY),
            .INST_TABLE_ADDR_WIDTH(INST_TABLE_ADDR_WIDTH),
            .INST_TABLE_DATA_WIDTH(INST_TABLE_DATA_WIDTH),
            .AXIS_WIDTH(AXIS_WIDTH),

            .ENVE_MEMORY_NUM_ENTRY(ENVE_MEMORY_NUM_ENTRY),
            .ENVE_MEMORY_ADDR_WIDTH(ENVE_MEMORY_ADDR_WIDTH),
            .PHASE_WIDTH(PHASE_WIDTH),
            .AMP_WIDTH(AMP_WIDTH),

            .CALI_MEMORY_NUM_ENTRY(CALI_MEMORY_NUM_ENTRY),
            .CALI_MEMORY_ADDR_WIDTH(CALI_MEMORY_ADDR_WIDTH),
            .CALI_MEMORY_DATA_WIDTH(CALI_MEMORY_DATA_WIDTH),

            .NCO_N(NCO_N),
            .Z_CORR_WIDTH(Z_CORR_WIDTH),
            .SIN_LUT_NUM_ENTRY(SIN_LUT_NUM_ENTRY),
            .SIN_LUT_ADDR_WIDTH(SIN_LUT_ADDR_WIDTH),
            .SIN_LUT_DATA_WIDTH(SIN_LUT_DATA_WIDTH),

            .IQ_CALI_WIDTH(IQ_CALI_WIDTH)
        ) drive_signal_gen_unit_instance (
            .clk(clk),
            .rst(rst),
            .PC(PC),
            .valid_PC_in(valid_PC),

            .start_read_addr(start_read_addr_i), // NUM_BANK
            .set_enve_memory_addr(set_enve_memory_addr_i),
            .increment_enve_memory_addr(increment_enve_memory_addr_i),

            .valid_addr_out(valid_addr_out_i),
            .valid_inst_list_out(valid_inst_list_i),
            .phase_imm_out(phase_imm_i),

            .valid_z_corr_in(valid_z_corr_i),
            .rz_mode_in(rz_mode_out_i),
            .rz_mode_out(rz_mode_in_i),

            .inst_list_wr_en(inst_list_wr_en_i),
            .inst_list_wr_addr(inst_list_wr_addr), // NUM_BANK * INST_LIST_ADDR_WIDTH
            .inst_list_wr_data(inst_list_wr_data), // NUM_BANK * INST_LIST_DATA_WIDTH

            .inst_table_wr_sel(inst_table_wr_sel),
            .inst_table_wr_en(inst_table_wr_en_i),
            .inst_table_wr_addr(inst_table_wr_addr),
            .inst_table_wr_data(inst_table_wr_data),

            .enve_memory_wr_en(enve_memory_wr_en_i),
            .enve_memory_wr_addr(enve_memory_wr_addr),
            .enve_memory_wr_data(enve_memory_wr_data),

            .cali_memory_wr_en(cali_memory_wr_en_i),
            .cali_memory_wr_addr(cali_memory_wr_addr),
            .cali_memory_wr_data(cali_memory_wr_data),

            .sin_lut_wr_en(sin_lut_wr_en),
            .cos_lut_wr_en(cos_lut_wr_en),
            .sinusoidal_lut_wr_addr(sinusoidal_lut_wr_addr),
            .sinusoidal_lut_wr_data(sinusoidal_lut_wr_data),

            .qubit_sel_out(qubit_sel_i),
            .valid_inst_table_out(valid_inst_table_out_i),
            .is_read_env_fin(is_read_env_fin_out_i),
            .is_rz_fin_out(is_rz_fin_out_i),

            .nco_ftw_wr_en(nco_ftw_wr_en_i),
            .nco_ftw_in(nco_ftw_in),
            
            .nco_z_corr_wr_en(nco_z_corr_wr_en_i),
            .nco_z_corr_in(z_corr_out_i),
            .nco_phase_wr_en(nco_phase_wr_en_i),
            .nco_z_corr_mode(nco_z_corr_mode_i),
            
            .valid_out(valid_out_i),
            .i_out(i_out_i),
            .q_out(q_out_i)
        );
    end
endgenerate

/* z_corr table */
drive_z_corr_table #(
    .NUM_BANK(NUM_BANK),
    .NUM_QUBIT_PER_BANK(NUM_QUBIT_PER_BANK),
    .QUBIT_ADDR_WIDTH_PER_BANK(QUBIT_ADDR_WIDTH_PER_BANK),
    .Z_CORR_WIDTH(Z_CORR_WIDTH)
) drive_z_corr_table_instance (
    .clk(clk),
    .rst(rst),
    .z_corr_memory_wr_sel(bank_wr_sel),
    .z_corr_memory_wr_en(z_corr_memory_wr_en),
    .z_corr_memory_wr_addr(z_corr_memory_wr_addr),
    .z_corr_memory_wr_data(z_corr_memory_wr_data),
    .qubit_sel(qubit_sel),
    .is_read_env_fin(is_read_env_fin_out),
    .z_corr_out(z_corr_out),

    .valid_inst_list_in(valid_inst_list),
    .phase_imm_in(phase_imm),
    .rz_mode_in(rz_mode_in),
    .rz_mode_out(rz_mode_out),
    .valid_z_corr_out(valid_z_corr)
);

/* Output */
generate
    if (NUM_BANK == 1) begin: genblk_iq_sum_1
        always @(posedge clk) begin
            i_sum       <= i_out_per_bank;
            q_sum       <= q_out_per_bank;
            valid_sum   <= valid_out_per_bank;
        end
    end
    else if (NUM_BANK == 2) begin: genblk_iq_sum_2
        always @(posedge clk) begin
            i_sum       <= (valid_out_per_bank[0] ? i_out_per_bank[0*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[1] ? i_out_per_bank[1*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0);
            q_sum       <= (valid_out_per_bank[0] ? q_out_per_bank[0*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[1] ? q_out_per_bank[1*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0);
            valid_sum   <= |valid_out_per_bank;
        end
    end
    else if (NUM_BANK == 3) begin: genblk_iq_sum_3
        always @(posedge clk) begin
            i_sum       <= (valid_out_per_bank[0] ? i_out_per_bank[0*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[1] ? i_out_per_bank[1*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[2] ? i_out_per_bank[2*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0);
            q_sum       <= (valid_out_per_bank[0] ? q_out_per_bank[0*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[1] ? q_out_per_bank[1*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[2] ? q_out_per_bank[2*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0);
            valid_sum   <= |valid_out_per_bank;
        end
    end
    else if (NUM_BANK == 4) begin: genblk_iq_sum_4
        always @(posedge clk) begin
            i_sum       <= (valid_out_per_bank[0] ? i_out_per_bank[0*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[1] ? i_out_per_bank[1*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[2] ? i_out_per_bank[2*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[3] ? i_out_per_bank[3*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0);
            q_sum       <= (valid_out_per_bank[0] ? q_out_per_bank[0*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[1] ? q_out_per_bank[1*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[2] ? q_out_per_bank[2*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[3] ? q_out_per_bank[3*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0);
            valid_sum   <= |valid_out_per_bank;
        end
    end
    else if (NUM_BANK == 8) begin: genblk_iq_sum_8
        always @(posedge clk) begin
            i_sum       <= (valid_out_per_bank[0] ? i_out_per_bank[0*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[1] ? i_out_per_bank[1*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[2] ? i_out_per_bank[2*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[3] ? i_out_per_bank[3*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[4] ? i_out_per_bank[4*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[5] ? i_out_per_bank[5*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[6] ? i_out_per_bank[6*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[7] ? i_out_per_bank[7*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0);
            q_sum       <= (valid_out_per_bank[0] ? q_out_per_bank[0*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[1] ? q_out_per_bank[1*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[2] ? q_out_per_bank[2*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[3] ? q_out_per_bank[3*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[4] ? q_out_per_bank[4*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[5] ? q_out_per_bank[5*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[6] ? q_out_per_bank[6*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0)
                        +  (valid_out_per_bank[7] ? q_out_per_bank[7*IQ_OUT_WIDTH +: IQ_OUT_WIDTH] : 0);
            valid_sum   <= |valid_out_per_bank;
        end
    end
endgenerate


endmodule 
