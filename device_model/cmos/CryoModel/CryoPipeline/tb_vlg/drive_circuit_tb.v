`timescale 1ns/100ps

`include "define_drive_circuit.v"

module drive_circuit_tb();

reg                                             clk;
reg                                             rst;
reg                                             trigger;
reg   [`DRIVE_NUM_BANK-1:0]                     bank_wr_sel;
reg                                             inst_list_wr_en;
reg   [`DRIVE_INST_LIST_ADDR_WIDTH-1:0]         inst_list_wr_addr;
reg   [`DRIVE_INST_LIST_DATA_WIDTH-1:0]         inst_list_wr_data;
reg   [`DRIVE_NUM_QUBIT_PER_BANK-1:0]           inst_table_wr_sel;
reg                                             inst_table_wr_en;
reg   [`DRIVE_INST_TABLE_ADDR_WIDTH-1:0]        inst_table_wr_addr;
reg   [`DRIVE_INST_TABLE_DATA_WIDTH-1:0]        inst_table_wr_data;
reg                                             enve_memory_wr_en;
reg   [`DRIVE_ENVE_MEMORY_ADDR_WIDTH-1:0]       enve_memory_wr_addr;
reg   [`DRIVE_ENVE_MEMORY_DATA_WIDTH-1:0]       enve_memory_wr_data;
reg                                             cali_memory_wr_en;
reg   [`DRIVE_CALI_MEMORY_ADDR_WIDTH-1:0]       cali_memory_wr_addr;
reg   [`DRIVE_CALI_MEMORY_DATA_WIDTH-1:0]       cali_memory_wr_data;
reg   [`DRIVE_NUM_NCO-1:0]                      nco_ftw_wr_en;
reg   [`DRIVE_NUM_NCO*`DRIVE_NCO_N-1:0]         nco_ftw_in;
reg                                             z_corr_memory_wr_en;
reg   [`DRIVE_Z_CORR_MEMORY_ADDR_WIDTH-1:0]     z_corr_memory_wr_addr;
reg   [`DRIVE_Z_CORR_MEMORY_DATA_WIDTH-1:0]     z_corr_memory_wr_data;
reg                                             sin_lut_wr_en;
reg                                             cos_lut_wr_en;
reg   [`DRIVE_SIN_LUT_ADDR_WIDTH-1:0]           sinusoidal_lut_wr_addr; 
reg   [`DRIVE_SIN_LUT_DATA_WIDTH-1:0]           sinusoidal_lut_wr_data;

wire                                            valid_out;
wire  [`DRIVE_IQ_SUM_WIDTH-1:0]                 i_out;
wire  [`DRIVE_IQ_SUM_WIDTH-1:0]                 q_out;

//
// TODO
localparam NUM_ITER_INIT = 40960;
localparam NUM_ITER_INST_0 = 1024;
localparam NUM_ITER_INST_1 = 2048;
localparam NCO_OFFSET = 0;

reg [`DRIVE_INST_LIST_DATA_WIDTH-1:0]          inst_list_mem_0 [0:`DRIVE_INST_LIST_NUM_ENTRY-1];
reg [`DRIVE_INST_TABLE_DATA_WIDTH-1:0]         inst_table_mem_0 [0:`DRIVE_INST_TABLE_NUM_ENTRY*`DRIVE_NUM_QUBIT_PER_BANK-1];
reg [`DRIVE_PHASE_WIDTH-1:0]                   phase_mem_0 [0:`DRIVE_ENVE_MEMORY_NUM_ENTRY-1];
reg [`DRIVE_AMP_WIDTH-1:0]                     amp_mem_0 [0:`DRIVE_ENVE_MEMORY_NUM_ENTRY-1];
reg [`DRIVE_CALI_MEMORY_DATA_WIDTH-1:0]        cali_mem_0 [0:`DRIVE_CALI_MEMORY_NUM_ENTRY-1];
reg [`DRIVE_Z_CORR_MEMORY_DATA_WIDTH-1:0]      z_corr_mem_0 [0:`DRIVE_Z_CORR_MEMORY_NUM_ENTRY-1];

reg [`DRIVE_INST_LIST_DATA_WIDTH-1:0]          inst_list_mem_1 [0:`DRIVE_INST_LIST_NUM_ENTRY-1];
reg [`DRIVE_INST_TABLE_DATA_WIDTH-1:0]         inst_table_mem_1 [0:`DRIVE_INST_TABLE_NUM_ENTRY*`DRIVE_NUM_QUBIT_PER_BANK-1];
reg [`DRIVE_PHASE_WIDTH-1:0]                   phase_mem_1 [0:`DRIVE_ENVE_MEMORY_NUM_ENTRY-1];
reg [`DRIVE_AMP_WIDTH-1:0]                     amp_mem_1 [0:`DRIVE_ENVE_MEMORY_NUM_ENTRY-1];
reg [`DRIVE_CALI_MEMORY_DATA_WIDTH-1:0]        cali_mem_1 [0:`DRIVE_CALI_MEMORY_NUM_ENTRY-1];
reg [`DRIVE_Z_CORR_MEMORY_DATA_WIDTH-1:0]      z_corr_mem_1 [0:`DRIVE_Z_CORR_MEMORY_NUM_ENTRY-1];

reg [`DRIVE_SIN_LUT_DATA_WIDTH-1:0]            sin_mem [0:`DRIVE_SIN_LUT_NUM_ENTRY-1];
reg [`DRIVE_SIN_LUT_DATA_WIDTH-1:0]            cos_mem [0:`DRIVE_SIN_LUT_NUM_ENTRY-1];

drive_circuit UUT (
    .clk(clk),
    .rst(rst),
    .trigger(trigger),

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

integer I, J;

always #10 clk = ~clk;

initial begin
    $dumpfile("drive_circuit.vcd");
    $dumpvars(0, drive_circuit_tb);

    /* Initialization start */
    clk = 1'b0;
    rst = 1'b0;
    trigger = 1'b0;
    
    // 
    bank_wr_sel = 0;

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

    z_corr_memory_wr_en = 0;
    z_corr_memory_wr_addr = 0;
    z_corr_memory_wr_data = 0;

    nco_ftw_wr_en = 0;

    sin_lut_wr_en = 0;
    cos_lut_wr_en = 0;
    sinusoidal_lut_wr_addr = 0;
    sinusoidal_lut_wr_data = 0;

    #5;
    rst = 1;
    #10;
    rst = 0;
    #5;
    
    // initialize memory
    for (J=0; J< `DRIVE_NUM_BANK; J=J+1) begin
        if (`DRIVE_NUM_BANK == 1) begin
            bank_wr_sel = 1'b1;
        end
        else begin
            if (J == 0)         bank_wr_sel = 2'b01;
            else if (J == 1)    bank_wr_sel = 2'b10;
            else                bank_wr_sel = 2'b00;
        end
        
        inst_table_wr_sel = {{(`DRIVE_NUM_QUBIT_PER_BANK-1){1'b0}}, 1'b1};
        for (I=0; I< NUM_ITER_INIT; I=I+1) begin
            // inst_list
            if (I < `DRIVE_INST_LIST_NUM_ENTRY) begin
                inst_list_wr_en = 1'b1;
                inst_list_wr_addr = I[`DRIVE_INST_LIST_ADDR_WIDTH-1:0];
                
                if (J == 0)         inst_list_wr_data = inst_list_mem_0[inst_list_wr_addr];
                else if (J == 1)    inst_list_wr_data = inst_list_mem_1[inst_list_wr_addr];
                else                inst_list_wr_data = 0;
            end
            else begin
                inst_list_wr_en = 1'b0;
                inst_list_wr_addr = 0;
                inst_list_wr_data = 0;
            end

            // inst_table
            if (I < `DRIVE_INST_TABLE_NUM_ENTRY * `DRIVE_NUM_QUBIT_PER_BANK) begin
                inst_table_wr_en = 1'b1;
                if ((I > 0) && (I[0 +: `DRIVE_INST_TABLE_ADDR_WIDTH] == 0)) begin
                    inst_table_wr_sel = inst_table_wr_sel << 1;
                end
                inst_table_wr_addr = I[0 +: `DRIVE_INST_TABLE_ADDR_WIDTH];
                
                if (J == 0)         inst_table_wr_data = inst_table_mem_0[I[0 +: (`DRIVE_INST_TABLE_ADDR_WIDTH+`DRIVE_QUBIT_ADDR_WIDTH_PER_BANK)]];
                else if (J == 1)    inst_table_wr_data = inst_table_mem_1[I[0 +: (`DRIVE_INST_TABLE_ADDR_WIDTH+`DRIVE_QUBIT_ADDR_WIDTH_PER_BANK)]];
                else                inst_table_wr_data = 0;
                
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
            if (I < `DRIVE_ENVE_MEMORY_NUM_ENTRY) begin
                enve_memory_wr_en = 1'b1;
                enve_memory_wr_addr = I[`DRIVE_ENVE_MEMORY_ADDR_WIDTH-1:0];
                if (J == 0)         enve_memory_wr_data = {phase_mem_0[enve_memory_wr_addr], amp_mem_0[enve_memory_wr_addr]};
                else if (J == 1)    enve_memory_wr_data = {phase_mem_1[enve_memory_wr_addr], amp_mem_1[enve_memory_wr_addr]};
                else                enve_memory_wr_data = 0;
            end
            else begin
                enve_memory_wr_en = 1'b0;
                enve_memory_wr_addr = 0;
                enve_memory_wr_data = 0;
            end

            // cali_memory
            if (I < `DRIVE_CALI_MEMORY_NUM_ENTRY) begin
                cali_memory_wr_en = 1'b1;
                cali_memory_wr_addr = I[`DRIVE_CALI_MEMORY_ADDR_WIDTH-1:0];
                if (J == 0)         cali_memory_wr_data = cali_mem_0[cali_memory_wr_addr];
                else if (J == 1)    cali_memory_wr_data = cali_mem_1[cali_memory_wr_addr];
                else                cali_memory_wr_data = 0;
            end
            else begin
                cali_memory_wr_en = 1'b0;
                cali_memory_wr_addr = 0;
                cali_memory_wr_data = 0;
            end

            // z_corr_memory
            if (I < `DRIVE_Z_CORR_MEMORY_NUM_ENTRY) begin
                z_corr_memory_wr_en = 1'b1;
                z_corr_memory_wr_addr = I[`DRIVE_Z_CORR_MEMORY_ADDR_WIDTH-1:0];
                if (J == 0)         z_corr_memory_wr_data = z_corr_mem_0[z_corr_memory_wr_addr];
                else if (J == 1)    z_corr_memory_wr_data = z_corr_mem_1[z_corr_memory_wr_addr];
                else                z_corr_memory_wr_data = 0;
            end
            else begin
                z_corr_memory_wr_en = 1'b0;
                z_corr_memory_wr_addr = 0;
                z_corr_memory_wr_data = 0;
            end
            #20;
        end
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

    z_corr_memory_wr_en = 1'b0;
    z_corr_memory_wr_addr = 0;
    z_corr_memory_wr_data = 0;

    // initialize nco
    for (J=0; J< `DRIVE_NUM_BANK; J=J+1) begin
        if (`DRIVE_NUM_BANK == 1) begin
            bank_wr_sel = 1'b1;
        end
        else begin
            if (J == 0)         bank_wr_sel = 2'b01;
            else if (J == 1)    bank_wr_sel = 2'b10;
            else                bank_wr_sel = 2'b00;
        end
        nco_ftw_wr_en = {`DRIVE_NUM_NCO{1'b1}};
        #20;
    end
    nco_ftw_wr_en = 0;
    #20;

    // initialize sinusoidal luts
    sin_lut_wr_en = 0;
    cos_lut_wr_en = 0;
    sinusoidal_lut_wr_addr = 0;
    sinusoidal_lut_wr_data = 0;

    for (J=0; J< 2; J=J+1) begin // sin/cos
        for (I=0; I< `DRIVE_SIN_LUT_NUM_ENTRY; I=I+1) begin
            if (J == 0) sin_lut_wr_en = 1'b1;
            else sin_lut_wr_en = 1'b0;

            if (J == 0) cos_lut_wr_en = 1'b0;
            else cos_lut_wr_en = 1'b1;
            
            sinusoidal_lut_wr_addr = I[`DRIVE_SIN_LUT_ADDR_WIDTH-1:0];            
            if (J == 0) sinusoidal_lut_wr_data = sin_mem[sinusoidal_lut_wr_addr];
            else sinusoidal_lut_wr_data = cos_mem[sinusoidal_lut_wr_addr];

            #20;
        end
    end
    sin_lut_wr_en = 0;
    cos_lut_wr_en = 0;
    sinusoidal_lut_wr_addr = 0;
    sinusoidal_lut_wr_data = 0;
    #20;

    /* Initialization finish */
    
    // inst_list:   qubit=q14, inst=inst0
    // inst_table:  start_addr=0, stop_addr=1023, axis=X
    // enve_memory: gaussian(0~1023)
    // cali_memory: no correction (b_i=0, b_q=0)
    trigger = 1'b1;

    #20;
    trigger = 1'b0;
    // update_PC == 1;
    #20;
    // drive_signal_gen_unit.is_next_inst_in == 1;
    #20;
    // drive_signal_gen_unit.is_next_inst_in == 0;
    #20;
    // drive_signal_gen_unit.is_next_addr_out == 1;
    // if (is_next_addr_out == 1'b1) begin
    //     $display("PASS: is_next_addr_out == %d, ANS == 1", is_next_addr_out);
    // end
    // else begin
    //     $display("FAIL: is_next_addr_out == %d, ANS == 1", is_next_addr_out);
    // end
    #20;
    // nco_z_corr_wr_en == {`DRIVE_NUM_QUBIT_PER_BANK{1'b1}};
    // nco_phase_wr_en == {`DRIVE_NUM_QUBIT_PER_BANK{1'b1}};
    // nco_z_corr_mode[qubit_sel] == 1'b0;
    #20;
    // nco_z_corr_wr_en == {`DRIVE_NUM_QUBIT_PER_BANK{1'b1}};
    // nco_phase_wr_en == {`DRIVE_NUM_QUBIT_PER_BANK{1'b1}};
    // nco_z_corr_mode[qubit_sel] == 1'b0;

    // Wait signal generation
    for (I=0; I<NUM_ITER_INST_0; I=I+1) begin
        #20;
        // if (is_read_env_fin == 1'b1) begin
        //     if (I < 10) $display("is_read_env_fin == %d at I == %d", is_read_env_fin, I);
        //     if (I > NUM_ITER_INST_0-10) $display("is_read_env_fin == %d at I == %d", is_read_env_fin, I);
        // end
    end
    // is_read_env_fin == 1;
    #20;
    // nco_z_corr_wr_en <= {`DRIVE_NUM_QUBIT_PER_BANK{1'b1}};
    // nco_phase_wr_en <= {`DRIVE_NUM_QUBIT_PER_BANK{1'b0}};
    // nco_z_corr_mode <= {`DRIVE_NUM_QUBIT_PER_BANK{1'b1}};

    #20;

    #200;
    for (I=0; I<NUM_ITER_INST_1; I=I+1) begin
        #20;
        // if (is_read_env_fin == 1'b1) begin
        //     if (I < 10) $display("is_read_env_fin == %d at I == %d", is_read_env_fin, I);
        //     if (I > NUM_ITER_INST_1-10) $display("is_read_env_fin == %d at I == %d", is_read_env_fin, I);
        // end
    end
    for (I=0; I<NUM_ITER_INST_1; I=I+1) begin
        #20;
        // if (is_read_env_fin == 1'b1) begin
        //     if (I < 10) $display("is_read_env_fin == %d at I == %d", is_read_env_fin, I);
        //     if (I > NUM_ITER_INST_1-10) $display("is_read_env_fin == %d at I == %d", is_read_env_fin, I);
        // end
    end
    for (I=0; I<NUM_ITER_INST_1; I=I+1) begin
        #20;
        // if (is_read_env_fin == 1'b1) begin
        //     if (I < 10) $display("is_read_env_fin == %d at I == %d", is_read_env_fin, I);
        //     if (I > NUM_ITER_INST_1-10) $display("is_read_env_fin == %d at I == %d", is_read_env_fin, I);
        // end
    end

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
genvar K;
generate
    for(K = 0; K < `DRIVE_NUM_NCO; K = K +1) begin: genblk_nco_ftw_in
        initial begin
            nco_ftw_in[K*`DRIVE_NCO_N +: `DRIVE_NCO_N] = {
                {(`DRIVE_NCO_OUTPUT_WIDTH-`DRIVE_NCO_ADDR_WIDTH+NCO_OFFSET){1'b0}},
                K[`DRIVE_NCO_ADDR_WIDTH-1:0],
                {(`DRIVE_NCO_N-`DRIVE_NCO_OUTPUT_WIDTH-NCO_OFFSET){1'b0}}
            };
        end
    end
endgenerate

// memory initialization
initial begin
    if (`DRIVE_NUM_BANK == 1) begin
        // Bank 0
        // inst_list
        $readmemh("inst_list_n2048_17b_0.mem", inst_list_mem_0, 0, `DRIVE_INST_LIST_NUM_ENTRY-1);
        // inst_table
        $readmemh("inst_table_n128_34b_0.mem", inst_table_mem_0, 0, `DRIVE_INST_TABLE_NUM_ENTRY*`DRIVE_NUM_QUBIT_PER_BANK-1);
        // enve_memory
        $readmemh("phase_memory_n40960_10b_0.mem", phase_mem_0, 0, `DRIVE_ENVE_MEMORY_NUM_ENTRY-1);
        $readmemh("amp_memory_n40960_8b_0.mem", amp_mem_0, 0, `DRIVE_ENVE_MEMORY_NUM_ENTRY-1);
        // cali_memory
        $readmemh("cali_memory_n16_36b_0.mem", cali_mem_0, 0, `DRIVE_CALI_MEMORY_NUM_ENTRY-1);
        // z_corr_memory
        $readmemh("z_corr_memory_n16_192b_0.mem", z_corr_mem_0, 0, `DRIVE_Z_CORR_MEMORY_NUM_ENTRY-1);
    end
    else begin // `DRIVE_NUM_BANK == 2
        // Bank 0
        // inst_list
        $readmemh("inst_list_n2048_17b_0.mem", inst_list_mem_0, 0, `DRIVE_INST_LIST_NUM_ENTRY-1);
        // inst_table
        $readmemh("inst_table_n128_34b_0.mem", inst_table_mem_0, 0, `DRIVE_INST_TABLE_NUM_ENTRY*`DRIVE_NUM_QUBIT_PER_BANK-1);
        // enve_memory
        $readmemh("phase_memory_n40960_10b_0.mem", phase_mem_0, 0, `DRIVE_ENVE_MEMORY_NUM_ENTRY-1);
        $readmemh("amp_memory_n40960_8b_0.mem", amp_mem_0, 0, `DRIVE_ENVE_MEMORY_NUM_ENTRY-1);
        // cali_memory
        $readmemh("cali_memory_n16_36b_0.mem", cali_mem_0, 0, `DRIVE_CALI_MEMORY_NUM_ENTRY-1);
        // z_corr_memory
        $readmemh("z_corr_memory_n16_384b_0.mem", z_corr_mem_0, 0, `DRIVE_Z_CORR_MEMORY_NUM_ENTRY-1);

        // Bank 1
        // inst_list
        $readmemh("inst_list_n2048_17b_1.mem", inst_list_mem_1, 0, `DRIVE_INST_LIST_NUM_ENTRY-1);
        // inst_table
        $readmemh("inst_table_n128_34b_1.mem", inst_table_mem_1, 0, `DRIVE_INST_TABLE_NUM_ENTRY*`DRIVE_NUM_QUBIT_PER_BANK-1);
        // enve_memory
        $readmemh("phase_memory_n40960_10b_1.mem", phase_mem_1, 0, `DRIVE_ENVE_MEMORY_NUM_ENTRY-1);
        $readmemh("amp_memory_n40960_8b_1.mem", amp_mem_1, 0, `DRIVE_ENVE_MEMORY_NUM_ENTRY-1);
        // cali_memory
        $readmemh("cali_memory_n16_36b_1.mem", cali_mem_1, 0, `DRIVE_CALI_MEMORY_NUM_ENTRY-1);
        // z_corr_memory
        $readmemh("z_corr_memory_n16_384b_1.mem", z_corr_mem_1, 0, `DRIVE_Z_CORR_MEMORY_NUM_ENTRY-1);
    end

    $readmemh("sin_n1024_8b.mem", sin_mem, 0, `DRIVE_SIN_LUT_NUM_ENTRY-1);
    $readmemh("cos_n1024_8b.mem", cos_mem, 0, `DRIVE_SIN_LUT_NUM_ENTRY-1);
end

endmodule

/* Expected result */
/*
*/