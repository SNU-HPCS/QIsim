
`include "define_pulse_circuit.v"

module pulse_mask_decoder #(
    parameter MASK_WIDTH = 3,
    parameter GLB_COUNTER_WIDTH = 24,
    parameter INST_LIST_ADDR_WIDTH = 5,
    parameter INST_LIST_DATA_WIDTH = 26,
    parameter DIRECTION_WIDTH = 2
)(
    clk,
    rst,

    valid_in,
    mask_in,
    start_time_in,

    inst_list_wr_en,
    inst_list_wr_addr,
    inst_list_wr_data
);

/* Port declaration */
input                                   clk;
input                                   rst;

input                                   valid_in;
input   [MASK_WIDTH-1:0]                mask_in;
input   [GLB_COUNTER_WIDTH-1:0]         start_time_in;

output                                  inst_list_wr_en;
output  [INST_LIST_ADDR_WIDTH-1:0]      inst_list_wr_addr;
output  [INST_LIST_DATA_WIDTH-1:0]      inst_list_wr_data;

/* Wire/reg declaration */
wire                                    update_wr_addr;
wire                                    enable;
wire    [DIRECTION_WIDTH-1:0]           direction;
reg     [INST_LIST_ADDR_WIDTH-1:0]      cur_inst_list_wr_addr;
wire    [INST_LIST_ADDR_WIDTH-1:0]      next_inst_list_wr_addr;

assign enable = mask_in[DIRECTION_WIDTH];
assign direction = mask_in[DIRECTION_WIDTH-1:0];

assign update_wr_addr = valid_in & enable;

assign next_inst_list_wr_addr = update_wr_addr ? cur_inst_list_wr_addr + 1 : cur_inst_list_wr_addr;

always @(posedge clk) begin
    if (rst) begin
        cur_inst_list_wr_addr <= 0;
    end
    else begin
        cur_inst_list_wr_addr <= next_inst_list_wr_addr;
    end
end

assign inst_list_wr_en = update_wr_addr;
assign inst_list_wr_addr = cur_inst_list_wr_addr;
assign inst_list_wr_data = {start_time_in, direction};

endmodule
