module moving_average_filter #(
    parameter DATA_WIDTH = 16,
    parameter NUM_OPERAND = 8, // power of 2
    parameter OPERAND_ADDR_WIDTH = 3
)(
    clk,
    rst,
    valid_in,
    data_in,
    valid_out,
    data_out
);

localparam NUM_STAGES = NUM_OPERAND-1;
localparam SCALE_AFTER_SUM = OPERAND_ADDR_WIDTH; // SCALE_AFTER_SUM <= OPERAND_ADDR_WIDTH, use SCALE_AFTER_SUM=0 for power validation
localparam DATA_INTERMEDIATE = DATA_WIDTH + SCALE_AFTER_SUM;
//
input  signed                     clk;
input  signed                     rst;
input  signed                     valid_in;
input  signed [DATA_WIDTH-1:0]    data_in;
output signed                     valid_out;
output signed [DATA_WIDTH-1:0]    data_out;

//
reg    signed [NUM_STAGES*DATA_INTERMEDIATE-1:0]    stage_regs;
reg    signed [NUM_STAGES-1:0]               valid_regs;

wire   signed [DATA_INTERMEDIATE-1:0]   data_in_scaled;
wire   signed [DATA_INTERMEDIATE-1:0]   data_out_before_scale;

//
assign data_in_scaled = (data_in >>> (OPERAND_ADDR_WIDTH-SCALE_AFTER_SUM));
assign data_out = (data_out_before_scale >> SCALE_AFTER_SUM);

always @(posedge clk) begin
    stage_regs[0 +: DATA_INTERMEDIATE] <= data_in_scaled;
    if (rst) valid_regs[0] <= 0;
    else valid_regs[0] <= valid_in;
end

genvar i;
generate
    for(i = 1; i < NUM_STAGES; i = i +1) begin: genblk_average_filter_reg
        always @(posedge clk) begin
            stage_regs[DATA_INTERMEDIATE*i +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*(i-1) +: DATA_INTERMEDIATE];
            if (rst) valid_regs[i] <= 0;
            else valid_regs[i] <= valid_regs[i-1];
        end
    end
endgenerate

generate
    if (NUM_OPERAND == 2) begin: genblk_avg_filter_adder_2
        reg [1*DATA_INTERMEDIATE-1:0]  intermediate_data_0;
        reg                     intermediate_valid_0;

        always @(posedge clk) begin
            intermediate_data_0 = data_in_scaled
                                + stage_regs[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE];
        end
        always @(posedge clk) begin
            if (rst) intermediate_valid_0 <= 0;
            else intermediate_valid_0 <= valid_regs[NUM_STAGES-1];
        end
        assign data_out_before_scale = intermediate_data_0;
        assign valid_out = intermediate_valid_0;
    end
    else if (NUM_OPERAND == 4) begin: genblk_avg_filter_adder_4
        reg [2*DATA_INTERMEDIATE-1:0]  intermediate_data_1;
        reg [1*DATA_INTERMEDIATE-1:0]  intermediate_data_0;
        reg                     intermediate_valid_1;
        reg                     intermediate_valid_0;

        always @(posedge clk) begin
            intermediate_data_1[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] <= data_in_scaled
                                                            + stage_regs[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE];
            intermediate_data_1[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE]
                                                            + stage_regs[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE];

            intermediate_data_0 <= intermediate_data_1[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] 
                                + intermediate_data_1[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
        end
        always @(posedge clk) begin
            if (rst) intermediate_valid_1 <= 0;
            else intermediate_valid_1 <= valid_regs[NUM_STAGES-1];
            if (rst) intermediate_valid_0 <= 0;
            else intermediate_valid_0 <= intermediate_valid_1;
        end
        assign data_out_before_scale = intermediate_data_0;
        assign valid_out = intermediate_valid_0;
    end
    else if (NUM_OPERAND == 8) begin: genblk_avg_filter_adder_8
        reg [4*DATA_INTERMEDIATE-1:0]  intermediate_data_2;
        reg [2*DATA_INTERMEDIATE-1:0]  intermediate_data_1;
        reg [1*DATA_INTERMEDIATE-1:0]  intermediate_data_0;
        reg                     intermediate_valid_2;
        reg                     intermediate_valid_1;
        reg                     intermediate_valid_0;
        always @(posedge clk) begin
            intermediate_data_2[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] <= data_in_scaled
                                                            + stage_regs[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE];
            intermediate_data_2[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE]
                                                            + stage_regs[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE];
            intermediate_data_2[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE]
                                                            + stage_regs[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE];
            intermediate_data_2[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE]
                                                            + stage_regs[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE];

            intermediate_data_1[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] <= intermediate_data_2[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_2[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
            intermediate_data_1[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE] <= intermediate_data_2[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_2[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE];

            intermediate_data_0 <= intermediate_data_1[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] 
                                + intermediate_data_1[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
        end
        always @(posedge clk) begin
            if (rst) intermediate_valid_2 <= 0;
            else intermediate_valid_2 <= valid_regs[NUM_STAGES-1];
            if (rst) intermediate_valid_1 <= 0;
            else intermediate_valid_1 <= intermediate_valid_2;
            if (rst) intermediate_valid_0 <= 0;
            else intermediate_valid_0 <= intermediate_valid_1;
        end
        assign data_out_before_scale = intermediate_data_0;
        assign valid_out = intermediate_valid_0;
    end
    else if (NUM_OPERAND == 16) begin: genblk_avg_filter_adder_16
        reg [8*DATA_INTERMEDIATE-1:0]  intermediate_data_3;
        reg [4*DATA_INTERMEDIATE-1:0]  intermediate_data_2;
        reg [2*DATA_INTERMEDIATE-1:0]  intermediate_data_1;
        reg [1*DATA_INTERMEDIATE-1:0]  intermediate_data_0;
        reg                     intermediate_valid_3;
        reg                     intermediate_valid_2;
        reg                     intermediate_valid_1;
        reg                     intermediate_valid_0;
        always @(posedge clk) begin
            intermediate_data_3[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] <= data_in_scaled
                                                            + stage_regs[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE]
                                                            + stage_regs[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE]
                                                            + stage_regs[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE]
                                                            + stage_regs[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE]
                                                            + stage_regs[DATA_INTERMEDIATE*8 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*9 +: DATA_INTERMEDIATE]
                                                            + stage_regs[DATA_INTERMEDIATE*10 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*11 +: DATA_INTERMEDIATE]
                                                            + stage_regs[DATA_INTERMEDIATE*12 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*13 +: DATA_INTERMEDIATE]
                                                            + stage_regs[DATA_INTERMEDIATE*14 +: DATA_INTERMEDIATE];

            intermediate_data_2[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] <= intermediate_data_3[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_3[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
            intermediate_data_2[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE] <= intermediate_data_3[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_3[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE];
            intermediate_data_2[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE] <= intermediate_data_3[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_3[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE];
            intermediate_data_2[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE] <= intermediate_data_3[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_3[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE];

            intermediate_data_1[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] <= intermediate_data_2[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_2[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
            intermediate_data_1[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE] <= intermediate_data_2[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_2[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE];

            intermediate_data_0 <= intermediate_data_1[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] 
                                + intermediate_data_1[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
        end
        always @(posedge clk) begin
            if (rst) intermediate_valid_3 <= 0;
            else intermediate_valid_3 <= valid_regs[NUM_STAGES-1];
            if (rst) intermediate_valid_2 <= 0;
            else intermediate_valid_2 <= intermediate_valid_3;
            if (rst) intermediate_valid_1 <= 0;
            else intermediate_valid_1 <= intermediate_valid_2;
            if (rst) intermediate_valid_0 <= 0;
            else intermediate_valid_0 <= intermediate_valid_1;
        end
        assign data_out_before_scale = intermediate_data_0;
        assign valid_out = intermediate_valid_0;
    end
    else if (NUM_OPERAND == 32) begin: genblk_avg_filter_adder_32
        reg [16*DATA_INTERMEDIATE-1:0] intermediate_data_4;
        reg [8*DATA_INTERMEDIATE-1:0]  intermediate_data_3;
        reg [4*DATA_INTERMEDIATE-1:0]  intermediate_data_2;
        reg [2*DATA_INTERMEDIATE-1:0]  intermediate_data_1;
        reg [1*DATA_INTERMEDIATE-1:0]  intermediate_data_0;
        reg                     intermediate_valid_4;
        reg                     intermediate_valid_3;
        reg                     intermediate_valid_2;
        reg                     intermediate_valid_1;
        reg                     intermediate_valid_0;
        always @(posedge clk) begin
            intermediate_data_4[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE]  <= data_in_scaled
                                                             + stage_regs[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*8 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*9 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*10 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*11 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*12 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*13 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*14 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*8 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*15 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*16 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*9 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*17 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*18 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*10 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*19 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*20 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*11 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*21 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*22 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*12 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*23 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*24 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*13 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*25 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*26 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*14 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*27 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*28 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*15 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*29 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*30 +: DATA_INTERMEDIATE];

            intermediate_data_3[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*8 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*9 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*10 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*11 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*12 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*13 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*14 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*15 +: DATA_INTERMEDIATE];

            intermediate_data_2[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] <= intermediate_data_3[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_3[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
            intermediate_data_2[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE] <= intermediate_data_3[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_3[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE];
            intermediate_data_2[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE] <= intermediate_data_3[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_3[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE];
            intermediate_data_2[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE] <= intermediate_data_3[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_3[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE];

            intermediate_data_1[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] <= intermediate_data_2[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_2[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
            intermediate_data_1[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE] <= intermediate_data_2[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_2[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE];

            intermediate_data_0 <= intermediate_data_1[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] 
                                + intermediate_data_1[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
        end
        always @(posedge clk) begin
            if (rst) intermediate_valid_4 <= 0;
            else intermediate_valid_4 <= valid_regs[NUM_STAGES-1];
            if (rst) intermediate_valid_3 <= 0;
            else intermediate_valid_3 <= intermediate_valid_4;
            if (rst) intermediate_valid_2 <= 0;
            else intermediate_valid_2 <= intermediate_valid_3;
            if (rst) intermediate_valid_1 <= 0;
            else intermediate_valid_1 <= intermediate_valid_2;
            if (rst) intermediate_valid_0 <= 0;
            else intermediate_valid_0 <= intermediate_valid_1;
        end
        assign data_out_before_scale = intermediate_data_0;
        assign valid_out = intermediate_valid_0;
    end
    else if (NUM_OPERAND == 64) begin: genblk_avg_filter_adder_64
        reg [32*DATA_INTERMEDIATE-1:0] intermediate_data_5;
        reg [16*DATA_INTERMEDIATE-1:0] intermediate_data_4;
        reg [8*DATA_INTERMEDIATE-1:0]  intermediate_data_3;
        reg [4*DATA_INTERMEDIATE-1:0]  intermediate_data_2;
        reg [2*DATA_INTERMEDIATE-1:0]  intermediate_data_1;
        reg [1*DATA_INTERMEDIATE-1:0]  intermediate_data_0;
        reg                     intermediate_valid_5;
        reg                     intermediate_valid_4;
        reg                     intermediate_valid_3;
        reg                     intermediate_valid_2;
        reg                     intermediate_valid_1;
        reg                     intermediate_valid_0;
        always @(posedge clk) begin
            intermediate_data_5[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE]  <= data_in_scaled
                                                             + stage_regs[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*8 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*9 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*10 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*11 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*12 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*13 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*14 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*8 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*15 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*16 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*9 +: DATA_INTERMEDIATE]  <= stage_regs[DATA_INTERMEDIATE*17 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*18 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*10 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*19 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*20 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*11 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*21 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*22 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*12 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*23 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*24 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*13 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*25 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*26 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*14 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*27 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*28 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*15 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*29 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*30 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*16 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*31 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*32 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*17 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*33 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*34 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*18 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*35 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*36 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*19 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*37 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*38 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*20 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*39 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*40 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*21 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*41 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*42 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*22 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*43 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*44 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*23 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*45 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*46 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*24 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*47 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*48 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*25 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*49 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*50 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*26 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*51 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*52 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*27 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*53 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*54 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*28 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*55 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*56 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*29 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*57 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*58 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*30 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*59 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*60 +: DATA_INTERMEDIATE];
            intermediate_data_5[DATA_INTERMEDIATE*31 +: DATA_INTERMEDIATE] <= stage_regs[DATA_INTERMEDIATE*61 +: DATA_INTERMEDIATE]
                                                             + stage_regs[DATA_INTERMEDIATE*62 +: DATA_INTERMEDIATE];

            intermediate_data_4[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE]  <= intermediate_data_5[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE]  <= intermediate_data_5[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE]  <= intermediate_data_5[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE]  <= intermediate_data_5[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE]  <= intermediate_data_5[DATA_INTERMEDIATE*8 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*9 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE]  <= intermediate_data_5[DATA_INTERMEDIATE*10 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*11 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE]  <= intermediate_data_5[DATA_INTERMEDIATE*12 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*13 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE]  <= intermediate_data_5[DATA_INTERMEDIATE*14 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*15 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*8 +: DATA_INTERMEDIATE]  <= intermediate_data_5[DATA_INTERMEDIATE*16 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*17 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*9 +: DATA_INTERMEDIATE]  <= intermediate_data_5[DATA_INTERMEDIATE*18 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*19 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*10 +: DATA_INTERMEDIATE] <= intermediate_data_5[DATA_INTERMEDIATE*20 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*21 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*11 +: DATA_INTERMEDIATE] <= intermediate_data_5[DATA_INTERMEDIATE*22 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*23 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*12 +: DATA_INTERMEDIATE] <= intermediate_data_5[DATA_INTERMEDIATE*24 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*25 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*13 +: DATA_INTERMEDIATE] <= intermediate_data_5[DATA_INTERMEDIATE*26 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*27 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*14 +: DATA_INTERMEDIATE] <= intermediate_data_5[DATA_INTERMEDIATE*28 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*29 +: DATA_INTERMEDIATE];
            intermediate_data_4[DATA_INTERMEDIATE*15 +: DATA_INTERMEDIATE] <= intermediate_data_5[DATA_INTERMEDIATE*30 +: DATA_INTERMEDIATE]
                                                             + intermediate_data_5[DATA_INTERMEDIATE*31 +: DATA_INTERMEDIATE];

            intermediate_data_3[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*8 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*9 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*10 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*11 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*12 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*13 +: DATA_INTERMEDIATE];
            intermediate_data_3[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE] <= intermediate_data_4[DATA_INTERMEDIATE*14 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_4[DATA_INTERMEDIATE*15 +: DATA_INTERMEDIATE];

            intermediate_data_2[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] <= intermediate_data_3[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_3[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
            intermediate_data_2[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE] <= intermediate_data_3[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_3[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE];
            intermediate_data_2[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE] <= intermediate_data_3[DATA_INTERMEDIATE*4 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_3[DATA_INTERMEDIATE*5 +: DATA_INTERMEDIATE];
            intermediate_data_2[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE] <= intermediate_data_3[DATA_INTERMEDIATE*6 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_3[DATA_INTERMEDIATE*7 +: DATA_INTERMEDIATE];

            intermediate_data_1[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] <= intermediate_data_2[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_2[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
            intermediate_data_1[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE] <= intermediate_data_2[DATA_INTERMEDIATE*2 +: DATA_INTERMEDIATE]
                                                            + intermediate_data_2[DATA_INTERMEDIATE*3 +: DATA_INTERMEDIATE];

            intermediate_data_0 <= intermediate_data_1[DATA_INTERMEDIATE*0 +: DATA_INTERMEDIATE] 
                                + intermediate_data_1[DATA_INTERMEDIATE*1 +: DATA_INTERMEDIATE];
        end
        always @(posedge clk) begin
            if (rst) intermediate_valid_5 <= 0;
            else intermediate_valid_5 <= valid_regs[NUM_STAGES-1];
            if (rst) intermediate_valid_4 <= 0;
            else intermediate_valid_4 <= intermediate_valid_5;
            if (rst) intermediate_valid_3 <= 0;
            else intermediate_valid_3 <= intermediate_valid_4;
            if (rst) intermediate_valid_2 <= 0;
            else intermediate_valid_2 <= intermediate_valid_3;
            if (rst) intermediate_valid_1 <= 0;
            else intermediate_valid_1 <= intermediate_valid_2;
            if (rst) intermediate_valid_0 <= 0;
            else intermediate_valid_0 <= intermediate_valid_1;
        end
        assign data_out_before_scale = intermediate_data_0;
        assign valid_out = intermediate_valid_0;
    end
    else begin: genblk_avg_filter_adder_1 // regard as "NUM_OPERAND == 1"
        assign data_out_before_scale = data_in_scaled;
    end
endgenerate

endmodule
