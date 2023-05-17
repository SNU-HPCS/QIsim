`define NUM_OUTPUT 15
`define SEL_WIDTH 4
`define DATA_WIDTH 4

module demux_param_tb ();

reg [`DATA_WIDTH-1:0] data_in;
reg [`SEL_WIDTH-1:0] sel;
wire [`DATA_WIDTH*`NUM_OUTPUT-1:0] data_out;

integer J;

demux_param #(
    .NUM_OUTPUT(`NUM_OUTPUT),
    .SEL_WIDTH(`SEL_WIDTH),
    .DATA_WIDTH(`DATA_WIDTH)
) UUT (
    .data_in(data_in),
    .sel(sel),
    .data_out(data_out)
);

initial begin
    $dumpfile("demux_param.vcd");
    $dumpvars(0, demux_param_tb);
    
    data_in = 10;
    
    sel = 0;
    for (J=0; J<`NUM_OUTPUT; J=J+1)
    begin
        #20;
        sel = J;
    end
    
    // Answer
    // For sel == J,
    // dataout[J*6+5:J*6] = 'hA
    
    #20;
    $finish;
end


endmodule

