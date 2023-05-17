`define NUM_INPUT 4
`define SEL_WIDTH 2
`define DATA_WIDTH 1

module mux_param_tb ();

reg [`DATA_WIDTH*`NUM_INPUT-1:0] data_in;
reg [`SEL_WIDTH-1:0] sel;
wire [`DATA_WIDTH-1:0] data_out;

integer I, J;

mux_param #(
    .NUM_INPUT(`NUM_INPUT),
    .SEL_WIDTH(`SEL_WIDTH),
    .DATA_WIDTH(`DATA_WIDTH)
) UUT (
    .data_in(data_in),
    .sel(sel),
    .data_out(data_out)
);

initial begin
    $dumpfile("mux_param.vcd");
    $dumpvars(0, mux_param_tb);
    
    for (I=0; I<`NUM_INPUT; I=I+1)
        data_in[I*`DATA_WIDTH +: `DATA_WIDTH] = I%2;
    
    sel = 0;
    for (J=0; J<`NUM_INPUT; J=J+1)
    begin
        #20;
        sel = J;
    end

    // Answer
    // for sel = J, data_out = 0 (J:even) or 1 (J:odd)
    
    #20;
    $finish;
end


endmodule

