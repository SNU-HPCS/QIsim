module moving_average_filter_4operand #(
    parameter DATA_WIDTH = 8,
    parameter NUM_OPERAND = 4, // power of 2
    parameter OPERAND_ADDR_WIDTH = 2
)(
    clk,
    rst,
    valid_in,
    data_in,
    valid_out,
    data_out
);

localparam NUM_STAGES = NUM_OPERAND-1;
//
input                             clk;
input                             rst;
input                             valid_in;
input  signed [DATA_WIDTH-1:0]    data_in;
output                            valid_out;
output signed [DATA_WIDTH-1:0]    data_out;

//
reg    signed [NUM_STAGES*DATA_WIDTH-1:0]    stage_regs;
reg           [NUM_STAGES-1:0]               valid_regs;

wire   signed [DATA_WIDTH-1:0]    data_in_scaled;

//
assign data_in_scaled = (data_in >>> OPERAND_ADDR_WIDTH);

always @(posedge clk) begin
    if (rst) valid_regs[0] <= 0;
    else valid_regs[0] <= valid_in;

    valid_regs[1] <= valid_regs[0];
    valid_regs[2] <= valid_regs[1];

    stage_regs[DATA_WIDTH*(0) +: DATA_WIDTH] <= data_in_scaled;
    stage_regs[DATA_WIDTH*(1) +: DATA_WIDTH] <= stage_regs[DATA_WIDTH*(0) +: DATA_WIDTH];
    stage_regs[DATA_WIDTH*(2) +: DATA_WIDTH] <= stage_regs[DATA_WIDTH*(1) +: DATA_WIDTH];
end


reg [2*DATA_WIDTH-1:0]  intermediate_data_1;
reg signed [1*DATA_WIDTH-1:0]  intermediate_data_0;
reg                     intermediate_valid_1;
reg                     intermediate_valid_0;

always @(posedge clk) begin
    intermediate_data_1[DATA_WIDTH*0 +: DATA_WIDTH] <= data_in_scaled
                                                    + stage_regs[DATA_WIDTH*0 +: DATA_WIDTH];
    intermediate_data_1[DATA_WIDTH*1 +: DATA_WIDTH] <= stage_regs[DATA_WIDTH*1 +: DATA_WIDTH]
                                                    + stage_regs[DATA_WIDTH*2 +: DATA_WIDTH];

    intermediate_data_0 <= intermediate_data_1[DATA_WIDTH*0 +: DATA_WIDTH] 
                        + intermediate_data_1[DATA_WIDTH*1 +: DATA_WIDTH];
end
always @(posedge clk) begin
    if (rst) intermediate_valid_1 <= 0;
    else intermediate_valid_1 <= valid_regs[NUM_STAGES-1];
    if (rst) intermediate_valid_0 <= 0;
    else intermediate_valid_0 <= intermediate_valid_1;
end
assign data_out = intermediate_data_0;
assign valid_out = intermediate_valid_0;

endmodule
