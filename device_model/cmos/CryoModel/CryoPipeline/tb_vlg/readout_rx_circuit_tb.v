`timescale 1ns/100ps

`include "define_readout_rx_circuit.v"

module readout_rx_circuit_tb();

/* Port declaration */
reg                                        clk; 
reg                                        rst;
reg        [`READRX_GLB_COUNTER_WIDTH-1:0]         glb_counter;
// inst_list
reg                                        inst_list_wr_en;
reg        [`READRX_INST_LIST_ADDR_WIDTH-1:0]      inst_list_wr_addr;
reg        [`READRX_INST_LIST_DATA_WIDTH-1:0]      inst_list_wr_data;
// nco
reg        [`READRX_QUBIT_ADDR_WIDTH-1:0]          nco_ftw_wr_sel;
reg                                        nco_ftw_wr_en;
reg        [`READRX_NCO_N-1:0]                     nco_ftw_in;
// calibration
reg                                            cali_coeff_wr_en;
reg        [`READRX_IQ_CALI_WIDTH*`READRX_NUM_CALI_COEFF-1:0]  cali_coeff_wr_data;
// sinusoidal lut
reg                                        sin_lut_wr_en;
reg                                        cos_lut_wr_en;
reg         [`READRX_SIN_LUT_ADDR_WIDTH-1:0]       sinusoidal_lut_wr_addr; 
reg         [`READRX_SIN_LUT_DATA_WIDTH-1:0]       sinusoidal_lut_wr_data;
// state_decision
reg        [`READRX_QUBIT_ADDR_WIDTH-1:0]               state_decision_coeff_wr_sel;
reg                                                     state_decision_coeff_wr_en;
reg        [`READRX_STATE_DECISION_ADDR_WIDTH-1:0]      state_decision_coeff_wr_addr; // [1,0]
reg        [`READRX_STATE_DECISION_DATA_WIDTH-1:0]      state_decision_coeff_wr_data; // [slope, y_intercept]

`ifdef READRX_STATE_DECISION_INTEL_OPT_2
    reg   [`READRX_QUBIT_ADDR_WIDTH-1:0]              threshold_memory_wr_sel;
    reg                                               threshold_memory_wr_en;
    reg   [`READRX_THRESHOLD_MEMORY_ADDR_WIDTH-1:0]   threshold_memory_wr_addr;
    reg   [`READRX_THRESHOLD_MEMORY_DATA_WIDTH-1:0]   threshold_memory_wr_data;
`endif

reg signed [`READRX_SIN_LUT_DATA_WIDTH-1:0]         slope;
reg signed [`READRX_SIN_LUT_DATA_WIDTH-1:0]         y_intercept;

// iq input
reg        [`READRX_INPUT_IQ_WIDTH-1:0]            i_in;
reg        [`READRX_INPUT_IQ_WIDTH-1:0]            q_in;
// output
wire      [`READRX_NUM_QUBIT-1:0]                 valid_meas_result;
wire      [`READRX_NUM_QUBIT-1:0]                 meas_result;

wire      [`READRX_NUM_QUBIT-1:0]                                   valid_filter_result;
wire      [`READRX_NUM_QUBIT*`READRX_SIN_LUT_DATA_WIDTH-1:0]        q_filter_result;
wire      [`READRX_NUM_QUBIT*`READRX_SIN_LUT_DATA_WIDTH-1:0]        i_filter_result;

///
// localparam NUM_ITER_INIT  = 2048;
localparam NUM_ITER_INIT  = 40;
localparam NUM_ITER_TEST1 = 256;
localparam NUM_ITER_TEST2 = 512;

// readout_rx_state_decision_unit_baseline
`ifdef READRX_STATE_DECISION_BASELINE
    localparam NUM_ITER_WAIT = 65536; // baseline
// readout_rx_state_decision_unit_google
`elsif READRX_STATE_DECISION_GOOGLE
    localparam NUM_ITER_WAIT = 64;
// readout_rx_state_decision_unit_intel_opt
`elsif READRX_STATE_DECISION_INTEL_OPT_1
    localparam NUM_ITER_WAIT = 64;
`elsif READRX_STATE_DECISION_INTEL_OPT_2
    localparam NUM_ITER_WAIT = 64;
`endif

localparam NCO_FTW_OFFSET = 4;

localparam SIN_LUT_DATA_WIDTH_0   = 8;
localparam SIN_LUT_DATA_WIDTH_1   = 7;
localparam SIN_LUT_NUM_ENTRY_0  = 1024;
localparam SIN_LUT_NUM_ENTRY_1  = 1536;

localparam NUM_ITER             = 3072;

localparam ADDR_STEP = 16;

reg         [`READRX_INST_LIST_DATA_WIDTH-1:0]     inst_list_mem [0:`READRX_INST_LIST_NUM_ENTRY-1];

reg [SIN_LUT_DATA_WIDTH_0-1:0]          sin_lut_n1024_mem_0 [0:SIN_LUT_NUM_ENTRY_0-1];
reg [SIN_LUT_DATA_WIDTH_1-1:0]          sin_lut_n1024_mem_1 [0:SIN_LUT_NUM_ENTRY_0-1];
reg [SIN_LUT_DATA_WIDTH_0-1:0]          cos_lut_n1024_mem_0 [0:SIN_LUT_NUM_ENTRY_0-1];
reg [SIN_LUT_DATA_WIDTH_1-1:0]          cos_lut_n1024_mem_1 [0:SIN_LUT_NUM_ENTRY_0-1];

reg [`READRX_SIN_LUT_DATA_WIDTH-1:0]          sin_mem [0:`READRX_SIN_LUT_NUM_ENTRY-1];
reg [`READRX_SIN_LUT_DATA_WIDTH-1:0]          cos_mem [0:`READRX_SIN_LUT_NUM_ENTRY-1];

reg [10:0] addr_0;
reg [10:0] addr_1;

readout_rx_circuit UUT ( // TODO
    .clk(clk),
    .rst(rst),

    .glb_counter(glb_counter), 

    .inst_list_wr_en(inst_list_wr_en),
    .inst_list_wr_addr(inst_list_wr_addr),
    .inst_list_wr_data(inst_list_wr_data),

    .nco_ftw_wr_sel(nco_ftw_wr_sel),
    .nco_ftw_wr_en(nco_ftw_wr_en),
    .nco_ftw_in(nco_ftw_in),

    .cali_coeff_wr_en(cali_coeff_wr_en),
    .cali_coeff_wr_data(cali_coeff_wr_data),

    .sin_lut_wr_en(sin_lut_wr_en),
    .cos_lut_wr_en(cos_lut_wr_en),
    .sinusoidal_lut_wr_addr(sinusoidal_lut_wr_addr),
    .sinusoidal_lut_wr_data(sinusoidal_lut_wr_data),

    .state_decision_coeff_wr_sel(state_decision_coeff_wr_sel),
    .state_decision_coeff_wr_en(state_decision_coeff_wr_en),
    .state_decision_coeff_wr_addr(state_decision_coeff_wr_addr),
    .state_decision_coeff_wr_data(state_decision_coeff_wr_data),

    `ifdef READRX_STATE_DECISION_INTEL_OPT_2
        .threshold_memory_wr_sel(threshold_memory_wr_sel),
        .threshold_memory_wr_en(threshold_memory_wr_en),
        .threshold_memory_wr_addr(threshold_memory_wr_addr),
        .threshold_memory_wr_data(threshold_memory_wr_data),
    `endif

    .i_in(i_in),
    .q_in(q_in),

    .valid_meas_result(valid_meas_result),
    .meas_result(meas_result),

    .valid_filter_result(valid_filter_result),
    .q_filter_result(q_filter_result),
    .i_filter_result(i_filter_result)
);

integer I, J, K;
integer WAIT_DURATION;
integer NUM_I, NUM_J;

always #10 clk = ~clk;

initial begin
    $dumpfile("readout_rx_circuit.vcd");
    $dumpvars(0, readout_rx_circuit_tb);

    clk = 1'b0;
    rst = 1'b0;
    
    // Manually reset reg signals
    inst_list_wr_en = 0;
    inst_list_wr_addr = 0;
    inst_list_wr_data = 0;
    nco_ftw_wr_sel = 0;
    nco_ftw_wr_en = 0;
    nco_ftw_in = 0;
    cali_coeff_wr_en = 0;
    cali_coeff_wr_data = 0;
    i_in = 0;
    q_in = 0;

    glb_counter = 0;

    sin_lut_wr_en = 0;
    cos_lut_wr_en = 0;
    sinusoidal_lut_wr_addr = 0;
    sinusoidal_lut_wr_data = 0;

    slope = 0;
    y_intercept = 0;
    state_decision_coeff_wr_sel = 0;
    state_decision_coeff_wr_en = 0;
    state_decision_coeff_wr_addr = 0;
    state_decision_coeff_wr_data = 0;

    `ifdef READRX_STATE_DECISION_INTEL_OPT_2
        threshold_memory_wr_sel = 0;
        threshold_memory_wr_en = 0;
        threshold_memory_wr_addr = 0;
        threshold_memory_wr_data = 0;
    `endif

    #5;
    rst = 1;
    #10;
    rst = 0;
    #5;
    
    // initialize nco_ftw
    for (I=0; I< `READRX_NUM_QUBIT; I=I+1) begin
            nco_ftw_wr_sel = I[`READRX_QUBIT_ADDR_WIDTH-1:0];
            nco_ftw_wr_en = 1'b1;
            nco_ftw_in = {{I[`READRX_QUBIT_ADDR_WIDTH-1:0], 1'b1}, {{NCO_FTW_OFFSET{1'b0}}, {(`READRX_NCO_N-`READRX_PHASE_WIDTH){1'b0}}}};
        #20;
    end
    nco_ftw_wr_sel = 0;
    nco_ftw_wr_en = 0;
    nco_ftw_in = 0;
    #20;

    // initialize memory
    for (I=0; I< NUM_ITER_INIT; I=I+1) begin
        // inst_list
        if (I < `READRX_INST_LIST_NUM_ENTRY) begin
            inst_list_wr_en = 1'b1;
            inst_list_wr_addr = I[`READRX_INST_LIST_ADDR_WIDTH-1:0];
            
            inst_list_wr_data = inst_list_mem[inst_list_wr_addr];
        end
        else begin
            inst_list_wr_en = 1'b0;
            inst_list_wr_addr = 0;
            inst_list_wr_data = 0;
        end
        #20;
    end
    inst_list_wr_en = 0;
    inst_list_wr_addr = 0;
    inst_list_wr_data = 0;
    #20;

    // initialize cali_coeff
    cali_coeff_wr_en = 1;
    /*
    cali_coeff_wr_data[(4*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH] = {2'b00, {(`READRX_IQ_CALI_WIDTH-2){1'b1}}}; // alpha_i
    cali_coeff_wr_data[(3*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH] = {2'b00, {(`READRX_IQ_CALI_WIDTH-2){1'b0}}}; // beta_i
    cali_coeff_wr_data[(2*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH] = {2'b00, {(`READRX_IQ_CALI_WIDTH-2){1'b1}}}; // alpha_q
    cali_coeff_wr_data[(1*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH] = {2'b00, {(`READRX_IQ_CALI_WIDTH-2){1'b0}}}; // beta_q
    cali_coeff_wr_data[(0*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH] = {2'b00, {(`READRX_IQ_CALI_WIDTH-2){1'b0}}}; // dc_correction
    */
    // /*
    cali_coeff_wr_data[(4*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH] = {1'b0, {(`READRX_IQ_CALI_WIDTH-1){1'b1}}}; // alpha_i
    cali_coeff_wr_data[(3*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH] = {2'b00, {(`READRX_IQ_CALI_WIDTH-2){1'b0}}}; // beta_i
    cali_coeff_wr_data[(2*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH] = {1'b0, {(`READRX_IQ_CALI_WIDTH-1){1'b1}}}; // alpha_q
    cali_coeff_wr_data[(1*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH] = {2'b00, {(`READRX_IQ_CALI_WIDTH-2){1'b0}}}; // beta_q
    cali_coeff_wr_data[(0*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH] = {2'b00, {(`READRX_IQ_CALI_WIDTH-2){1'b0}}}; // dc_correction
    // */
    // cali_coeff_wr_data[(0*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH] = {1'b1, {(`READRX_IQ_CALI_WIDTH-1){1'b1}}}; // dc_correction
    #20;
    cali_coeff_wr_en = 0;
    cali_coeff_wr_data = 0;

    // initialize sinusoidal lut
    sin_lut_wr_en = 0;
    cos_lut_wr_en = 0;
    sinusoidal_lut_wr_addr = 0;
    sinusoidal_lut_wr_data = 0;

    for (J=0; J< 2; J=J+1) begin // sin/cos
        for (I=0; I< `READRX_SIN_LUT_NUM_ENTRY; I=I+1) begin
            if (J == 0) sin_lut_wr_en = 1'b1;
            else sin_lut_wr_en = 1'b0;

            if (J == 0) cos_lut_wr_en = 1'b0;
            else cos_lut_wr_en = 1'b1;
            
            sinusoidal_lut_wr_addr = I[`READRX_SIN_LUT_ADDR_WIDTH-1:0];            
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

    // initialize state_decision_coeff

    // readout_rx_state_decision_unit_intel_opt
    `ifdef READRX_STATE_DECISION_INTEL_OPT_1
        slope = {1'b0, {(`READRX_STATE_DECISION_DATA_WIDTH-1){1'b1}}}; // -1.0 <= slope < +1.0
        y_intercept = `READRX_STATE_DECISION_DATA_WIDTH'b0; // -1.0 <= y_intercept < +1.0
        for (I=0; I< `READRX_NUM_QUBIT; I=I+1) begin
            state_decision_coeff_wr_sel = I[`READRX_QUBIT_ADDR_WIDTH-1:0];
            state_decision_coeff_wr_en = 1'b1;

            state_decision_coeff_wr_addr = 1'b0;
            state_decision_coeff_wr_data = y_intercept;
            #20;
            state_decision_coeff_wr_addr = 1'b1;
            state_decision_coeff_wr_data = slope;
            #20;
        end
        state_decision_coeff_wr_sel = 0;
        state_decision_coeff_wr_en = 0;
        state_decision_coeff_wr_data = 0;

    // readout_rx_state_decision_unit_google
    `elsif READRX_STATE_DECISION_GOOGLE
        slope = {1'b0, {(`READRX_STATE_DECISION_DATA_WIDTH-1){1'b1}}}; // -1.0 <= slope < +1.0
        y_intercept = `READRX_STATE_DECISION_DATA_WIDTH'b0; // -1.0 <= y_intercept < +1.0
        for (I=0; I< `READRX_NUM_QUBIT; I=I+1) begin
            state_decision_coeff_wr_sel = I[`READRX_QUBIT_ADDR_WIDTH-1:0];
            state_decision_coeff_wr_en = 1'b1;

            state_decision_coeff_wr_addr = 1'b0;
            state_decision_coeff_wr_data = y_intercept;
            #20;
            state_decision_coeff_wr_addr = 1'b1;
            state_decision_coeff_wr_data = slope;
            #20;
        end
        state_decision_coeff_wr_sel = 0;
        state_decision_coeff_wr_en = 0;
        state_decision_coeff_wr_data = 0;
    // readout_rx_state_decision_unit_baseline
    `elsif READRX_STATE_DECISION_BASELINE
        slope = {1'b0, {(`READRX_SIN_LUT_DATA_WIDTH-1){1'b1}}}; // -1.0 <= slope < +1.0
        y_intercept = `READRX_SIN_LUT_DATA_WIDTH'b0; // -1.0 <= y_intercept < +1.0
        NUM_I = (1 << `READRX_SIN_LUT_DATA_WIDTH);
        NUM_J = (1 << `READRX_SIN_LUT_DATA_WIDTH);
        for (K=0; K< `READRX_NUM_QUBIT; K=K+1) begin
            state_decision_coeff_wr_sel = K[`READRX_QUBIT_ADDR_WIDTH-1:0];
            state_decision_coeff_wr_en = 1'b1;
            for (J=0; J< NUM_J; J=J+1) begin
                for (I=0; I< NUM_I; I=I+1) begin
                    if (slope * (I) + y_intercept > (J)*(NUM_I>>1)) begin
                        state_decision_coeff_wr_data[I] = 1;
                    end
                    else begin
                        state_decision_coeff_wr_data[I] = 0;
                    end
                end
                state_decision_coeff_wr_addr = J;
                #20;
            end
        end
        state_decision_coeff_wr_sel = 0;
        state_decision_coeff_wr_en = 0;
        state_decision_coeff_wr_addr = 0;
        state_decision_coeff_wr_data = 0;
    `elsif READRX_STATE_DECISION_INTEL_OPT_2
        slope = {1'b0, {(`READRX_STATE_DECISION_DATA_WIDTH-1){1'b1}}}; // -1.0 <= slope < +1.0
        y_intercept = `READRX_STATE_DECISION_DATA_WIDTH'b0; // -1.0 <= y_intercept < +1.0
        for (I=0; I< `READRX_NUM_QUBIT; I=I+1) begin
            state_decision_coeff_wr_sel = I[`READRX_QUBIT_ADDR_WIDTH-1:0];
            state_decision_coeff_wr_en = 1'b1;

            state_decision_coeff_wr_addr = 1'b0;
            state_decision_coeff_wr_data = y_intercept;
            #20;
            state_decision_coeff_wr_addr = 1'b1;
            state_decision_coeff_wr_data = slope;
            #20;
        end
        state_decision_coeff_wr_sel = 0;
        state_decision_coeff_wr_en = 0;
        state_decision_coeff_wr_data = 0;

        #20;
        for (I=0; I< `READRX_NUM_QUBIT; I=I+1) begin
            threshold_memory_wr_sel = I[`READRX_QUBIT_ADDR_WIDTH-1:0];
            threshold_memory_wr_en = 1'b1;
            for (J=0; J< `READRX_THRESHOLD_MEMORY_NUM_ENTRY; J=J+1) begin
                threshold_memory_wr_addr = J[`READRX_THRESHOLD_MEMORY_ADDR_WIDTH-1:0];
                threshold_memory_wr_data = {`READRX_BIN_COUNTER_WIDTH'b1000_0000_0110_0000, `READRX_BIN_COUNTER_WIDTH'b0111_1111_1001_1111};
                #20;
            end
        end
        threshold_memory_wr_sel = 0;
        threshold_memory_wr_en = 0;
        threshold_memory_wr_addr = 0;
        threshold_memory_wr_data = 0;

    `endif
    // */
    #20;

    // Test 1
    // inst_list[0] = 0000000002015 (counter = 32, length = 256, channel_en = 6'b111111)
    #20;
    addr_0 = 32;
    for (I=0; I< NUM_ITER_TEST1; I=I+1) begin
        glb_counter = I;
        if (I >= 32) begin
            i_in = cos_lut_n1024_mem_0[addr_0];
            q_in = sin_lut_n1024_mem_0[addr_0];
            #20;
            if (addr_0 >= SIN_LUT_NUM_ENTRY_0-ADDR_STEP) addr_0 = 0;
            else addr_0 = addr_0 + ADDR_STEP;
        end
        else begin
            #20;
        end
    end

    i_in = 0;
    q_in = 0;
    #20;

    for (I=0; I< NUM_ITER_WAIT + 128; I=I+1) begin
        #20;
    end

    // // Test 2
    // // inst_list[1] = 0000000002015 (counter = 320, length = 256, channel_en = 6'b111111)
    // addr_0 = 320+256;
    // for (I=NUM_ITER_TEST1; I< NUM_ITER_TEST1+NUM_ITER_TEST2; I=I+1) begin
    //     glb_counter = I;
    //     if (I >= 320) begin
    //         i_in = {cos_lut_n1024_mem_1[addr_0][6], cos_lut_n1024_mem_1[addr_0]};
    //         q_in = {sin_lut_n1024_mem_1[addr_0][6], sin_lut_n1024_mem_1[addr_0]};
    //         #20;
    //         if (addr_0 >= SIN_LUT_NUM_ENTRY_0-ADDR_STEP) addr_0 = 0;
    //         else addr_0 = addr_0 + ADDR_STEP;
    //     end
    //     else begin
    //         #20;
    //     end
    // end

    // i_in = 0;
    // q_in = 0;
    // #20;

    // for (I=0; I< NUM_ITER_WAIT; I=I+1) begin
    //     #20;
    // end
    $finish;
end

initial begin
    // inst_list
    $readmemh("inst_list_n32_57b.mem", inst_list_mem, 0, `READRX_INST_LIST_NUM_ENTRY-1);
    // sinusoidal lut
    // $readmemh("signed_sin_n1024_16b.mem", sin_mem, 0, `READRX_SIN_LUT_NUM_ENTRY-1);
    // $readmemh("signed_cos_n1024_16b.mem", cos_mem, 0, `READRX_SIN_LUT_NUM_ENTRY-1);
    $readmemh("signed_sin_n1024_8b.mem", sin_mem, 0, `READRX_SIN_LUT_NUM_ENTRY-1);
    $readmemh("signed_cos_n1024_8b.mem", cos_mem, 0, `READRX_SIN_LUT_NUM_ENTRY-1);
    
    // input wave
    $readmemh("signed_sin_n1024_8b.mem", sin_lut_n1024_mem_0, 0, SIN_LUT_NUM_ENTRY_0-1);
    $readmemh("signed_cos_n1024_8b.mem", cos_lut_n1024_mem_0, 0, SIN_LUT_NUM_ENTRY_0-1);
    $readmemh("signed_sin_n1024_7b.mem", sin_lut_n1024_mem_1, 0, SIN_LUT_NUM_ENTRY_0-1);
    $readmemh("signed_cos_n1024_7b.mem", cos_lut_n1024_mem_1, 0, SIN_LUT_NUM_ENTRY_0-1);
end


endmodule

/* Expected result */
/*
*/