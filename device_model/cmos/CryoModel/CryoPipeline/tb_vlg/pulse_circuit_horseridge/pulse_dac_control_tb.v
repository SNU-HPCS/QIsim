`timescale 1ns/100ps

module pulse_dac_control_tb();

parameter NUM_CHANNEL                       = 22;
parameter DC_VALUE_WIDTH                    = 12;
parameter PULSE_LENGTH_WIDTH                = 20;

reg                                         clk; 
reg                                         rst;
reg                                         default_dc_value_wr_en;
reg     [DC_VALUE_WIDTH*NUM_CHANNEL-1:0]    default_dc_value_wr_data;
reg                                         valid_dc_value_in;
reg     [DC_VALUE_WIDTH*NUM_CHANNEL-1:0]    dc_value_in;
reg     [PULSE_LENGTH_WIDTH-1:0]            length_in;

wire    [DC_VALUE_WIDTH*NUM_CHANNEL-1:0]    dc_value_out;
wire                                        valid_dc_value_out;

///

pulse_dac_control #(
    .NUM_CHANNEL(NUM_CHANNEL),
    .DC_VALUE_WIDTH(DC_VALUE_WIDTH),
    .PULSE_LENGTH_WIDTH(PULSE_LENGTH_WIDTH)
) UUT (
    .clk(clk),
    .rst(rst),
    .default_dc_value_wr_en(default_dc_value_wr_en),
    .default_dc_value_wr_data(default_dc_value_wr_data),
    .valid_dc_value_in(valid_dc_value_in),
    .dc_value_in(dc_value_in),
    .length_in(length_in),
    .dc_value_out(dc_value_out),
    .valid_dc_value_out(valid_dc_value_out)
);

integer I;
integer WAIT_DURATION;

always #10 clk = ~clk;

initial begin
    $dumpfile("pulse_dac_control.vcd");
    $dumpvars(0, pulse_dac_control_tb);

    clk = 1'b0;
    rst = 1'b0;
    
    // Manually reset input signals
    default_dc_value_wr_en = 0;
    valid_dc_value_in = 0;
    dc_value_in = 0;
    length_in = 0;

    #5;
    rst = 1;
    #10;
    rst = 0;
    #5;
    
    // initialize default dc_value
    default_dc_value_wr_en = 1'b1;
    #20;
    default_dc_value_wr_en = 1'b0;
    #20;

    
    // Test 1
    WAIT_DURATION = 16;
    valid_dc_value_in = 1;
    dc_value_in = {NUM_CHANNEL{12'hABC}};
    length_in = WAIT_DURATION;

    for (I = 0; I < WAIT_DURATION+8; I = I+1) begin
        #20;
        valid_dc_value_in = 0;
    end

    WAIT_DURATION = 0;
    valid_dc_value_in = 0;
    dc_value_in = 0;
    length_in = 0;
    #20;

    // Test 2
    WAIT_DURATION = 64;
    valid_dc_value_in = 1;
    dc_value_in = {NUM_CHANNEL{12'hDEF}};
    length_in = WAIT_DURATION;

    for (I = 0; I < WAIT_DURATION+8; I = I+1) begin
        #20;
        valid_dc_value_in = 0;
    end

    WAIT_DURATION = 0;
    valid_dc_value_in = 0;
    dc_value_in = 0;
    length_in = 0;
    #20;
    
    $finish;
end


genvar J;
generate
    for(J = 0; J < NUM_CHANNEL; J = J +1) begin: genblk_default_dc_value_wr_data
        initial begin
            default_dc_value_wr_data[J*DC_VALUE_WIDTH +: DC_VALUE_WIDTH] = J[DC_VALUE_WIDTH-1:0];
        end
    end
endgenerate

endmodule

/* Expected result */
/*
*/