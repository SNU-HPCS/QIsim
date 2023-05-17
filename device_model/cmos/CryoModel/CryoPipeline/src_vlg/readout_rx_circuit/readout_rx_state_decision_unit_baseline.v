`ifndef DEFINE_READOUT_RX_CIRCUIT_V
`include "define_readout_rx_circuit.v"
`endif

module readout_rx_state_decision_unit_baseline #(
    parameter DATA_WIDTH = 16,
    parameter NUM_THRESHOLD = 0, // N(count_cont) - N(!count_cond)
    parameter BIN_COUNTER_WIDTH = 16,  // ** not specified in the paper

    parameter BIN_COUNT_MEM_NUM_ENTRY  = 65536,
    parameter BIN_COUNT_MEM_ADDR_WIDTH = 16,
    parameter BIN_COUNT_MEM_DATA_WIDTH = BIN_COUNTER_WIDTH,

    parameter STATE_DECISION_DATA_WIDTH = DATA_WIDTH,
    parameter STATE_DECISION_ADDR_WIDTH = 1
)(
    clk,
    rst,

    state_decision_coeff_wr_en,
    state_decision_coeff_wr_addr,
    state_decision_coeff_wr_data,

    start_count,
    finish_count,

    valid_in,
    i_in,
    q_in,

    valid_meas_result_out,
    meas_result_out,

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
    bin_count_mem_valid_rd_data_in
);

localparam BIN_COUNT_MEM_HALF_ADDR_WIDTH = BIN_COUNT_MEM_ADDR_WIDTH >> 1;
localparam STATE_DECISION_NUM_ENTRY = STATE_DECISION_DATA_WIDTH;

input clk;
input rst;

input                                   state_decision_coeff_wr_en;
input [STATE_DECISION_ADDR_WIDTH-1:0]   state_decision_coeff_wr_addr;
input [STATE_DECISION_DATA_WIDTH-1:0]   state_decision_coeff_wr_data;

input start_count;
input finish_count;

input valid_in;
input [DATA_WIDTH-1:0] i_in;
input [DATA_WIDTH-1:0] q_in;

output valid_meas_result_out;
output meas_result_out;

//
output  [BIN_COUNT_MEM_ADDR_WIDTH-1:0]  bin_count_mem_wr_addr_out;
output  [BIN_COUNT_MEM_DATA_WIDTH-1:0]  bin_count_mem_wr_data_out;
output  [BIN_COUNT_MEM_ADDR_WIDTH-1:0]  bin_count_mem_rd_addr_out;
input   [BIN_COUNT_MEM_DATA_WIDTH-1:0]  bin_count_mem_rd_data_in;

output  [STATE_DECISION_ADDR_WIDTH-1:0] bin_count_mem_roi_sel_rd_addr_out;
input   [STATE_DECISION_DATA_WIDTH-1:0] bin_count_mem_roi_sel_rd_data_in;

output                                  bin_count_mem_valid_rst_out;
output [BIN_COUNT_MEM_ADDR_WIDTH-1:0]   bin_count_mem_valid_wr_addr_out;
output                                  bin_count_mem_valid_wr_data_out;
output [BIN_COUNT_MEM_ADDR_WIDTH-1:0]   bin_count_mem_valid_rd_addr_out;
input                                   bin_count_mem_valid_rd_data_in;


//
wire [DATA_WIDTH-1:0] i_unsigned;
wire [DATA_WIDTH-1:0] q_unsigned;

wire                                 bin_count_mem_wr_en;
wire  [BIN_COUNT_MEM_ADDR_WIDTH-1:0] bin_count_mem_wr_addr;
wire  [BIN_COUNT_MEM_DATA_WIDTH-1:0] bin_count_mem_wr_data;

wire  [BIN_COUNT_MEM_ADDR_WIDTH-1:0] bin_count_mem_rd_addr;
wire  [BIN_COUNT_MEM_DATA_WIDTH-1:0] bin_count_mem_rd_data;

// reg [BIN_COUNT_MEM_NUM_ENTRY-1:0] bin_count_mem_valid;   
// reg [BIN_COUNT_MEM_NUM_ENTRY-1:0] bin_count_mem_roi_sel;   

wire [BIN_COUNT_MEM_HALF_ADDR_WIDTH-1:0] bin_counter_addr_i;
wire [BIN_COUNT_MEM_HALF_ADDR_WIDTH-1:0] bin_counter_addr_q;

wire                                  bin_count_mem_roi_sel_wr_en;
wire  [STATE_DECISION_ADDR_WIDTH-1:0] bin_count_mem_roi_sel_wr_addr;
wire  [STATE_DECISION_DATA_WIDTH-1:0] bin_count_mem_roi_sel_wr_data;

wire  [STATE_DECISION_ADDR_WIDTH-1:0] bin_count_mem_roi_sel_rd_addr;
wire  [STATE_DECISION_DATA_WIDTH-1:0] bin_count_mem_roi_sel_rd_data;


wire                                bin_count_mem_valid_rst;
wire                                bin_count_mem_valid_wr_en;
wire [BIN_COUNT_MEM_ADDR_WIDTH-1:0] bin_count_mem_valid_wr_addr;
wire                                bin_count_mem_valid_wr_data;
wire [BIN_COUNT_MEM_ADDR_WIDTH-1:0] bin_count_mem_valid_rd_addr;
wire                                bin_count_mem_valid_rd_data;



reg [BIN_COUNTER_WIDTH-1:0] bin_count;
wire [BIN_COUNTER_WIDTH-1:0] next_bin_count;

wire count_condition;
wire bin_count_finish_condition;
wire meas_result_condition;

reg process_result;

reg valid_meas_result;
reg meas_result;
reg [BIN_COUNT_MEM_ADDR_WIDTH-1:0] bin_counter_addr;

wire cur_bin_count_mem_roi_sel;
wire cur_bin_count_mem_valid;
//

assign i_unsigned = {~i_in[DATA_WIDTH-1], i_in[DATA_WIDTH-2:0]};
assign q_unsigned = {~q_in[DATA_WIDTH-1], q_in[DATA_WIDTH-2:0]};

assign bin_count_mem_wr_en   = valid_in;

assign bin_count_mem_wr_addr = {q_unsigned[(DATA_WIDTH-1) -: BIN_COUNT_MEM_HALF_ADDR_WIDTH],
                            i_unsigned[(DATA_WIDTH-1) -: BIN_COUNT_MEM_HALF_ADDR_WIDTH]};
assign bin_count_mem_rd_addr = process_result ? bin_counter_addr : bin_count_mem_wr_addr;
assign bin_count_mem_wr_data = bin_count_mem_valid_rd_data ? bin_count_mem_rd_data +1 : 1;

/*
random_access_mem #(
    .NUM_ENTRY(BIN_COUNT_MEM_NUM_ENTRY),
    .ADDR_WIDTH(BIN_COUNT_MEM_ADDR_WIDTH),
    .DATA_WIDTH(BIN_COUNT_MEM_DATA_WIDTH)
) bin_count_mem (
    .clk(clk),
    .wr_en(bin_count_mem_wr_en),
    .wr_addr(bin_count_mem_wr_addr),
    .wr_data(bin_count_mem_wr_data),
    .rd_addr(bin_count_mem_rd_addr),
    .rd_data(bin_count_mem_rd_data)
);
*/

assign bin_count_mem_wr_addr_out = bin_count_mem_wr_addr;
assign bin_count_mem_wr_data_out = bin_count_mem_wr_data;
assign bin_count_mem_rd_addr_out = bin_count_mem_rd_addr;
assign bin_count_mem_rd_data = bin_count_mem_rd_data_in;



assign bin_counter_addr_i = bin_counter_addr[0*BIN_COUNT_MEM_HALF_ADDR_WIDTH +: BIN_COUNT_MEM_HALF_ADDR_WIDTH];
assign bin_counter_addr_q = bin_counter_addr[1*BIN_COUNT_MEM_HALF_ADDR_WIDTH +: BIN_COUNT_MEM_HALF_ADDR_WIDTH];

assign bin_count_mem_roi_sel_wr_en = state_decision_coeff_wr_en;
assign bin_count_mem_roi_sel_wr_addr = state_decision_coeff_wr_addr;
assign bin_count_mem_roi_sel_wr_data = state_decision_coeff_wr_data;
assign bin_count_mem_roi_sel_rd_addr = bin_counter_addr_q;

/*
random_access_mem #(
    .NUM_ENTRY(STATE_DECISION_NUM_ENTRY),
    .ADDR_WIDTH(STATE_DECISION_ADDR_WIDTH),
    .DATA_WIDTH(STATE_DECISION_DATA_WIDTH)
) bin_count_mem_roi_sel (
    .clk(clk),
    .wr_en(bin_count_mem_roi_sel_wr_en),
    .wr_addr(bin_count_mem_roi_sel_wr_addr),
    .wr_data(bin_count_mem_roi_sel_wr_data),
    .rd_addr(bin_count_mem_roi_sel_rd_addr),
    .rd_data(bin_count_mem_roi_sel_rd_data)
);
*/
assign bin_count_mem_roi_sel_rd_addr_out = bin_count_mem_roi_sel_rd_addr;
assign bin_count_mem_roi_sel_rd_data = bin_count_mem_roi_sel_rd_data_in;


assign bin_count_mem_valid_rst = rst | (process_result & bin_count_finish_condition);
assign bin_count_mem_valid_wr_en = valid_in;
assign bin_count_mem_valid_wr_addr = bin_count_mem_rd_addr;
assign bin_count_mem_valid_wr_data = 1'b1;
assign bin_count_mem_valid_rd_addr = (process_result) ? bin_counter_addr : bin_count_mem_rd_addr;

/*
random_access_mem_valid #(
    .NUM_ENTRY(BIN_COUNT_MEM_NUM_ENTRY),
    .ADDR_WIDTH(BIN_COUNT_MEM_ADDR_WIDTH)
) bin_count_mem_valid (
    .clk(clk),
    .rst(bin_count_mem_valid_rst),
    .wr_en(bin_count_mem_valid_wr_en),
    .wr_addr(bin_count_mem_valid_wr_addr),
    .wr_data(bin_count_mem_valid_wr_data),
    .rd_addr(bin_count_mem_valid_rd_addr),
    .rd_data(bin_count_mem_valid_rd_data)
);
*/
assign bin_count_mem_valid_rst_out = bin_count_mem_valid_rst;
assign bin_count_mem_valid_wr_addr_out = bin_count_mem_valid_wr_addr;
assign bin_count_mem_valid_wr_data_out = bin_count_mem_valid_wr_data;
assign bin_count_mem_valid_rd_addr_out = bin_count_mem_valid_rd_addr;
assign bin_count_mem_valid_rd_data = bin_count_mem_valid_rd_data_in;


assign bin_count_finish_condition = (bin_counter_addr >= BIN_COUNT_MEM_NUM_ENTRY-1) ? 1'b1 : 1'b0;
assign cur_bin_count_mem_roi_sel = bin_count_mem_roi_sel_rd_data[bin_counter_addr_i];
assign cur_bin_count_mem_valid = bin_count_mem_valid_rd_data;
assign count_condition = cur_bin_count_mem_roi_sel & cur_bin_count_mem_valid;
assign next_bin_count = count_condition ? bin_count + bin_count_mem_rd_data : bin_count;
assign meas_result_condition = (bin_count >= NUM_THRESHOLD) ? 1'b1 : 1'b0;

always @(posedge clk) begin
    if (rst) begin
        process_result <= 0;
        bin_counter_addr <= 0;
        valid_meas_result <= 0;
        meas_result <= 0;
        bin_count <= 0;
    end
    else begin
        if (process_result) begin
            if (bin_count_finish_condition) begin
                process_result <= 0;
                bin_counter_addr <= 0;
                valid_meas_result <= 1;
                meas_result <= meas_result_condition;
                bin_count <= 0;
            end
            else begin
                process_result <= 1;
                bin_counter_addr <= bin_counter_addr +1;
                valid_meas_result <= 0;
                meas_result <= meas_result_condition;
                bin_count <= next_bin_count;
            end
        end
        else begin // ~process_result
            if (finish_count) begin
                process_result <= 1;
                bin_counter_addr <= 0;
                valid_meas_result <= 0;
                meas_result <= 0;
                bin_count <= 0;
            end
            else begin
                process_result <= 0;
                bin_counter_addr <= 0;
                valid_meas_result <= 0;
                meas_result <= 0;
                bin_count <= 0;
            end
        end
    end
end

assign valid_meas_result_out = valid_meas_result;
assign meas_result_out = meas_result;



endmodule