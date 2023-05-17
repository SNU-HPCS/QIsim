
`include "define_readout_rx_circuit.v"

module readout_rx_circuit (
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

    cali_coeff_wr_en,
    cali_coeff_wr_data,

    sin_lut_wr_en,
    cos_lut_wr_en,
    sinusoidal_lut_wr_addr,
    sinusoidal_lut_wr_data,

    state_decision_coeff_wr_sel,
    state_decision_coeff_wr_en,
    state_decision_coeff_wr_addr,
    state_decision_coeff_wr_data,

    `ifdef READRX_STATE_DECISION_INTEL_OPT_2
        threshold_memory_wr_sel,
        threshold_memory_wr_en,
        threshold_memory_wr_addr,
        threshold_memory_wr_data,
        threshold_memory_rd_addr_out,
        threshold_memory_rd_data_in,
    `endif

    /* input */
    i_in,
    q_in,

    /* output */
    valid_meas_result,
    meas_result,

    /* Assume the memory is instantiated outside of the module */
    inst_list_rd_addr_out,
    inst_list_rd_data_in,
    cos_lut_rd_addr_out,
    cos_lut_rd_data_in,
    sin_lut_rd_addr_out,
    sin_lut_rd_data_in,

    `ifdef READRX_STATE_DECISION_BASELINE
        bin_count_mem_wr_addr_out,
        bin_count_mem_wr_data_out,
        bin_count_mem_rd_addr_out,
        bin_count_mem_rd_data_in,
        bin_count_mem_roi_sel_rd_addr_out,
        bin_count_mem_roi_sel_rd_data_in,
        bin_count_mem_valid_rst_out,
        bin_count_mem_valid_wr_addr_out,
        bin_count_mem_valid_wr_data_out,
        bin_count_mem_valid_rd_addr_out,
        bin_count_mem_valid_rd_data_in,
    `endif

    /* Only for debugging */
    i_filter_result,
    q_filter_result,
    valid_filter_result
);

/* Port declaration */
input                                               clk; 
input                                               rst;
input       [`READRX_GLB_COUNTER_WIDTH-1:0]         glb_counter;

// inst_list
input                                               inst_list_wr_en;
input       [`READRX_INST_LIST_ADDR_WIDTH-1:0]      inst_list_wr_addr;
input       [`READRX_INST_LIST_DATA_WIDTH-1:0]      inst_list_wr_data;
 
// nco
input       [`READRX_QUBIT_ADDR_WIDTH-1:0]          nco_ftw_wr_sel;
input                                               nco_ftw_wr_en;
input       [`READRX_NCO_N-1:0]                     nco_ftw_in;

// calibration
input                                               cali_coeff_wr_en;
input       [`READRX_IQ_CALI_WIDTH*`READRX_NUM_CALI_COEFF-1:0]  cali_coeff_wr_data;

// sin_lut
input                                               sin_lut_wr_en;
input                                               cos_lut_wr_en;
input       [`READRX_SIN_LUT_ADDR_WIDTH-1:0]        sinusoidal_lut_wr_addr; 
input       [`READRX_SIN_LUT_DATA_WIDTH-1:0]        sinusoidal_lut_wr_data;

// state_decision
input       [`READRX_QUBIT_ADDR_WIDTH-1:0]            state_decision_coeff_wr_sel;
input                                                 state_decision_coeff_wr_en;
input       [`READRX_STATE_DECISION_ADDR_WIDTH-1:0]   state_decision_coeff_wr_addr; // [1,0]
input       [`READRX_STATE_DECISION_DATA_WIDTH-1:0]   state_decision_coeff_wr_data; // [slope, y_intercept]

`ifdef READRX_STATE_DECISION_INTEL_OPT_2
    input   [`READRX_QUBIT_ADDR_WIDTH-1:0]              threshold_memory_wr_sel;
    input                                               threshold_memory_wr_en;
    input   [`READRX_THRESHOLD_MEMORY_ADDR_WIDTH-1:0]   threshold_memory_wr_addr;
    input   [`READRX_THRESHOLD_MEMORY_DATA_WIDTH-1:0]   threshold_memory_wr_data;
    output  [`READRX_NUM_QUBIT*`READRX_THRESHOLD_MEMORY_ADDR_WIDTH-1:0]   threshold_memory_rd_addr_out;
    input   [`READRX_NUM_QUBIT*`READRX_THRESHOLD_MEMORY_DATA_WIDTH-1:0]   threshold_memory_rd_data_in;
`endif

// iq input
input       [`READRX_INPUT_IQ_WIDTH-1:0]            i_in;
input       [`READRX_INPUT_IQ_WIDTH-1:0]            q_in;

// output
output      [`READRX_NUM_QUBIT-1:0]                 valid_meas_result;
output      [`READRX_NUM_QUBIT-1:0]                 meas_result;

//
output      [`READRX_INST_LIST_ADDR_WIDTH-1:0]      inst_list_rd_addr_out;
input       [`READRX_INST_LIST_DATA_WIDTH-1:0]      inst_list_rd_data_in;
output      [`READRX_NUM_QUBIT*`READRX_SIN_LUT_ADDR_WIDTH-1:0] cos_lut_rd_addr_out;
input       [`READRX_NUM_QUBIT*`READRX_SIN_LUT_DATA_WIDTH-1:0] cos_lut_rd_data_in;
output      [`READRX_NUM_QUBIT*`READRX_SIN_LUT_ADDR_WIDTH-1:0] sin_lut_rd_addr_out;
input       [`READRX_NUM_QUBIT*`READRX_SIN_LUT_DATA_WIDTH-1:0] sin_lut_rd_data_in;

output      [`READRX_NUM_QUBIT-1:0]                                   valid_filter_result;
output      [`READRX_NUM_QUBIT*`READRX_SIN_LUT_DATA_WIDTH-1:0]        q_filter_result;
output      [`READRX_NUM_QUBIT*`READRX_SIN_LUT_DATA_WIDTH-1:0]        i_filter_result;

`ifdef READRX_STATE_DECISION_BASELINE
    output  [`READRX_NUM_QUBIT*`READRX_BIN_COUNT_MEM_ADDR_WIDTH-1:0]  bin_count_mem_wr_addr_out;
    output  [`READRX_NUM_QUBIT*`READRX_BIN_COUNT_MEM_DATA_WIDTH-1:0]  bin_count_mem_wr_data_out;
    output  [`READRX_NUM_QUBIT*`READRX_BIN_COUNT_MEM_ADDR_WIDTH-1:0]  bin_count_mem_rd_addr_out;
    input   [`READRX_NUM_QUBIT*`READRX_BIN_COUNT_MEM_DATA_WIDTH-1:0]  bin_count_mem_rd_data_in;

    output  [`READRX_NUM_QUBIT*`READRX_STATE_DECISION_ADDR_WIDTH-1:0] bin_count_mem_roi_sel_rd_addr_out;
    input   [`READRX_NUM_QUBIT*`READRX_STATE_DECISION_DATA_WIDTH-1:0] bin_count_mem_roi_sel_rd_data_in;

    output  [`READRX_NUM_QUBIT-1:0]                                   bin_count_mem_valid_rst_out;
    output  [`READRX_NUM_QUBIT*`READRX_BIN_COUNT_MEM_ADDR_WIDTH-1:0]  bin_count_mem_valid_wr_addr_out;
    output  [`READRX_NUM_QUBIT-1:0]                                   bin_count_mem_valid_wr_data_out;
    output  [`READRX_NUM_QUBIT*`READRX_BIN_COUNT_MEM_ADDR_WIDTH-1:0]  bin_count_mem_valid_rd_addr_out;
    input   [`READRX_NUM_QUBIT-1:0]                                   bin_count_mem_valid_rd_data_in;
`endif

// PC
wire        [`READRX_PC_WIDTH-1:0]                  PC;
wire        [`READRX_PC_WIDTH-1:0]                  next_PC;
wire                                                update_pc;

// inst_list
wire        [`READRX_INST_LIST_ADDR_WIDTH-1:0]      inst_list_rd_addr;
wire        [`READRX_INST_LIST_DATA_WIDTH-1:0]      inst_list_rd_data;

reg         [`READRX_LOGGING_SRC_WIDTH-1:0]         logging_src;
reg         [`READRX_AVG_WINDOW_WIDTH-1:0]          avg_window;
reg         [`READRX_SIGNAL_LENGTH_WIDTH-1:0]       length;
reg         [`READRX_NUM_QUBIT-1:0]                 channel_en;
reg                                                 valid_inst_list;

// signal length counter
wire        [`READRX_SIGNAL_LENGTH_WIDTH-1:0]       next_time;
reg         [`READRX_SIGNAL_LENGTH_WIDTH-1:0]       cur_time;

// readout_rx_signal_decode_unit
wire        [`READRX_NUM_QUBIT-1:0]                 valid_inst_in;
reg         [`READRX_NUM_QUBIT-1:0]                 valid_inst_0_1;
reg         [`READRX_NUM_QUBIT-1:0]                 valid_inst_1_1;

// calibration_unit
wire        [`READRX_IQ_CALI_WIDTH-1:0]             i_before_cali_sign_extend;
wire        [`READRX_IQ_CALI_WIDTH-1:0]             q_before_cali_sign_extend;
wire        [`READRX_IQ_CALI_OUT_WIDTH-1:0]         i_cali_out;
wire        [`READRX_IQ_CALI_OUT_WIDTH-1:0]         q_cali_out;

reg         [`READRX_INPUT_IQ_WIDTH-1:0]            i_before_cali;
reg         [`READRX_INPUT_IQ_WIDTH-1:0]            q_before_cali;
reg         [`READRX_IQ_CALI_OUT_WIDTH-1:0]         i_after_cali;
reg         [`READRX_IQ_CALI_OUT_WIDTH-1:0]         q_after_cali;

reg         [`READRX_IQ_CALI_WIDTH-1:0]             alpha_i;
reg         [`READRX_IQ_CALI_WIDTH-1:0]             beta_i;
reg         [`READRX_IQ_CALI_WIDTH-1:0]             alpha_q;
reg         [`READRX_IQ_CALI_WIDTH-1:0]             beta_q;
reg         [`READRX_IQ_CALI_WIDTH-1:0]             dc_correction;

reg                                                 valid_cali_in;
wire                                                valid_cali_out;

/* Declaration end */

genvar i;

// PC
assign next_PC = PC + 1;
assign update_pc = (glb_counter == inst_list_rd_data[(`READRX_SIGNAL_LENGTH_WIDTH+`READRX_NUM_QUBIT+`READRX_AVG_WINDOW_WIDTH+`READRX_LOGGING_SRC_WIDTH) +: `READRX_GLB_COUNTER_WIDTH]) ? 1'b1 : 1'b0;

readout_rx_pc #(
    .PC_WIDTH(`READRX_PC_WIDTH)
) pc_0 (
    .clk(clk),
    .rst(rst),
    .update_pc(update_pc),
    .next_PC(next_PC),
    .PC(PC)
);

// inst_list
assign inst_list_rd_addr = PC;
/*
random_access_mem #(
    .NUM_ENTRY(`READRX_INST_LIST_NUM_ENTRY),
    .ADDR_WIDTH(`READRX_INST_LIST_ADDR_WIDTH),
    .DATA_WIDTH(`READRX_INST_LIST_DATA_WIDTH)
) inst_list (
    .clk(clk),
    .wr_en(inst_list_wr_en),
    .wr_addr(inst_list_wr_addr),
    .wr_data(inst_list_wr_data),
    .rd_addr(inst_list_rd_addr),
    .rd_data(inst_list_rd_data)
);
*/
assign inst_list_rd_addr_out = inst_list_rd_addr;
assign inst_list_rd_data = inst_list_rd_data_in;

always @(posedge clk) begin
    // if (cur_time == 0) begin
    //     length <= inst_list_rd_data[`READRX_NUM_QUBIT +: `READRX_SIGNAL_LENGTH_WIDTH];
    //     channel_en <= inst_list_rd_data[0 +: `READRX_NUM_QUBIT];
    // end
    // else begin
    //     length <= length;
    //     channel_en <= channel_en;
    // end
    if (update_pc) begin
        length <= inst_list_rd_data[(`READRX_LOGGING_SRC_WIDTH+`READRX_AVG_WINDOW_WIDTH+`READRX_NUM_QUBIT) +: `READRX_SIGNAL_LENGTH_WIDTH];
        channel_en <= inst_list_rd_data[(`READRX_LOGGING_SRC_WIDTH+`READRX_AVG_WINDOW_WIDTH) +: `READRX_NUM_QUBIT];
        avg_window <= inst_list_rd_data[`READRX_LOGGING_SRC_WIDTH +: `READRX_AVG_WINDOW_WIDTH];
        logging_src <= inst_list_rd_data[0 +: `READRX_LOGGING_SRC_WIDTH];
    end
    else begin
        length <= length;
        channel_en <= channel_en;
        avg_window <= avg_window;
        logging_src <= logging_src;
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

// readout_rx_signal_decode_unit
always @(posedge clk) begin
    valid_inst_0_1 <= channel_en & {`READRX_NUM_QUBIT{((cur_time > 0) ? 1'b1 : 1'b0)}};
    valid_inst_1_1 <= valid_inst_0_1;
end

assign valid_inst_in = valid_inst_1_1;


generate
    for(i = 0; i < `READRX_NUM_QUBIT; i = i +1) begin: genblk_rx_signal_decode
        wire                    nco_ftw_wr_en_i;
        wire                    valid_inst_in_i;
        wire                    meas_result_i;
        wire                    valid_meas_result_i;
        wire [`READRX_SIN_LUT_ADDR_WIDTH-1:0] cos_lut_rd_addr_out_i;
        wire [`READRX_SIN_LUT_DATA_WIDTH-1:0] cos_lut_rd_data_in_i;
        wire [`READRX_SIN_LUT_ADDR_WIDTH-1:0] sin_lut_rd_addr_out_i;
        wire [`READRX_SIN_LUT_DATA_WIDTH-1:0] sin_lut_rd_data_in_i;

        wire                                  valid_filter_result_i;
        wire [`READRX_SIN_LUT_DATA_WIDTH-1:0] q_filter_result_i;
        wire [`READRX_SIN_LUT_DATA_WIDTH-1:0] i_filter_result_i;

        wire                    state_decision_coeff_wr_en_i;

        `ifdef READRX_STATE_DECISION_BASELINE
            wire  [`READRX_BIN_COUNT_MEM_ADDR_WIDTH-1:0]  bin_count_mem_wr_addr_out_i;
            wire  [`READRX_BIN_COUNT_MEM_DATA_WIDTH-1:0]  bin_count_mem_wr_data_out_i;
            wire  [`READRX_BIN_COUNT_MEM_ADDR_WIDTH-1:0]  bin_count_mem_rd_addr_out_i;
            wire  [`READRX_BIN_COUNT_MEM_DATA_WIDTH-1:0]  bin_count_mem_rd_data_in_i;

            wire  [`READRX_STATE_DECISION_ADDR_WIDTH-1:0] bin_count_mem_roi_sel_rd_addr_out_i;
            wire  [`READRX_STATE_DECISION_DATA_WIDTH-1:0] bin_count_mem_roi_sel_rd_data_in_i;

            wire                                     bin_count_mem_valid_rst_out_i;
            wire  [`READRX_BIN_COUNT_MEM_ADDR_WIDTH-1:0]  bin_count_mem_valid_wr_addr_out_i;
            wire                                     bin_count_mem_valid_wr_data_out_i;
            wire  [`READRX_BIN_COUNT_MEM_ADDR_WIDTH-1:0]  bin_count_mem_valid_rd_addr_out_i;
            wire                                      bin_count_mem_valid_rd_data_in_i;
        `endif

        assign nco_ftw_wr_en_i   = nco_ftw_wr_en & (nco_ftw_wr_sel == i);
        assign valid_inst_in_i = valid_inst_in[i];
        assign meas_result[i] = meas_result_i;
        assign valid_meas_result[i] = valid_meas_result_i;

        assign sin_lut_rd_addr_out[i*`READRX_SIN_LUT_ADDR_WIDTH +: `READRX_SIN_LUT_ADDR_WIDTH] = sin_lut_rd_addr_out_i;
        assign sin_lut_rd_data_in_i = sin_lut_rd_data_in[i*`READRX_SIN_LUT_DATA_WIDTH +: `READRX_SIN_LUT_DATA_WIDTH];
        assign cos_lut_rd_addr_out[i*`READRX_SIN_LUT_ADDR_WIDTH +: `READRX_SIN_LUT_ADDR_WIDTH] = cos_lut_rd_addr_out_i;
        assign cos_lut_rd_data_in_i = cos_lut_rd_data_in[i*`READRX_SIN_LUT_DATA_WIDTH +: `READRX_SIN_LUT_DATA_WIDTH];
        assign valid_filter_result[i] = valid_filter_result_i;
        assign q_filter_result[`READRX_SIN_LUT_DATA_WIDTH*i +: `READRX_SIN_LUT_DATA_WIDTH] = q_filter_result_i;
        assign i_filter_result[`READRX_SIN_LUT_DATA_WIDTH*i +: `READRX_SIN_LUT_DATA_WIDTH] = i_filter_result_i;

        assign state_decision_coeff_wr_en_i = state_decision_coeff_wr_en & (state_decision_coeff_wr_sel == i);

        `ifdef READRX_STATE_DECISION_INTEL_OPT_2
            wire threshold_memory_wr_en_i;
            assign threshold_memory_wr_en_i = threshold_memory_wr_en & (threshold_memory_wr_sel == i);
            wire    [`READRX_THRESHOLD_MEMORY_ADDR_WIDTH-1:0]   threshold_memory_rd_addr_out_i;
            wire    [`READRX_THRESHOLD_MEMORY_DATA_WIDTH-1:0]   threshold_memory_rd_data_in_i;
            assign threshold_memory_rd_addr_out[`READRX_THRESHOLD_MEMORY_ADDR_WIDTH*i +: `READRX_THRESHOLD_MEMORY_ADDR_WIDTH] = threshold_memory_rd_addr_out_i;
            assign threshold_memory_rd_data_in_i = threshold_memory_rd_data_in[`READRX_THRESHOLD_MEMORY_DATA_WIDTH*i +: `READRX_THRESHOLD_MEMORY_DATA_WIDTH];
        `endif
        `ifdef READRX_STATE_DECISION_BASELINE
            assign bin_count_mem_wr_addr_out[`READRX_BIN_COUNT_MEM_ADDR_WIDTH*i +: `READRX_BIN_COUNT_MEM_ADDR_WIDTH] = bin_count_mem_wr_addr_out_i;
            assign bin_count_mem_wr_data_out[`READRX_BIN_COUNT_MEM_DATA_WIDTH*i +: `READRX_BIN_COUNT_MEM_DATA_WIDTH] = bin_count_mem_wr_data_out_i;
            assign bin_count_mem_rd_addr_out[`READRX_BIN_COUNT_MEM_ADDR_WIDTH*i +: `READRX_BIN_COUNT_MEM_ADDR_WIDTH] = bin_count_mem_rd_addr_out_i;
            assign bin_count_mem_rd_data_in_i = bin_count_mem_rd_data_in[`READRX_BIN_COUNT_MEM_DATA_WIDTH*i +: `READRX_BIN_COUNT_MEM_DATA_WIDTH];
            
            assign bin_count_mem_roi_sel_rd_addr_out[`READRX_STATE_DECISION_ADDR_WIDTH*i +: `READRX_STATE_DECISION_ADDR_WIDTH] = bin_count_mem_roi_sel_rd_addr_out_i;
            assign bin_count_mem_roi_sel_rd_data_in_i = bin_count_mem_roi_sel_rd_data_in[`READRX_STATE_DECISION_DATA_WIDTH*i +: `READRX_STATE_DECISION_DATA_WIDTH];
            
            assign bin_count_mem_valid_rst_out[i] = bin_count_mem_valid_rst_out_i;
            assign bin_count_mem_valid_wr_addr_out[`READRX_BIN_COUNT_MEM_ADDR_WIDTH*i +: `READRX_BIN_COUNT_MEM_ADDR_WIDTH] = bin_count_mem_valid_wr_addr_out_i;
            assign bin_count_mem_valid_wr_data_out[i] = bin_count_mem_valid_wr_data_out_i;
            assign bin_count_mem_valid_rd_addr_out[`READRX_BIN_COUNT_MEM_ADDR_WIDTH*i +: `READRX_BIN_COUNT_MEM_ADDR_WIDTH] = bin_count_mem_valid_rd_addr_out_i;
            assign bin_count_mem_valid_rd_data_in_i = bin_count_mem_valid_rd_data_in[i];
        `endif

        readout_rx_signal_decode_unit #(
            .INPUT_IQ_WIDTH(`READRX_IQ_CALI_OUT_WIDTH),
            .NCO_N(`READRX_NCO_N),
            .PHASE_WIDTH(`READRX_PHASE_WIDTH),
            .SIN_LUT_NUM_ENTRY(`READRX_SIN_LUT_NUM_ENTRY),
            .SIN_LUT_ADDR_WIDTH(`READRX_SIN_LUT_ADDR_WIDTH),
            .SIN_LUT_DATA_WIDTH(`READRX_SIN_LUT_DATA_WIDTH),
            .AVG_FILTER_NUM_OPERAND(`READRX_AVG_FILTER_NUM_OPERAND),
            .AVG_FILTER_OPERAND_ADDR_WIDTH(`READRX_AVG_FILTER_OPERAND_ADDR_WIDTH),
            .AVG_FILTER_NUM_OPERAND(`READRX_AVG_FILTER_NUM_OPERAND),
            .AVG_FILTER_OPERAND_ADDR_WIDTH(`READRX_AVG_FILTER_OPERAND_ADDR_WIDTH),

            .NUM_THRESHOLD(`READRX_NUM_THRESHOLD),
            .BIN_COUNTER_WIDTH(`READRX_BIN_COUNTER_WIDTH),
            `ifdef READRX_STATE_DECISION_BASELINE
                .BIN_COUNT_MEM_NUM_ENTRY(`READRX_BIN_COUNT_MEM_NUM_ENTRY),
                .BIN_COUNT_MEM_ADDR_WIDTH(`READRX_BIN_COUNT_MEM_ADDR_WIDTH),
                .BIN_COUNT_MEM_DATA_WIDTH(`READRX_BIN_COUNT_MEM_DATA_WIDTH),
            `elsif READRX_STATE_DECISION_GOOGLE
                .ACCUMULATOR_WIDTH(`READRX_ACCUMULATOR_WIDTH),
            `elsif READRX_STATE_DECISION_INTEL_OPT_2
                .STEP_COUNTER_WIDTH(`READRX_STEP_COUNTER_WIDTH),
                .TRIAL_COUNTER_WIDTH(`READRX_TRIAL_COUNTER_WIDTH),
                .THRESHOLD_MEMORY_NUM_ENTRY(`READRX_THRESHOLD_MEMORY_NUM_ENTRY),
                .THRESHOLD_MEMORY_ADDR_WIDTH(`READRX_THRESHOLD_MEMORY_ADDR_WIDTH),
                .THRESHOLD_MEMORY_DATA_WIDTH(`READRX_THRESHOLD_MEMORY_DATA_WIDTH),
                .THRESHOLD_WIDTH(`READRX_THRESHOLD_WIDTH),
                .STEP_LIMIT_THRESHOLD(`READRX_STEP_LIMIT_THRESHOLD),
                .MAX_TRIAL(`READRX_MAX_TRIAL),
            `endif
            
            .STATE_DECISION_DATA_WIDTH(`READRX_STATE_DECISION_DATA_WIDTH),
            .STATE_DECISION_ADDR_WIDTH(`READRX_STATE_DECISION_ADDR_WIDTH)
        ) readout_rx_signal_decode_unit_instance (
            .clk(clk),
            .rst(rst),

            .nco_ftw_wr_en(nco_ftw_wr_en_i),
            .nco_ftw_in(nco_ftw_in),

            .sin_lut_wr_en(sin_lut_wr_en),
            .cos_lut_wr_en(cos_lut_wr_en),
            .sinusoidal_lut_wr_addr(sinusoidal_lut_wr_addr),
            .sinusoidal_lut_wr_data(sinusoidal_lut_wr_data),

            .state_decision_coeff_wr_en(state_decision_coeff_wr_en_i),
            .state_decision_coeff_wr_data(state_decision_coeff_wr_data),
            .state_decision_coeff_wr_addr(state_decision_coeff_wr_addr),

            `ifdef READRX_STATE_DECISION_INTEL_OPT_2
                .threshold_memory_wr_en(threshold_memory_wr_en_i),
                .threshold_memory_wr_addr(threshold_memory_wr_addr),
                .threshold_memory_wr_data(threshold_memory_wr_data),
                .threshold_memory_rd_addr_out(threshold_memory_rd_addr_out_i),
                .threshold_memory_rd_data_in(threshold_memory_rd_data_in_i),
            `endif

            .valid_inst_in(valid_inst_in_i),

            .i_in(i_after_cali),
            .q_in(q_after_cali),

            .valid_meas_result(valid_meas_result_i),
            .meas_result(meas_result_i),

            .cos_lut_rd_addr_out(cos_lut_rd_addr_out_i),
            .cos_lut_rd_data_in(cos_lut_rd_data_in_i),
            .sin_lut_rd_addr_out(sin_lut_rd_addr_out_i),
            .sin_lut_rd_data_in(sin_lut_rd_data_in_i),

            `ifdef READRX_STATE_DECISION_BASELINE
                .bin_count_mem_wr_addr_out(bin_count_mem_wr_addr_out_i),
                .bin_count_mem_wr_data_out(bin_count_mem_wr_data_out_i),
                .bin_count_mem_rd_addr_out(bin_count_mem_rd_addr_out_i),
                .bin_count_mem_rd_data_in(bin_count_mem_rd_data_in_i),
                .bin_count_mem_roi_sel_rd_addr_out(bin_count_mem_roi_sel_rd_addr_out_i),
                .bin_count_mem_roi_sel_rd_data_in(bin_count_mem_roi_sel_rd_data_in_i),
                .bin_count_mem_valid_rst_out(bin_count_mem_valid_rst_out_i),
                .bin_count_mem_valid_wr_addr_out(bin_count_mem_valid_wr_addr_out_i),
                .bin_count_mem_valid_wr_data_out(bin_count_mem_valid_wr_data_out_i),
                .bin_count_mem_valid_rd_addr_out(bin_count_mem_valid_rd_addr_out_i),
                .bin_count_mem_valid_rd_data_in(bin_count_mem_valid_rd_data_in_i),
            `endif

            .valid_filter_result(valid_filter_result_i),
            .q_filter_result(q_filter_result_i),
            .i_filter_result(i_filter_result_i)
        );
    end
endgenerate

// calibration_unit
assign i_before_cali_sign_extend = {{(`READRX_IQ_CALI_WIDTH-`READRX_INPUT_IQ_WIDTH){i_before_cali[`READRX_INPUT_IQ_WIDTH-1]}}, i_before_cali};
assign q_before_cali_sign_extend = {{(`READRX_IQ_CALI_WIDTH-`READRX_INPUT_IQ_WIDTH){q_before_cali[`READRX_INPUT_IQ_WIDTH-1]}}, q_before_cali};

readout_rx_calibration_unit #(
    .IQ_CALI_WIDTH(`READRX_IQ_CALI_WIDTH),
    .IQ_CALI_OUT_WIDTH(`READRX_IQ_CALI_OUT_WIDTH)
) readout_rx_calibration_unit_instance (
    .clk(clk),
    .i_in(i_before_cali_sign_extend),
    .q_in(q_before_cali_sign_extend),
    .alpha_i(alpha_i),
    .beta_i(beta_i),
    .alpha_q(alpha_q),
    .beta_q(beta_q),
    .dc_correction(dc_correction),
    .valid_in(valid_cali_in),
    .i_out(i_cali_out),
    .q_out(q_cali_out),
    .valid_out(valid_cali_out) // only for debugging
);

always @(posedge clk) begin
    i_before_cali <= i_in;
    q_before_cali <= q_in;
    valid_cali_in <= ((cur_time > 0) ? 1'b1 : 1'b0);

    i_after_cali <= i_cali_out;
    q_after_cali <= q_cali_out;

    if (rst) begin
        alpha_i <= 0;
        beta_i <= 0;
        alpha_q <= 0;
        beta_q <= 0;
        dc_correction <= 0;
    end
    else if (cali_coeff_wr_en) begin
        alpha_i         <= cali_coeff_wr_data[(4*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH];
        beta_i          <= cali_coeff_wr_data[(3*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH];
        alpha_q         <= cali_coeff_wr_data[(2*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH];
        beta_q          <= cali_coeff_wr_data[(1*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH];
        dc_correction   <= cali_coeff_wr_data[(0*`READRX_IQ_CALI_WIDTH) +: `READRX_IQ_CALI_WIDTH];
    end
    else begin
        alpha_i <= alpha_i;
        beta_i <= beta_i;
        alpha_q <= alpha_q;
        beta_q <= beta_q;
        dc_correction <= dc_correction;
    end
end

endmodule 
