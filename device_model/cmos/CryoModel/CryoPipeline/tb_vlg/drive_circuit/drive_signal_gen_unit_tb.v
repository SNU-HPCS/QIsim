`timescale 1ns/100ps

module drive_signal_gen_unit_tb();

parameter NUM_QUBIT                 = 16; // number of qubits per bank
parameter QUBIT_ADDR_WIDTH          = 4;
parameter IQ_OUT_WIDTH              = 9; // Usually IQ_OUT_WIDTH == IQ_CALI_WIDTH

/* Instruction decode */
// inst_list
parameter INST_LIST_NUM_ENTRY       = 2048;
parameter INST_LIST_ADDR_WIDTH      = 11;
parameter INST_LIST_DATA_WIDTH      = 17;
// inst_table
parameter INST_TABLE_NUM_ENTRY      = 8;
parameter INST_TABLE_ADDR_WIDTH     = 3; // INST_LIST_DATA_WIDTH - 5 (log2(32))
parameter INST_TABLE_DATA_WIDTH     = 34; // ENVE_MEMORY_ADDR_WIDTH *2 + AXIS_WIDTH
parameter AXIS_WIDTH                = 2;
// enve_memory
parameter ENVE_MEMORY_NUM_ENTRY     = 40960;
parameter ENVE_MEMORY_ADDR_WIDTH    = 16;
parameter PHASE_WIDTH               = 10;
parameter AMP_WIDTH                 = 8;
// cali_memory
parameter CALI_MEMORY_NUM_ENTRY     = 16;
parameter CALI_MEMORY_ADDR_WIDTH    = 4;
parameter CALI_MEMORY_DATA_WIDTH    = 36;

/* NCO */
parameter NCO_N                     = 22;
parameter Z_CORR_WIDTH              = 12;
parameter SIN_LUT_NUM_ENTRY         = 1024;

/* Calibration */
parameter IQ_CALI_WIDTH             = 9;


localparam ENVE_MEMORY_DATA_WIDTH = PHASE_WIDTH + AMP_WIDTH;
localparam PC_WIDTH = INST_LIST_ADDR_WIDTH;

/* NCO */
// NCO
localparam NUM_NCO = NUM_QUBIT;
localparam NCO_ADDR_WIDTH = QUBIT_ADDR_WIDTH;
localparam NCO_OUTPUT_WIDTH = PHASE_WIDTH;
localparam NCO_Z_CORR_WIDTH = Z_CORR_WIDTH;

// sin/cos lut
localparam SIN_LUT_ADDR_WIDTH = PHASE_WIDTH;
localparam SIN_LUT_DATA_WIDTH = AMP_WIDTH;
localparam POLAR_MOD_WIDTH = IQ_CALI_WIDTH;
//

localparam NUM_ITER_INIT = 40960;
localparam NUM_ITER_INST_0 = 1024;
localparam NUM_ITER_INST_1 = 2048;

localparam NCO_OFFSET = 0;

reg                                     clk; 
reg                                     rst;
reg     [PC_WIDTH-1:0]                  PC;
reg                                     valid_PC_in;

/* Instruction decode */
reg                                     valid_addr_in;
reg                                     set_enve_memory_addr;
reg                                     increment_enve_memory_addr;

reg                                     inst_list_wr_en;
reg     [INST_LIST_ADDR_WIDTH-1:0]      inst_list_wr_addr;
reg     [INST_LIST_DATA_WIDTH-1:0]      inst_list_wr_data;

reg     [NUM_QUBIT-1:0]                 inst_table_wr_sel;
reg                                     inst_table_wr_en;
reg     [INST_TABLE_ADDR_WIDTH-1:0]     inst_table_wr_addr;
reg     [INST_TABLE_DATA_WIDTH-1:0]     inst_table_wr_data;

reg                                     enve_memory_wr_en;
reg     [ENVE_MEMORY_ADDR_WIDTH-1:0]    enve_memory_wr_addr;
reg     [ENVE_MEMORY_DATA_WIDTH-1:0]    enve_memory_wr_data;

reg                                     cali_memory_wr_en;
reg     [CALI_MEMORY_ADDR_WIDTH-1:0]    cali_memory_wr_addr;
reg     [CALI_MEMORY_DATA_WIDTH-1:0]    cali_memory_wr_data;

wire    [QUBIT_ADDR_WIDTH-1:0]          qubit_sel_out;
wire                                    valid_inst_table_out;
wire                                    is_read_env_fin;
wire                                    valid_z_corr_out;
wire                                    is_rz_fin_out;

/* NCO */
reg     [NUM_NCO-1:0]                   nco_ftw_wr_en;
reg     [NUM_NCO*NCO_N-1:0]             nco_ftw_in;
reg     [NUM_NCO-1:0]                   nco_z_corr_wr_en;
reg     [NUM_NCO*NCO_Z_CORR_WIDTH-1:0]  nco_z_corr_in;
reg     [NUM_NCO-1:0]                   nco_phase_wr_en;
reg     [NUM_NCO-1:0]                   nco_z_corr_mode;

/* IQ Result */
wire                                    valid_out;
wire    [IQ_OUT_WIDTH-1:0]              i_out;
wire    [IQ_OUT_WIDTH-1:0]              q_out;

///

reg [INST_LIST_DATA_WIDTH-1:0]          inst_list_mem [0:INST_LIST_NUM_ENTRY-1];
reg [INST_TABLE_DATA_WIDTH-1:0]         inst_table_mem [0:INST_TABLE_NUM_ENTRY * NUM_QUBIT-1];
reg [PHASE_WIDTH-1:0]                   phase_mem [0:ENVE_MEMORY_NUM_ENTRY-1];
reg [AMP_WIDTH-1:0]                     amp_mem [0:ENVE_MEMORY_NUM_ENTRY-1];
reg [CALI_MEMORY_DATA_WIDTH-1:0]        cali_mem [0:CALI_MEMORY_NUM_ENTRY-1];

drive_signal_gen_unit #(
    .NUM_QUBIT(NUM_QUBIT),
    .QUBIT_ADDR_WIDTH(QUBIT_ADDR_WIDTH),
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
    .IQ_CALI_WIDTH(IQ_CALI_WIDTH)
) UUT (
    .clk(clk),
    .rst(rst),
    .PC(PC),
    .valid_PC_in(valid_PC_in),

    .valid_addr_in(valid_addr_in),
    .set_enve_memory_addr(set_enve_memory_addr),
    .increment_enve_memory_addr(increment_enve_memory_addr),

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

    .qubit_sel_out(qubit_sel_out),
    .valid_inst_table_out(valid_inst_table_out),
    .is_read_env_fin(is_read_env_fin),
    .valid_z_corr_out(valid_z_corr_out),
    .is_rz_fin_out(is_rz_fin_out),

    .nco_ftw_wr_en(nco_ftw_wr_en),
    .nco_ftw_in(nco_ftw_in),
    .nco_z_corr_wr_en(nco_z_corr_wr_en),
    .nco_z_corr_in(nco_z_corr_in),
    .nco_phase_wr_en(nco_phase_wr_en),
    .nco_z_corr_mode(nco_z_corr_mode),

    .valid_out(valid_out),
    .i_out(i_out),
    .q_out(q_out)
);

integer I;

always #10 clk = ~clk;

initial begin
    $dumpfile("drive_signal_gen_unit.vcd");
    $dumpvars(0, drive_signal_gen_unit_tb);

    clk = 1'b0;
    rst = 1'b0;
    
    // Manually reset control signals
    inst_list_wr_en = 0;
    inst_list_wr_addr = 0;
    inst_list_wr_data = 0;

    inst_table_wr_sel = 0;
    inst_table_wr_en = 0;
    inst_table_wr_addr = 0;
    inst_table_wr_data = 0;

    enve_memory_wr_en = 0;
    enve_memory_wr_addr = 0;
    enve_memory_wr_data = 0;

    cali_memory_wr_en = 0;
    cali_memory_wr_addr = 0;
    cali_memory_wr_data = 0;

    nco_ftw_wr_en = 0;
    // nco_ftw_in = 0;
    nco_z_corr_wr_en = 0;
    nco_z_corr_in = 0;
    nco_phase_wr_en = 0;
    nco_z_corr_mode = 0;

    valid_PC_in = 1'b0;
    PC = 0;
    valid_addr_in = 1'b0;
    set_enve_memory_addr = 1'b0;
    increment_enve_memory_addr = 1'b0;

    #5;
    rst = 1;
    #10;
    rst = 0;
    #5;
    
    // initialize memory
    inst_table_wr_sel = {{(NUM_QUBIT-1){1'b0}}, 1'b1};
    for (I=0; I< NUM_ITER_INIT; I=I+1)
    begin
        // inst_list
        if (I < INST_LIST_NUM_ENTRY) begin
            inst_list_wr_en = 1'b1;
            inst_list_wr_addr = I[INST_LIST_ADDR_WIDTH-1:0];
            inst_list_wr_data = inst_list_mem[inst_list_wr_addr];
        end
        else begin
            inst_list_wr_en = 1'b0;
            inst_list_wr_addr = 0;
            inst_list_wr_data = 0;
        end

        // inst_table
        if (I < INST_TABLE_NUM_ENTRY * NUM_QUBIT) begin
            inst_table_wr_en = 1'b1;
            if ((I > 0) && (I[0 +: INST_TABLE_ADDR_WIDTH] == 0)) begin
                inst_table_wr_sel = inst_table_wr_sel << 1;
            end
            inst_table_wr_addr = I[0 +: INST_TABLE_ADDR_WIDTH];
            inst_table_wr_data = inst_table_mem[I[0 +: (INST_TABLE_ADDR_WIDTH+QUBIT_ADDR_WIDTH)]];
            // $display("### I: %h", I);
            // $display("inst_table_wr_en: %h", inst_table_wr_en);
            // $display("inst_table_wr_sel: %h", inst_table_wr_sel);
            // $display("inst_table_wr_addr: %h", inst_table_wr_addr);
            // $display("inst_table_wr_data: %h", inst_table_wr_data);
        end
        else begin
            inst_table_wr_en = 1'b0;
            inst_table_wr_sel = 0;
            inst_table_wr_addr = 0;
            inst_table_wr_data = 0;
        end

        // enve_memory
        if (I < ENVE_MEMORY_NUM_ENTRY) begin
            enve_memory_wr_en = 1'b1;
            enve_memory_wr_addr = I[ENVE_MEMORY_ADDR_WIDTH-1:0];
            enve_memory_wr_data = {phase_mem[enve_memory_wr_addr]
                                , amp_mem[enve_memory_wr_addr]};
        end
        else begin
            enve_memory_wr_en = 1'b0;
            enve_memory_wr_addr = 0;
            enve_memory_wr_data = 0;
        end

        // cali_memory
        if (I < CALI_MEMORY_NUM_ENTRY) begin
            cali_memory_wr_en = 1'b1;
            cali_memory_wr_addr = I[CALI_MEMORY_ADDR_WIDTH-1:0];
            cali_memory_wr_data = cali_mem[enve_memory_wr_addr];
        end
        else begin
            cali_memory_wr_en = 1'b0;
            cali_memory_wr_addr = 0;
            cali_memory_wr_data = 0;
        end

        #20;
    end

    inst_list_wr_en = 0;
    inst_list_wr_addr = 0;
    inst_list_wr_data = 0;

    inst_table_wr_sel = 0;
    inst_table_wr_en = 0;
    inst_table_wr_addr = 0;
    inst_table_wr_data = 0;

    enve_memory_wr_en = 0;
    enve_memory_wr_addr = 0;
    enve_memory_wr_data = 0;

    cali_memory_wr_en = 0;
    cali_memory_wr_addr = 0;
    cali_memory_wr_data = 0;

    // initialize nco
    nco_ftw_wr_en = {NUM_NCO{1'b1}};
    nco_z_corr_wr_en = {NUM_NCO{1'b1}};
    nco_z_corr_in = {(NUM_NCO*Z_CORR_WIDTH){1'b0}};
    #20;

    nco_ftw_wr_en = 0;
    nco_z_corr_wr_en = 0;
    nco_z_corr_in = 0;
    #20;

    /* inst #1 */
    // inst_list:   qubit=q14, inst=inst0
    // inst_table:  start_addr=0, stop_addr=1023, axis=X
    // enve_memory: gaussian(0~1023)
    // cali_memory: no correction (b_i=0, b_q=0)

    // Emulate control_signal_gen_unit
    valid_PC_in = 1'b1;
    PC = 0;
    // Emulate control_z_corr_unit
    nco_z_corr_wr_en = {NUM_NCO{1'b1}};
    nco_phase_wr_en = {NUM_NCO{1'b0}};
    nco_z_corr_mode = {NUM_NCO{1'b1}};
    // Emulate control_enve_memory_unit
    valid_addr_in = 1'b0;
    set_enve_memory_addr = 1'b0;
    increment_enve_memory_addr = 1'b0;

    // Wait instruction fetching (inst_list, inst_table)
    #20;
    valid_PC_in = 1'b0;
    #20;
    // Check result
    if (valid_inst_table_out == 1'b1) begin
        $display("PASS: valid_inst_table_out == %d, ANS == 1", valid_inst_table_out);
    end
    else begin
        $display("FAIL: valid_inst_table_out == %d, ANS == 1", valid_inst_table_out);
    end

    // Emulate control_z_corr_unit
    nco_z_corr_wr_en = {NUM_NCO{1'b1}};
    nco_phase_wr_en = {NUM_NCO{1'b1}};
    nco_z_corr_mode[qubit_sel_out] = 1'b0;
    // Emulate control_enve_memory_unit
    valid_addr_in = 1'b1;
    set_enve_memory_addr = 1'b1;
    increment_enve_memory_addr = 1'b0;
    #20;
    // Emulate control_enve_memory_unit
    valid_addr_in = 1'b1;
    set_enve_memory_addr = 1'b0;
    increment_enve_memory_addr = 1'b1;

    // Wait signal generation
    for (I=0; I<NUM_ITER_INST_0; I=I+1) begin
        #20;
        if (is_read_env_fin == 1'b1) begin
            if (I < 10) $display("is_read_env_fin == %d at I == %d", is_read_env_fin, I);
            if (I > NUM_ITER_INST_0-10) $display("is_read_env_fin == %d at I == %d", is_read_env_fin, I);
        end
    end

    // Check result
    if (is_read_env_fin == 1'b1) begin
        $display("PASS: is_read_env_fin == %d, ANS == 1", is_read_env_fin);
    end
    else begin
        $display("FAIL: is_read_env_fin == %d, ANS == 1", is_read_env_fin);
    end

    // Emulate control_z_corr_unit
    nco_z_corr_wr_en = {NUM_NCO{1'b1}};
    nco_phase_wr_en = {NUM_NCO{1'b0}};
    nco_z_corr_mode = {NUM_NCO{1'b1}};
    // Emulate control_enve_memory_unit
    valid_addr_in = 1'b0;
    set_enve_memory_addr = 1'b0;
    increment_enve_memory_addr = 1'b0;
    #20;

    /* inst #2 */
    // inst_list:   qubit=q3, inst=inst2
    // inst_table:  start_addr=1024, stop_addr=3071, axis=X
    // enve_memory: gaussian(1024~3071)
    // cali_memory: no correction (b_i=0, b_q=0)
    
    // Emulate control_signal_gen_unit
    valid_PC_in = 1'b1;
    PC = 1;
    // Emulate control_z_corr_unit
    nco_z_corr_wr_en = {NUM_NCO{1'b1}};
    nco_phase_wr_en = {NUM_NCO{1'b0}};
    nco_z_corr_mode = {NUM_NCO{1'b1}};
    // Emulate control_enve_memory_unit
    valid_addr_in = 1'b0;
    set_enve_memory_addr = 1'b0;
    increment_enve_memory_addr = 1'b0;

    // Wait instruction fetching (inst_list, inst_table)
    #20;
    valid_PC_in = 1'b0;
    #20;
    // Check result
    if (valid_inst_table_out == 1'b1) begin
        $display("PASS: valid_inst_table_out == %d, ANS == 1", valid_inst_table_out);
    end
    else begin
        $display("FAIL: valid_inst_table_out == %d, ANS == 1", valid_inst_table_out);
    end

    // Emulate control_z_corr_unit
    nco_z_corr_wr_en = {NUM_NCO{1'b1}};
    nco_phase_wr_en = {NUM_NCO{1'b1}};
    nco_z_corr_mode[qubit_sel_out] = 1'b0;
    // Emulate control_enve_memory_unit
    valid_addr_in = 1'b1;
    set_enve_memory_addr = 1'b1;
    increment_enve_memory_addr = 1'b0;
    #20;
    // Emulate control_enve_memory_unit
    valid_addr_in = 1'b1;
    set_enve_memory_addr = 1'b0;
    increment_enve_memory_addr = 1'b1;

    // Wait signal generation
    for (I=0; I<NUM_ITER_INST_1; I=I+1) begin
        #20;
        if (is_read_env_fin == 1'b1) begin
            if (I < 10) $display("is_read_env_fin == %d at I == %d", is_read_env_fin, I);
            if (I > NUM_ITER_INST_1-10) $display("is_read_env_fin == %d at I == %d", is_read_env_fin, I);
        end
    end

    // Check result
    if (is_read_env_fin == 1'b1) begin
        $display("PASS: is_read_env_fin == %d, ANS == 1", is_read_env_fin);
    end
    else begin
        $display("FAIL: is_read_env_fin == %d, ANS == 1", is_read_env_fin);
    end

    // Emulate control_z_corr_unit
    nco_z_corr_wr_en = {NUM_NCO{1'b1}};
    nco_phase_wr_en = {NUM_NCO{1'b0}};
    nco_z_corr_mode = {NUM_NCO{1'b1}};
    // Emulate control_enve_memory_unit
    valid_addr_in = 1'b0;
    set_enve_memory_addr = 1'b0;
    increment_enve_memory_addr = 1'b0;
    #20;

    /* inst #3 */
    // inst_list:   qubit=q5, rz_mode=1, phase_imm=0xfed

    // Emulate control_signal_gen_unit
    valid_PC_in = 1'b1;
    PC = 2;
    // Emulate control_z_corr_unit
    nco_z_corr_wr_en = {NUM_NCO{1'b0}};
    nco_phase_wr_en = {NUM_NCO{1'b0}};
    nco_z_corr_mode = {NUM_NCO{1'b0}};

    // Wait instruction fetching (inst_list, inst_table)
    #20;
    valid_PC_in = 1'b0;
    #20;
    if (valid_z_corr_out) begin
        nco_z_corr_mode[qubit_sel_out] = 1'b1;
    end
    #20;
    // Check result
    if (is_rz_fin_out == 1'b1) begin
        $display("PASS: is_rz_fin_out == %d, ANS == 1", is_rz_fin_out);
    end
    else begin
        $display("FAIL: is_rz_fin_out == %d, ANS == 1", is_rz_fin_out);
    end
    
    #20;
    $finish;
end

// 00_0000_0000_0001_0000_0000
// 00_0000_0000_0010_0000_0000
// 00_0000_0000_0011_0000_0000
// 00_0000_0000_0100_0000_0000
// 00_0000_0000_0101_0000_0000
// 00_0000_0000_0110_0000_0000
// 00_0000_0000_0111_0000_0000
// 00_0000_0000_1000_0000_0000
// 00_0000_0000_1001_0000_0000
// 00_0000_0000_1010_0000_0000
// 00_0000_0000_1011_0000_0000
// 00_0000_0000_1100_0000_0000
// 00_0000_0000_1101_0000_0000
// 00_0000_0000_1110_0000_0000
// 00_0000_0000_1111_0000_0000
genvar J;
generate
    for(J = 0; J < NUM_NCO; J = J +1) begin: genblk_nco_ftw_in
        initial begin
            nco_ftw_in[J*NCO_N +: NCO_N] = {
                {(NCO_OUTPUT_WIDTH-NCO_ADDR_WIDTH+NCO_OFFSET){1'b0}},
                J[NCO_ADDR_WIDTH-1:0],
                {(NCO_N-NCO_OUTPUT_WIDTH-NCO_OFFSET){1'b0}}
            };
        end
    end
endgenerate

// memory initialization
initial begin
    // inst_list
    $readmemh("inst_list_n2048_17b.mem", inst_list_mem, 0, INST_LIST_NUM_ENTRY-1);
    // inst_table
    $readmemh("inst_table_n128_34b.mem", inst_table_mem, 0, INST_TABLE_NUM_ENTRY*NUM_QUBIT-1);
    // enve_memory
    $readmemh("phase_memory_n40960_10b.mem", phase_mem, 0, ENVE_MEMORY_NUM_ENTRY-1);
    $readmemh("amp_memory_n40960_8b.mem", amp_mem, 0, ENVE_MEMORY_NUM_ENTRY-1);
    // cali_memory
    $readmemh("cali_memory_n16_36b.mem", cali_mem, 0, CALI_MEMORY_NUM_ENTRY-1);
end

endmodule

/* Expected result */
/*
*/