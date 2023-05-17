// Readout tx circuit (based on Horse Ridge II)

`include "define_readout_tx_circuit.v"

module readout_tx_circuit (
    clk,
    rst,

    glb_counter, 

    /* Internal memory initialization */
    inst_list_wr_en,
    inst_list_wr_addr,
    inst_list_wr_data,

    nco_ftw_wr_sel,
    nco_ftw_wr_en,
    nco_ftw_in,

    sin_lut_wr_en,
    sin_lut_wr_addr,
    sin_lut_wr_data,

    /* output */
    valid_sin_wave_out,
    sin_wave_out
    // valid_sin_wave_sum_out,
    // sin_wave_sum_out

    // /* Assume the memory is instantiated outside of the module */
    // inst_list_rd_addr_out,
    // inst_list_rd_data_in,
    // sin_lut_rd_addr_out,
    // sin_lut_rd_data_in
);

/* Port declaration */
input                                       clk; 
input                                       rst;
input       [`READTX_GLB_COUNTER_WIDTH-1:0]         glb_counter;

// inst_list
input                                       inst_list_wr_en;
input       [`READTX_INST_LIST_ADDR_WIDTH-1:0]      inst_list_wr_addr;
input       [`READTX_INST_LIST_DATA_WIDTH-1:0]      inst_list_wr_data;
 
// nco
input       [`READTX_QUBIT_ADDR_WIDTH-1:0]         nco_ftw_wr_sel;
input                                       nco_ftw_wr_en;
input       [`READTX_NCO_N-1:0]                    nco_ftw_in;

// sin_lut
input                                       sin_lut_wr_en;
input       [`READTX_SIN_LUT_ADDR_WIDTH-1:0]       sin_lut_wr_addr;
input       [`READTX_SIN_LUT_DATA_WIDTH-1:0]       sin_lut_wr_data;

// output
output                                                          valid_sin_wave_out;
output      [`READTX_OUTPUT_WIDTH-1:0]                          sin_wave_out;
// output        [`READTX_NUM_QUBIT*`READTX_SIN_LUT_DATA_WIDTH-1:0]  sin_wave_out;
// output        [`READTX_NUM_QUBIT-1:0]               valid_sin_wave_out;

// output      [`READTX_INST_LIST_ADDR_WIDTH-1:0]                  inst_list_rd_addr_out;
// input       [`READTX_INST_LIST_DATA_WIDTH-1:0]                  inst_list_rd_data_in;

// output      [`READTX_NUM_QUBIT*`READTX_SIN_LUT_ADDR_WIDTH-1:0]  sin_lut_rd_addr_out;
// input       [`READTX_NUM_QUBIT*`READTX_SIN_LUT_DATA_WIDTH-1:0]  sin_lut_rd_data_in;

// PC
wire        [`READTX_PC_WIDTH-1:0]                              PC;
wire        [`READTX_PC_WIDTH-1:0]                              next_PC;
wire                                                            update_pc;

// inst_list
wire        [`READTX_INST_LIST_ADDR_WIDTH-1:0]                  inst_list_rd_addr;
wire        [`READTX_INST_LIST_DATA_WIDTH-1:0]                  inst_list_rd_data;

reg         [`READTX_SIGNAL_LENGTH_WIDTH-1:0]                   length;
reg         [`READTX_NUM_QUBIT-1:0]                             channel_en;
reg                                                             valid_inst_list;

// signal length counter
wire        [`READTX_SIGNAL_LENGTH_WIDTH-1:0]                   next_time;
reg         [`READTX_SIGNAL_LENGTH_WIDTH-1:0]                   cur_time;

// readout_tx_signal_gen_unit
wire        [`READTX_NUM_QUBIT-1:0]                             valid_inst_in;

wire        [`READTX_NUM_QUBIT-1:0]                             valid_sin_wave_out_per_qubit;
wire        [`READTX_NUM_QUBIT*`READTX_SIN_LUT_DATA_WIDTH-1:0]  sin_wave_out_per_qubit;

//
reg                                                             valid_sin_wave_sum;
reg         [`READTX_OUTPUT_WIDTH-1:0]                          sin_wave_sum;

/* Declaration end */

genvar i;

// PC
assign next_PC = PC + 1;
assign update_pc = (glb_counter == inst_list_rd_data[(`READTX_SIGNAL_LENGTH_WIDTH+`READTX_NUM_QUBIT) +: `READTX_GLB_COUNTER_WIDTH]) ? 1'b1 : 1'b0;

readout_tx_pc #(
    .PC_WIDTH(`READTX_PC_WIDTH)
) pc_0 (
    .clk(clk),
    .rst(rst),
    .update_pc(update_pc),
    .next_PC(next_PC),
    .PC(PC)
);

// inst_list
assign inst_list_rd_addr = PC;
// /*
random_access_mem #(
    .NUM_ENTRY(`READTX_INST_LIST_NUM_ENTRY),
    .ADDR_WIDTH(`READTX_INST_LIST_ADDR_WIDTH),
    .DATA_WIDTH(`READTX_INST_LIST_DATA_WIDTH)
) inst_list (
    .clk(clk),
    .wr_en(inst_list_wr_en),
    .wr_addr(inst_list_wr_addr),
    .wr_data(inst_list_wr_data),
    .rd_addr(inst_list_rd_addr),
    .rd_data(inst_list_rd_data)
);
// */
// assign inst_list_rd_addr_out = inst_list_rd_addr;
// assign inst_list_rd_data = inst_list_rd_data_in;

always @(posedge clk) begin
    // if (cur_time == 0) begin
    //     length <= inst_list_rd_data[`READTX_NUM_QUBIT +: `SIGNAL_LENGTH_WIDTH];
    //     channel_en <= inst_list_rd_data[0 +: `READTX_NUM_QUBIT];
    // end
    // else begin
    //     length <= length;
    //     channel_en <= channel_en;
    // end
    if (update_pc) begin
        length <= inst_list_rd_data[`READTX_NUM_QUBIT +: `READTX_SIGNAL_LENGTH_WIDTH];
        channel_en <= inst_list_rd_data[0 +: `READTX_NUM_QUBIT];
    end
    else begin
        length <= length;
        channel_en <= channel_en;
    end

    valid_inst_list <= update_pc;
end

// signal length counter
assign next_time = cur_time -1;

always @(posedge clk) begin
    if (rst) begin
        cur_time <= 0;
    end
    if (valid_inst_list) begin
        cur_time <= length;
    end
    else if (cur_time > 0) begin
        cur_time <= next_time;
    end
end

// readout_tx_signal_gen_unit
assign valid_inst_in = channel_en & {`READTX_NUM_QUBIT{(cur_time > 0) ? 1'b1 : 1'b0}};

generate
    for(i = 0; i < `READTX_NUM_QUBIT; i = i +1) begin: genblk_tx_signal_gen
        wire                            nco_ftw_wr_en_i;
        wire                            valid_inst_in_i;
        wire                            valid_sin_wave_out_i;
        wire [`READTX_SIN_LUT_DATA_WIDTH-1:0]  sin_wave_out_i;

        assign nco_ftw_wr_en_i   = nco_ftw_wr_en & (nco_ftw_wr_sel == i);
        assign valid_inst_in_i = valid_inst_in[i];
        assign valid_sin_wave_out_per_qubit[i] = valid_sin_wave_out_i;
        assign sin_wave_out_per_qubit[i*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] = sin_wave_out_i;
        
        //
        // wire [`READTX_SIN_LUT_ADDR_WIDTH-1:0] sin_lut_rd_addr_out_i;
        // wire [`READTX_SIN_LUT_DATA_WIDTH-1:0] sin_lut_rd_data_in_i;
        // assign sin_lut_rd_addr_out[i*`READTX_SIN_LUT_ADDR_WIDTH +: `READTX_SIN_LUT_ADDR_WIDTH] = sin_lut_rd_addr_out_i;
        // assign sin_lut_rd_data_in_i = sin_lut_rd_data_in[i*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH];

        readout_tx_signal_gen_unit #(
            .NCO_N(`READTX_NCO_N),
            .PHASE_WIDTH(`READTX_PHASE_WIDTH),
            .SIN_LUT_NUM_ENTRY(`READTX_SIN_LUT_NUM_ENTRY),
            .SIN_LUT_ADDR_WIDTH(`READTX_SIN_LUT_ADDR_WIDTH),
            .SIN_LUT_DATA_WIDTH(`READTX_SIN_LUT_DATA_WIDTH)
        ) readout_tx_signal_gen_unit_instance (
            .clk(clk),
            .rst(rst),
            .nco_ftw_wr_en(nco_ftw_wr_en_i),
            .nco_ftw_in(nco_ftw_in),
            .sin_lut_wr_en(sin_lut_wr_en),
            .sin_lut_wr_addr(sin_lut_wr_addr),
            .sin_lut_wr_data(sin_lut_wr_data),
            .valid_inst_in(valid_inst_in_i),
            .valid_sin_wave_out(valid_sin_wave_out_i),
            .sin_wave_out(sin_wave_out_i)

            // .sin_lut_rd_addr_out(sin_lut_rd_addr_out_i),
            // .sin_lut_rd_data_in(sin_lut_rd_data_in_i)
        );
    end
endgenerate

// output
// TODO: implement an adder tree and calculate a sum of waves
assign sin_wave_out = sin_wave_sum;
assign valid_sin_wave_out = valid_sin_wave_sum;
generate
    if (`READTX_NUM_QUBIT == 1) begin: genblk_sin_sum_1
        always @(posedge clk) begin
            sin_wave_sum        <= sin_wave_out_per_qubit;
            valid_sin_wave_sum  <= valid_sin_wave_out_per_qubit;
        end
    end
    else if (`READTX_NUM_QUBIT == 2) begin: genblk_sin_sum_2
        always @(posedge clk) begin
            sin_wave_sum        <= (valid_sin_wave_out_per_qubit[0] ? sin_wave_out_per_qubit[0*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[1] ? sin_wave_out_per_qubit[1*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0);
            valid_sin_wave_sum  <= |valid_sin_wave_out_per_qubit;
        end
    end
    else if (`READTX_NUM_QUBIT == 3) begin: genblk_sin_sum_3
        always @(posedge clk) begin
            sin_wave_sum        <= (valid_sin_wave_out_per_qubit[0] ? sin_wave_out_per_qubit[0*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[1] ? sin_wave_out_per_qubit[1*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[2] ? sin_wave_out_per_qubit[2*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0);
            valid_sin_wave_sum  <= |valid_sin_wave_out_per_qubit;
        end
    end
    else if (`READTX_NUM_QUBIT == 4) begin: genblk_sin_sum_4
        always @(posedge clk) begin
            sin_wave_sum        <= (valid_sin_wave_out_per_qubit[0] ? sin_wave_out_per_qubit[0*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[1] ? sin_wave_out_per_qubit[1*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[2] ? sin_wave_out_per_qubit[2*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[3] ? sin_wave_out_per_qubit[3*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0);
            valid_sin_wave_sum  <= |valid_sin_wave_out_per_qubit;
        end
    end
    else if (`READTX_NUM_QUBIT == 6) begin: genblk_sin_sum_6
        always @(posedge clk) begin
            sin_wave_sum        <= (valid_sin_wave_out_per_qubit[0] ? sin_wave_out_per_qubit[0*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[1] ? sin_wave_out_per_qubit[1*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[2] ? sin_wave_out_per_qubit[2*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[3] ? sin_wave_out_per_qubit[3*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[4] ? sin_wave_out_per_qubit[4*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[5] ? sin_wave_out_per_qubit[5*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0);
            valid_sin_wave_sum  <= |valid_sin_wave_out_per_qubit;
        end
    end
    else if (`READTX_NUM_QUBIT == 8) begin: genblk_sin_sum_8
        always @(posedge clk) begin
            sin_wave_sum        <= (valid_sin_wave_out_per_qubit[0] ? sin_wave_out_per_qubit[0*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[1] ? sin_wave_out_per_qubit[1*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[2] ? sin_wave_out_per_qubit[2*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[3] ? sin_wave_out_per_qubit[3*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[4] ? sin_wave_out_per_qubit[4*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[5] ? sin_wave_out_per_qubit[5*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[6] ? sin_wave_out_per_qubit[6*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[7] ? sin_wave_out_per_qubit[7*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0);
            valid_sin_wave_sum  <= |valid_sin_wave_out_per_qubit;
        end
    end
    else if (`READTX_NUM_QUBIT == 16) begin: genblk_sin_sum_16
        always @(posedge clk) begin
            sin_wave_sum        <= (valid_sin_wave_out_per_qubit[0] ? sin_wave_out_per_qubit[0*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[1] ? sin_wave_out_per_qubit[1*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[2] ? sin_wave_out_per_qubit[2*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[3] ? sin_wave_out_per_qubit[3*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[4] ? sin_wave_out_per_qubit[4*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[5] ? sin_wave_out_per_qubit[5*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[6] ? sin_wave_out_per_qubit[6*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[7] ? sin_wave_out_per_qubit[7*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[8] ? sin_wave_out_per_qubit[8*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[9] ? sin_wave_out_per_qubit[9*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[10] ? sin_wave_out_per_qubit[10*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[11] ? sin_wave_out_per_qubit[11*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[12] ? sin_wave_out_per_qubit[12*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[13] ? sin_wave_out_per_qubit[13*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[14] ? sin_wave_out_per_qubit[14*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0)
                                +  (valid_sin_wave_out_per_qubit[15] ? sin_wave_out_per_qubit[15*`READTX_SIN_LUT_DATA_WIDTH +: `READTX_SIN_LUT_DATA_WIDTH] : 0);
            valid_sin_wave_sum  <= |valid_sin_wave_out_per_qubit;
        end
    end
endgenerate

endmodule 
