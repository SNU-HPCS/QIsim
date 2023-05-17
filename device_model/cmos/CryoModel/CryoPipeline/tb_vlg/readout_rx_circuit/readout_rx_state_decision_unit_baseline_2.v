module readout_rx_state_decision_unit_baseline_2 #(
    parameter DATA_WIDTH = 16,
    parameter ROI_THRESHOLD = 16384,
    parameter NUM_THRESHOLD = 0, // N(amp>=ROI_THRESHOLD) - N(amp<ROI_THRESHOLD)
    parameter BIN_COUNTER_WIDTH = 16,  // ** not specified in the paper

    parameter BIN_COUNT_NUM_ENTRY  = 65536,
    parameter BIN_COUNT_ADDR_WIDTH = 16,
    parameter BIN_COUNT_DATA_WIDTH = BIN_COUNTER_WIDTH
)(
    clk,
    rst,

    start_count,
    finish_count,

    valid_in,
    i_in,
    q_in,

    valid_meas_result_out,
    meas_result_out
);

localparam BIN_COUNT_MEM_HALF_ADDR_WIDTH = BIN_COUNT_ADDR_WIDTH >> 1;

input clk;
input rst;

input start_count;
input finish_count;

input valid_in;
input [DATA_WIDTH-1:0] i_in;
input [DATA_WIDTH-1:0] q_in;

output valid_meas_result_out;
output meas_result_out;

//
wire [DATA_WIDTH-1:0] i_unsigned;
wire [DATA_WIDTH-1:0] q_unsigned;

reg [BIN_COUNT_NUM_ENTRY-1:0] bin_count_mem_roi_sel;   


reg [BIN_COUNT_ADDR_WIDTH-1:0]                          bin_count_rd_addr;
reg [BIN_COUNT_NUM_ENTRY*BIN_COUNT_DATA_WIDTH-1:0]      bin_count_rd_data;
wire                                                    bin_count_rst;


reg [BIN_COUNTER_WIDTH-1:0] bin_count_sum;
wire [BIN_COUNTER_WIDTH-1:0] next_bin_count;

wire count_condition;
wire bin_count_finish_condition;
wire meas_result_condition;

reg process_result;

reg valid_meas_result;
reg meas_result;

wire cur_bin_count_mem_roi_sel;
wire cur_bin_count_mem_valid;
//

assign i_unsigned = {~i_in[DATA_WIDTH-1], i_in[DATA_WIDTH-2:0]};
assign q_unsigned = {~q_in[DATA_WIDTH-1], q_in[DATA_WIDTH-2:0]};

assign bin_count_mem_wr_en   = valid_in;
assign bin_count_wr_addr = {i_unsigned[(DATA_WIDTH-1) -: BIN_COUNT_MEM_HALF_ADDR_WIDTH],
                            q_unsigned[(DATA_WIDTH-1) -: BIN_COUNT_MEM_HALF_ADDR_WIDTH]};

assign bin_count_rst = (rst | valid_meas_result_out);

generate
    for(i = 0; i < BIN_COUNT_NUM_ENTRY; i = i +1) begin: genblk_counter
        wire                                bin_count_en_i;
        wire [BIN_COUNT_DATA_WIDTH-1:0]     bin_count_rd_data_i;

        assign bin_count_en_i = (i == bin_count_wr_addr) ? 1'b1 : 1'b0;
        assign bin_count_rd_data[BIN_COUNT_DATA_WIDTH*i +: BIN_COUNT_DATA_WIDTH] = bin_count_rd_data_i;
        
        counter_param #(
            .COUNT_WIDTH(BIN_COUNT_DATA_WIDTH)
        ) counter (
            .clk(clk),
            .rst(bin_count_rst),
            .en(bin_count_en_i),
            .count(bin_count_rd_data_i)
        );
    end
endgenerate

mux_param #(
    .NUM_INPUT(BIN_COUNT_NUM_ENTRY),
    .SEL_WIDTH(BIN_COUNT_ADDR_WIDTH),
    .DATA_WIDTH(BIN_COUNT_DATA_WIDTH)
) bin_count_mux (
    .data_in(bin_count_rd_data),
    .sel(bin_count_rd_addr),
    .data_out(bin_count_mux_out)
);

always @(posedge clk) begin
    selected_bin_count <= bin_count_mux_out;
end

always @(posedge clk) begin
    if (rst) begin
        bin_count_mem_valid  <= 0;
        bin_count_mem_roi_sel <= {BIN_COUNT_NUM_ENTRY{1'b1}};
    end
    else if (process_result & bin_count_finish_condition) begin
        bin_count_mem_valid  <= 0;
        bin_count_mem_roi_sel <= bin_count_mem_roi_sel;
    end
    else if (valid_in) begin
        bin_count_mem_valid[bin_count_addr] <= 1;
        bin_count_mem_roi_sel <= bin_count_mem_roi_sel;
    end
    else begin
        bin_count_mem_valid <= bin_count_mem_valid;
        bin_count_mem_roi_sel <= bin_count_mem_roi_sel;
    end
end

assign bin_count_finish_condition = (bin_count_rd_addr >= BIN_COUNT_NUM_ENTRY-1) ? 1'b1 : 1'b0;
assign cur_bin_count_mem_roi_sel = bin_count_mem_roi_sel[bin_count_rd_addr];
assign cur_bin_count_mem_valid = bin_count_mem_valid[bin_count_rd_addr];
assign count_condition = cur_bin_count_mem_roi_sel & cur_bin_count_mem_valid;
assign next_bin_count = count_condition ? bin_count_sum + bin_count_mem_rd_data : bin_count_sum;
assign meas_result_condition = (bin_count_sum >= NUM_THRESHOLD) ? 1'b1 : 1'b0;

always @(posedge clk) begin
    if (rst) begin
        process_result <= 0;
        bin_count_rd_addr <= 0;
        valid_meas_result <= 0;
        meas_result <= 0;
        bin_count_sum <= 0;
    end
    else begin
        if (process_result) begin
            if (bin_count_finish_condition) begin
                process_result <= 0;
                bin_count_rd_addr <= 0;
                valid_meas_result <= 1;
                meas_result <= meas_result_condition;
                bin_count_sum <= 0;
            end
            else begin
                process_result <= 1;
                bin_count_rd_addr <= bin_count_rd_addr +1;
                valid_meas_result <= 0;
                meas_result <= meas_result_condition;
                bin_count_sum <= next_bin_count;
            end
        end
        else begin // ~process_result
            if (finish_count) begin
                process_result <= 1;
                bin_count_rd_addr <= 0;
                valid_meas_result <= 0;
                meas_result <= 0;
                bin_count_sum <= 0;
            end
            else begin
                process_result <= 0;
                bin_count_rd_addr <= 0;
                valid_meas_result <= 0;
                meas_result <= 0;
                bin_count_sum <= 0;
            end
        end
    end
end

assign valid_meas_result_out = valid_meas_result;
assign meas_result_out = meas_result;



endmodule