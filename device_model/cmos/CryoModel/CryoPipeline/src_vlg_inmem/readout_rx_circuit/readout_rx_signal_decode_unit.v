module readout_rx_signal_decode_unit #(
    // input
    parameter INPUT_IQ_WIDTH            = 16,

    // nco
    parameter NCO_N                     = 22,
    parameter PHASE_WIDTH               = 10,

    // sin_lut
    parameter SIN_LUT_NUM_ENTRY         = 1024,
    parameter SIN_LUT_ADDR_WIDTH        = PHASE_WIDTH,
    parameter SIN_LUT_DATA_WIDTH        = INPUT_IQ_WIDTH,

    
    // moving average filter
    parameter AVG_FILTER_NUM_OPERAND     = 8,
    parameter AVG_FILTER_OPERAND_ADDR_WIDTH = 3,

    // state_decision_unit
    parameter NUM_THRESHOLD = 0,
    parameter BIN_COUNTER_WIDTH = 16,

    `ifdef READRX_STATE_DECISION_BASELINE
        parameter BIN_COUNT_MEM_NUM_ENTRY = 65536,
        parameter BIN_COUNT_MEM_ADDR_WIDTH = 16,
        parameter BIN_COUNT_MEM_DATA_WIDTH = BIN_COUNTER_WIDTH,
    `elsif READRX_STATE_DECISION_GOOGLE
        parameter ACCUMULATOR_WIDTH = (SIN_LUT_DATA_WIDTH + 10),
    `elsif READRX_STATE_DECISION_INTEL_OPT_2
        parameter STEP_COUNTER_WIDTH = 8,
        parameter TRIAL_COUNTER_WIDTH = 4,
        parameter THRESHOLD_MEMORY_NUM_ENTRY = 16,
        parameter THRESHOLD_MEMORY_ADDR_WIDTH = 4,
        parameter THRESHOLD_MEMORY_DATA_WIDTH = 32,
        parameter THRESHOLD_WIDTH = 16,
        parameter STEP_LIMIT_THRESHOLD = 125,
        parameter MAX_TRIAL = 10,
    `endif

    parameter STATE_DECISION_DATA_WIDTH = SIN_LUT_DATA_WIDTH,
    parameter STATE_DECISION_ADDR_WIDTH = 1
)(
    clk,
    rst,

    nco_ftw_wr_en,
    nco_ftw_in,

    sin_lut_wr_en,
    cos_lut_wr_en,
    sinusoidal_lut_wr_addr,
    sinusoidal_lut_wr_data,

    state_decision_coeff_wr_en,
    state_decision_coeff_wr_data,
    state_decision_coeff_wr_addr,

    `ifdef READRX_STATE_DECISION_INTEL_OPT_2
        threshold_memory_wr_en,
        threshold_memory_wr_addr,
        threshold_memory_wr_data,
    `endif

    valid_inst_in,

    i_in,
    q_in,

    valid_meas_result,
    meas_result,

    i_filter_result,
    q_filter_result,
    valid_filter_result
);

/* localparam declaration */
localparam NCO_OUTPUT_WIDTH = PHASE_WIDTH;

localparam MUX_NUM_INPUT = 2;
localparam MUX_SEL_WIDTH = 1;

localparam MIXER_INPUT_WIDTH = SIN_LUT_DATA_WIDTH;
localparam MIXER_OUTPUT_WIDTH = SIN_LUT_DATA_WIDTH;

localparam AVG_FILTER_DATA_WIDTH = SIN_LUT_DATA_WIDTH;

/* Port declaration */
input                                           clk;
input                                           rst;
input                                           nco_ftw_wr_en;
input   [NCO_N-1:0]                             nco_ftw_in;

input                                           sin_lut_wr_en;
input                                           cos_lut_wr_en;
input   [SIN_LUT_ADDR_WIDTH-1:0]                sinusoidal_lut_wr_addr; 
input   [SIN_LUT_DATA_WIDTH-1:0]                sinusoidal_lut_wr_data;

input                                           state_decision_coeff_wr_en;
input   [STATE_DECISION_DATA_WIDTH-1:0]         state_decision_coeff_wr_data; // [slope, y_intercept]
input   [STATE_DECISION_ADDR_WIDTH-1:0]         state_decision_coeff_wr_addr; // [1, 0]

`ifdef READRX_STATE_DECISION_INTEL_OPT_2
    input                                       threshold_memory_wr_en;
    input   [THRESHOLD_MEMORY_ADDR_WIDTH-1:0]   threshold_memory_wr_addr;
    input   [THRESHOLD_MEMORY_DATA_WIDTH-1:0]   threshold_memory_wr_data;
`endif

input                                           valid_inst_in;

input   [INPUT_IQ_WIDTH-1:0]                    i_in;
input   [INPUT_IQ_WIDTH-1:0]                    q_in;

output                                          valid_meas_result;
output                                          meas_result;

output                                          valid_filter_result;
output      [AVG_FILTER_DATA_WIDTH-1:0]         i_filter_result;
output      [AVG_FILTER_DATA_WIDTH-1:0]         q_filter_result;

// nco
wire                                            nco_phase_wr_en;
wire    [NCO_OUTPUT_WIDTH-1:0]                  nco_phase_out;

// nco_mux
wire    [MUX_NUM_INPUT*NCO_OUTPUT_WIDTH-1:0]    nco_mux_data_in;
wire    [MUX_SEL_WIDTH-1:0]                     nco_mux_sel;
wire    [NCO_OUTPUT_WIDTH-1:0]                  nco_mux_data_out;

reg     [NCO_OUTPUT_WIDTH-1:0]                  selected_nco_phase;
reg                                             valid_selected_nco_phase;

// sin_lut
wire    [SIN_LUT_ADDR_WIDTH-1:0]                sin_lut_rd_addr;
wire    [SIN_LUT_DATA_WIDTH-1:0]                sin_lut_rd_data;
wire    [SIN_LUT_ADDR_WIDTH-1:0]                cos_lut_rd_addr;
wire    [SIN_LUT_DATA_WIDTH-1:0]                cos_lut_rd_data;

reg                                             valid_sinusoidal_wave;
reg     [SIN_LUT_DATA_WIDTH-1:0]                sin_wave;
reg     [SIN_LUT_DATA_WIDTH-1:0]                cos_wave;

// down-mixer
wire    [MIXER_OUTPUT_WIDTH-1:0]                i_mixer_out;
wire    [MIXER_OUTPUT_WIDTH-1:0]                q_mixer_out;

wire    [MIXER_INPUT_WIDTH-1:0]                 i_in_sign_extend;
wire    [MIXER_INPUT_WIDTH-1:0]                 q_in_sign_extend;

reg                                             valid_mixer;
reg     [MIXER_OUTPUT_WIDTH-1:0]                i_mixer;
reg     [MIXER_OUTPUT_WIDTH-1:0]                q_mixer;

// moving average filter
wire                                            valid_i_filter_out;
wire                                            valid_q_filter_out;
wire    [AVG_FILTER_DATA_WIDTH-1:0]             i_filter_out;
wire    [AVG_FILTER_DATA_WIDTH-1:0]             q_filter_out;

reg                                             valid_filter;
reg     [AVG_FILTER_DATA_WIDTH-1:0]             i_filter;
reg     [AVG_FILTER_DATA_WIDTH-1:0]             q_filter;

// state_decision_unit
reg                                             state_decision_start_count;
reg                                             state_decision_finish_count;
/* Declaration end */

// nco
assign nco_phase_wr_en = valid_inst_in;

nco_no_z_corr #(
    .N(NCO_N),
    .OUTPUT_WIDTH(NCO_OUTPUT_WIDTH)
) nco_instance (
    .clk(clk),
    .rst(rst),
    .ftw_wr_en(nco_ftw_wr_en),
    .ftw_in(nco_ftw_in),
    .phase_wr_en(nco_phase_wr_en),
    .phase_out(nco_phase_out)
);


// nco_mux
assign nco_mux_data_in = {nco_phase_out, {NCO_OUTPUT_WIDTH{1'b0}}};
assign nco_mux_sel = valid_inst_in;

mux_param #(
    .NUM_INPUT(MUX_NUM_INPUT),
    .SEL_WIDTH(MUX_SEL_WIDTH),
    .DATA_WIDTH(NCO_OUTPUT_WIDTH)
) nco_mux (
    .data_in(nco_mux_data_in),
    .sel(nco_mux_sel),
    .data_out(nco_mux_data_out)
);

always @(posedge clk) begin
    selected_nco_phase <= nco_mux_data_out;
    valid_selected_nco_phase <= valid_inst_in;
end

// sin_lut, cos_lut
assign sin_lut_rd_addr = selected_nco_phase;
assign cos_lut_rd_addr = selected_nco_phase;

sin_lut_param #(
    .NUM_ENTRY(SIN_LUT_NUM_ENTRY),
    .ADDR_WIDTH(SIN_LUT_ADDR_WIDTH),
    .DATA_WIDTH(SIN_LUT_DATA_WIDTH)
) sin_lut (
    .clk(clk),
    .wr_en(sin_lut_wr_en),
    .wr_addr(sinusoidal_lut_wr_addr),
    .wr_data(sinusoidal_lut_wr_data),
    .rd_addr(sin_lut_rd_addr),
    .rd_data(sin_lut_rd_data)
);

cos_lut_param #(
    .NUM_ENTRY(SIN_LUT_NUM_ENTRY),
    .ADDR_WIDTH(SIN_LUT_ADDR_WIDTH),
    .DATA_WIDTH(SIN_LUT_DATA_WIDTH)
) cos_lut (
    .clk(clk),
    .wr_en(cos_lut_wr_en),
    .wr_addr(sinusoidal_lut_wr_addr),
    .wr_data(sinusoidal_lut_wr_data),
    .rd_addr(cos_lut_rd_addr),
    .rd_data(cos_lut_rd_data)
);

always @(posedge clk) begin
    sin_wave <= sin_lut_rd_data;
    cos_wave <= cos_lut_rd_data;
    valid_sinusoidal_wave <= valid_selected_nco_phase;
end

// down-mixer
// assign i_in_sign_extend = {{(MIXER_INPUT_WIDTH-INPUT_IQ_WIDTH){i_in[INPUT_IQ_WIDTH-1]}}, i_in};
// assign q_in_sign_extend = {{(MIXER_INPUT_WIDTH-INPUT_IQ_WIDTH){q_in[INPUT_IQ_WIDTH-1]}}, q_in};
assign i_in_sign_extend = {i_in, {(MIXER_INPUT_WIDTH-INPUT_IQ_WIDTH){1'b0}}};
assign q_in_sign_extend = {q_in, {(MIXER_INPUT_WIDTH-INPUT_IQ_WIDTH){1'b0}}};

// TODO: use ifdef to selectively choose multipliers
// down_mixer #(
down_mixer_opt #(
    .INPUT_WIDTH(MIXER_INPUT_WIDTH),
    .OUTPUT_WIDTH(MIXER_OUTPUT_WIDTH)
) down_mixer_instance (
    .i_in_1(i_in_sign_extend),
    .q_in_1(q_in_sign_extend),
    .i_in_2(cos_wave),
    .q_in_2(sin_wave),
    .i_out(i_mixer_out),
    .q_out(q_mixer_out)
);

always @(posedge clk) begin
    // Shift numbers so that every number has a positive value
    // i_mixer <= {~i_mixer_out[MIXER_OUTPUT_WIDTH-1], i_mixer_out[MIXER_OUTPUT_WIDTH-2:0]};
    // q_mixer <= {~q_mixer_out[MIXER_OUTPUT_WIDTH-1], q_mixer_out[MIXER_OUTPUT_WIDTH-2:0]};
    i_mixer <= i_mixer_out;
    q_mixer <= q_mixer_out;
    
    valid_mixer <= valid_sinusoidal_wave;
end

// readout_rx_state_decision_unit_baseline
`ifdef READRX_STATE_DECISION_BASELINE
    // moving_average_filter
    moving_average_filter #(
        .DATA_WIDTH(AVG_FILTER_DATA_WIDTH),
        .NUM_OPERAND(AVG_FILTER_NUM_OPERAND),
        .OPERAND_ADDR_WIDTH(AVG_FILTER_OPERAND_ADDR_WIDTH)
    ) moving_average_filter_i (
        .clk(clk),
        .rst(rst),
        .valid_in(valid_mixer),
        .data_in(i_mixer),
        .valid_out(valid_i_filter_out),
        .data_out(i_filter_out)
    );

    moving_average_filter #(
        .DATA_WIDTH(AVG_FILTER_DATA_WIDTH),
        .NUM_OPERAND(AVG_FILTER_NUM_OPERAND),
        .OPERAND_ADDR_WIDTH(AVG_FILTER_OPERAND_ADDR_WIDTH)
    ) moving_average_filter_q (
        .clk(clk),
        .rst(rst),
        .valid_in(valid_mixer),
        .data_in(q_mixer),
        .valid_out(valid_q_filter_out),
        .data_out(q_filter_out)
    );

    always @(posedge clk) begin
        i_filter <= i_filter_out;
        q_filter <= q_filter_out;
        valid_filter <= (valid_i_filter_out & valid_q_filter_out);
    end

    // state_decision_unit
    readout_rx_state_decision_unit_baseline #(
        .DATA_WIDTH(SIN_LUT_DATA_WIDTH),
        .NUM_THRESHOLD(NUM_THRESHOLD),
        .BIN_COUNTER_WIDTH(BIN_COUNTER_WIDTH),
        .STATE_DECISION_DATA_WIDTH(STATE_DECISION_DATA_WIDTH),
        .STATE_DECISION_ADDR_WIDTH(STATE_DECISION_ADDR_WIDTH),
        .BIN_COUNT_MEM_NUM_ENTRY(BIN_COUNT_MEM_NUM_ENTRY),
        .BIN_COUNT_MEM_ADDR_WIDTH(BIN_COUNT_MEM_ADDR_WIDTH),
        .BIN_COUNT_MEM_DATA_WIDTH(BIN_COUNT_MEM_DATA_WIDTH)
    ) state_decision_unit_instance (
        .clk(clk),
        .rst(rst),

        .state_decision_coeff_wr_en(state_decision_coeff_wr_en),
        .state_decision_coeff_wr_data(state_decision_coeff_wr_data),
        .state_decision_coeff_wr_addr(state_decision_coeff_wr_addr),

        .start_count(state_decision_start_count),
        .finish_count(state_decision_finish_count),

        .valid_in(valid_filter),
        .i_in(i_filter),
        .q_in(q_filter),
        .valid_meas_result_out(valid_meas_result),
        .meas_result_out(meas_result)
    );

    assign i_filter_result = i_filter;
    assign q_filter_result = q_filter;
    assign valid_filter_result = valid_filter;

    always @(posedge clk) begin
        if ((~valid_filter) & (valid_i_filter_out & valid_q_filter_out)) state_decision_start_count <= 1'b1;
        else state_decision_start_count <= 1'b0;

        if (valid_filter & (~(valid_i_filter_out & valid_q_filter_out))) state_decision_finish_count <= 1'b1;
        else state_decision_finish_count <= 1'b0;
    end

// readout_rx_state_decision_unit_intel_opt_1
`elsif READRX_STATE_DECISION_INTEL_OPT_1
    // moving_average_filter
    moving_average_filter #(
        .DATA_WIDTH(AVG_FILTER_DATA_WIDTH),
        .NUM_OPERAND(AVG_FILTER_NUM_OPERAND),
        .OPERAND_ADDR_WIDTH(AVG_FILTER_OPERAND_ADDR_WIDTH)
    ) moving_average_filter_i (
        .clk(clk),
        .rst(rst),
        .valid_in(valid_mixer),
        .data_in(i_mixer),
        .valid_out(valid_i_filter_out),
        .data_out(i_filter_out)
    );

    moving_average_filter #(
        .DATA_WIDTH(AVG_FILTER_DATA_WIDTH),
        .NUM_OPERAND(AVG_FILTER_NUM_OPERAND),
        .OPERAND_ADDR_WIDTH(AVG_FILTER_OPERAND_ADDR_WIDTH)
    ) moving_average_filter_q (
        .clk(clk),
        .rst(rst),
        .valid_in(valid_mixer),
        .data_in(q_mixer),
        .valid_out(valid_q_filter_out),
        .data_out(q_filter_out)
    );

    always @(posedge clk) begin
        i_filter <= i_filter_out;
        q_filter <= q_filter_out;
        valid_filter <= (valid_i_filter_out & valid_q_filter_out);
    end

    // state_decision_unit
    readout_rx_state_decision_unit_intel_opt_1 #(
        .DATA_WIDTH(SIN_LUT_DATA_WIDTH),
        .NUM_THRESHOLD(NUM_THRESHOLD),
        .BIN_COUNTER_WIDTH(BIN_COUNTER_WIDTH),
        .STATE_DECISION_DATA_WIDTH(STATE_DECISION_DATA_WIDTH),
        .STATE_DECISION_ADDR_WIDTH(STATE_DECISION_ADDR_WIDTH)
    ) state_decision_unit_instance (
        .clk(clk),
        .rst(rst),

        .state_decision_coeff_wr_en(state_decision_coeff_wr_en),
        .state_decision_coeff_wr_data(state_decision_coeff_wr_data),
        .state_decision_coeff_wr_addr(state_decision_coeff_wr_addr),

        .start_count(state_decision_start_count),
        .finish_count(state_decision_finish_count),

        .valid_in(valid_filter),
        .i_in(i_filter),
        .q_in(q_filter),
        .valid_meas_result_out(valid_meas_result),
        .meas_result_out(meas_result)
    );

    assign i_filter_result = i_filter;
    assign q_filter_result = q_filter;
    assign valid_filter_result = valid_filter;

    always @(posedge clk) begin
        if ((~valid_filter) & (valid_i_filter_out & valid_q_filter_out)) state_decision_start_count <= 1'b1;
        else state_decision_start_count <= 1'b0;

        if (valid_filter & (~(valid_i_filter_out & valid_q_filter_out))) state_decision_finish_count <= 1'b1;
        else state_decision_finish_count <= 1'b0;
    end

// readout_rx_state_decision_unit_intel_opt_2
`elsif READRX_STATE_DECISION_INTEL_OPT_2
    // moving_average_filter
    moving_average_filter #(
        .DATA_WIDTH(AVG_FILTER_DATA_WIDTH),
        .NUM_OPERAND(AVG_FILTER_NUM_OPERAND),
        .OPERAND_ADDR_WIDTH(AVG_FILTER_OPERAND_ADDR_WIDTH)
    ) moving_average_filter_i (
        .clk(clk),
        .rst(rst),
        .valid_in(valid_mixer),
        .data_in(i_mixer),
        .valid_out(valid_i_filter_out),
        .data_out(i_filter_out)
    );

    moving_average_filter #(
        .DATA_WIDTH(AVG_FILTER_DATA_WIDTH),
        .NUM_OPERAND(AVG_FILTER_NUM_OPERAND),
        .OPERAND_ADDR_WIDTH(AVG_FILTER_OPERAND_ADDR_WIDTH)
    ) moving_average_filter_q (
        .clk(clk),
        .rst(rst),
        .valid_in(valid_mixer),
        .data_in(q_mixer),
        .valid_out(valid_q_filter_out),
        .data_out(q_filter_out)
    );

    always @(posedge clk) begin
        i_filter <= i_filter_out;
        q_filter <= q_filter_out;
        valid_filter <= (valid_i_filter_out & valid_q_filter_out);
    end

    // state_decision_unit
    readout_rx_state_decision_unit_intel_opt_2 #(
        .DATA_WIDTH(SIN_LUT_DATA_WIDTH),
        .NUM_THRESHOLD(NUM_THRESHOLD),
        .BIN_COUNTER_WIDTH(BIN_COUNTER_WIDTH),
        .STATE_DECISION_DATA_WIDTH(STATE_DECISION_DATA_WIDTH),
        .STATE_DECISION_ADDR_WIDTH(STATE_DECISION_ADDR_WIDTH),

        .STEP_COUNTER_WIDTH(STEP_COUNTER_WIDTH),
        .TRIAL_COUNTER_WIDTH(TRIAL_COUNTER_WIDTH),
        .THRESHOLD_MEMORY_NUM_ENTRY(THRESHOLD_MEMORY_NUM_ENTRY),
        .THRESHOLD_MEMORY_ADDR_WIDTH(THRESHOLD_MEMORY_ADDR_WIDTH),
        .THRESHOLD_MEMORY_DATA_WIDTH(THRESHOLD_MEMORY_DATA_WIDTH),
        .THRESHOLD_WIDTH(THRESHOLD_WIDTH),
        .STEP_LIMIT_THRESHOLD(STEP_LIMIT_THRESHOLD),
        .MAX_TRIAL(MAX_TRIAL)
    ) state_decision_unit_instance (
        .clk(clk),
        .rst(rst),

        .state_decision_coeff_wr_en(state_decision_coeff_wr_en),
        .state_decision_coeff_wr_data(state_decision_coeff_wr_data),
        .state_decision_coeff_wr_addr(state_decision_coeff_wr_addr),

        .threshold_memory_wr_en(threshold_memory_wr_en), // FILLME
        .threshold_memory_wr_addr(threshold_memory_wr_addr),// FILLME
        .threshold_memory_wr_data(threshold_memory_wr_data),// FILLME

        .start_count(state_decision_start_count),
        .finish_count(state_decision_finish_count),

        .valid_in(valid_filter),
        .i_in(i_filter),
        .q_in(q_filter),
        .valid_meas_result_out(valid_meas_result),
        .meas_result_out(meas_result)
    );

    assign i_filter_result = i_filter;
    assign q_filter_result = q_filter;
    assign valid_filter_result = valid_filter;

    always @(posedge clk) begin
        if ((~valid_filter) & (valid_i_filter_out & valid_q_filter_out)) state_decision_start_count <= 1'b1;
        else state_decision_start_count <= 1'b0;

        if (valid_filter & (~(valid_i_filter_out & valid_q_filter_out))) state_decision_finish_count <= 1'b1;
        else state_decision_finish_count <= 1'b0;
    end

// readout_rx_state_decision_unit_google
`elsif READRX_STATE_DECISION_GOOGLE
    // state_decision_unit
    readout_rx_state_decision_unit_google #(
        .DATA_WIDTH(SIN_LUT_DATA_WIDTH),
        .ACCUMULATOR_WIDTH(ACCUMULATOR_WIDTH),
        .STATE_DECISION_DATA_WIDTH(STATE_DECISION_DATA_WIDTH),
        .STATE_DECISION_ADDR_WIDTH(STATE_DECISION_ADDR_WIDTH)
    ) state_decision_unit_instance (
        .clk(clk),
        .rst(rst),

        .state_decision_coeff_wr_en(state_decision_coeff_wr_en),
        .state_decision_coeff_wr_data(state_decision_coeff_wr_data),
        .state_decision_coeff_wr_addr(state_decision_coeff_wr_addr),

        .start_count(state_decision_start_count),
        .finish_count(state_decision_finish_count),

        .valid_in(valid_mixer),
        .i_in(i_mixer),
        .q_in(q_mixer),

        .valid_meas_result_out(valid_meas_result),
        .meas_result_out(meas_result)
    );

    assign i_filter_result = i_mixer;
    assign q_filter_result = q_mixer;
    assign valid_filter_result = valid_mixer;

    always @(posedge clk) begin
        if ((~valid_mixer) & (valid_sinusoidal_wave)) state_decision_start_count <= 1'b1;
        else state_decision_start_count <= 1'b0;

        if (valid_mixer & (~(valid_sinusoidal_wave))) state_decision_finish_count <= 1'b1;
        else state_decision_finish_count <= 1'b0;
    end
`endif

endmodule
    