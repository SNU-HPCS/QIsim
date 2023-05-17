`timescale 1ns/100ps

`include "define_readout_tx_circuit.v"

module readout_tx_circuit_tb();

reg                                        clk; 
reg                                        rst;
reg         [`READTX_GLB_COUNTER_WIDTH-1:0]       glb_counter;

// inst_list
reg                                        inst_list_wr_en;
reg         [`READTX_INST_LIST_ADDR_WIDTH-1:0]    inst_list_wr_addr;
reg         [`READTX_INST_LIST_DATA_WIDTH-1:0]    inst_list_wr_data;
 
// nco
reg         [`READTX_QUBIT_ADDR_WIDTH-1:0]        nco_ftw_wr_sel;
reg                                        nco_ftw_wr_en;
reg         [`READTX_NCO_N-1:0]                   nco_ftw_in;

// sin_lut
reg                                        sin_lut_wr_en;
reg         [`READTX_SIN_LUT_ADDR_WIDTH-1:0]      sin_lut_wr_addr;
reg         [`READTX_SIN_LUT_DATA_WIDTH-1:0]      sin_lut_wr_data;

// output
output      [`READTX_OUTPUT_WIDTH-1:0]            sin_wave_out;
output                                     valid_sin_wave_out;
// wire       [`READTX_NUM_QUBIT*`READTX_SIN_LUT_DATA_WIDTH-1:0]    sin_wave_out;
// wire       [`READTX_NUM_QUBIT-1:0]                 valid_sin_wave_out;

///
// localparam NUM_ITER_INIT  = 2048;
localparam NUM_ITER_INIT  = 40;
localparam NUM_ITER_TEST1 = 256;
localparam NUM_ITER_TEST2 = 512;
localparam NCO_FTW_OFFSET = 4;

reg         [`READTX_INST_LIST_DATA_WIDTH-1:0]    inst_list_mem [0:`READTX_INST_LIST_NUM_ENTRY-1];

reg         [`READTX_SIN_LUT_DATA_WIDTH-1:0]      sin_mem [0:`READTX_SIN_LUT_NUM_ENTRY-1];

readout_tx_circuit UUT (
    .clk(clk),
    .rst(rst),

    .glb_counter(glb_counter), 

    /* Internal memory initialization */
    .inst_list_wr_en(inst_list_wr_en),
    .inst_list_wr_addr(inst_list_wr_addr),
    .inst_list_wr_data(inst_list_wr_data),

    .nco_ftw_wr_sel(nco_ftw_wr_sel),
    .nco_ftw_wr_en(nco_ftw_wr_en),
    .nco_ftw_in(nco_ftw_in),

    .sin_lut_wr_en(sin_lut_wr_en),
    .sin_lut_wr_addr(sin_lut_wr_addr),
    .sin_lut_wr_data(sin_lut_wr_data),

    /* output */
    .valid_sin_wave_out(valid_sin_wave_out),
    .sin_wave_out(sin_wave_out)
    // valid_sin_wave_sum_out,
    // sin_wave_sum_out
);

integer I;
integer WAIT_DURATION;

always #10 clk = ~clk;

initial begin
    $dumpfile("readout_tx_circuit.vcd");
    $dumpvars(0, readout_tx_circuit_tb);

    clk = 1'b0;
    rst = 1'b0;
    
    // Manually reset reg signals
    inst_list_wr_en = 0;
    inst_list_wr_addr = 0;
    inst_list_wr_data = 0;
    nco_ftw_wr_sel = 0;
    nco_ftw_wr_en = 0;
    nco_ftw_in = 0;

    glb_counter = 0;

    sin_lut_wr_en = 0;
    sin_lut_wr_addr = 0;
    sin_lut_wr_data = 0;

    #5;
    rst = 1;
    #10;
    rst = 0;
    #5;
    
    // initialize nco_ftw
    for (I=0; I< `READTX_NUM_QUBIT; I=I+1) begin
            nco_ftw_wr_sel = I[`READTX_QUBIT_ADDR_WIDTH-1:0];
            nco_ftw_wr_en = 1'b1;
            nco_ftw_in = {{I[`READTX_QUBIT_ADDR_WIDTH-1:0], 1'b1}, {{NCO_FTW_OFFSET{1'b0}}, {(`READTX_NCO_N-`READTX_PHASE_WIDTH){1'b0}}}};
        #20;
    end
    nco_ftw_wr_sel = 0;
    nco_ftw_wr_en = 0;
    nco_ftw_in = 0;
    #20;

    // initialize memory
    for (I=0; I< NUM_ITER_INIT; I=I+1) begin
        // inst_list
        if (I < `READTX_INST_LIST_NUM_ENTRY) begin
            inst_list_wr_en = 1'b1;
            inst_list_wr_addr = I[`READTX_INST_LIST_ADDR_WIDTH-1:0];
            
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

    // initialize sin_lut
    sin_lut_wr_en = 0;
    sin_lut_wr_addr = 0;
    sin_lut_wr_data = 0;

    for (I=0; I< `READTX_SIN_LUT_NUM_ENTRY; I=I+1) begin
        sin_lut_wr_en = 1'b1;
        sin_lut_wr_addr = I[`READTX_SIN_LUT_ADDR_WIDTH-1:0];            
        sin_lut_wr_data = sin_mem[sin_lut_wr_addr];

        #20;
    end
    sin_lut_wr_en = 0;
    sin_lut_wr_addr = 0;
    sin_lut_wr_data = 0;
    #20;

    // Test 1
    // inst_list[0] = 0000000002015 (counter = 32, length = 128, channel_en = 6'b010101)
    #20;
    for (I=0; I< NUM_ITER_TEST1; I=I+1) begin
        glb_counter = I;
        #20;
    end
    #20;

    // Test 2
    // inst_list[1] = 000048000102a (counter = 288, length = 64, channel_en = 6'b101010)
    #20;
    for (I=NUM_ITER_TEST1; I< NUM_ITER_TEST2; I=I+1) begin
        glb_counter = I;
        #20;
    end
    #20;

    
    $finish;
end

initial begin
    // inst_list
    $readmemh("inst_list_n32_50b.mem", inst_list_mem, 0, `READTX_INST_LIST_NUM_ENTRY-1);
    // sin_lut
    $readmemh("sin_n1024_16b.mem", sin_mem, 0, `READTX_SIN_LUT_NUM_ENTRY-1);
end


endmodule

/* Expected result */
/*
*/