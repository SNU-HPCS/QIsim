module demux_param #(
    parameter NUM_OUTPUT = 8, 
    parameter SEL_WIDTH = 3,
    parameter DATA_WIDTH = 4
)(
    data_in, 
    sel,
    data_out
);

input [DATA_WIDTH-1:0] data_in;
input [SEL_WIDTH-1:0] sel;
output reg [DATA_WIDTH*NUM_OUTPUT-1:0] data_out;

integer I;

always @(*)
begin
    for (I=0; I<NUM_OUTPUT; I=I+1)
        if(sel == I)
            data_out[I*DATA_WIDTH +: DATA_WIDTH] = data_in;
        else
            data_out[I*DATA_WIDTH +: DATA_WIDTH] = 0;
    
end

endmodule
