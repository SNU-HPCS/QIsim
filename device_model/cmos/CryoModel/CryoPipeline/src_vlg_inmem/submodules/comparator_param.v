module comparator_param #(
	parameter DATA_WIDTH = 8
)(
    data_in_1, 
    data_in_2, 
    data_out // 1 if data_in_1 > data_in_2
);

input signed [DATA_WIDTH-1:0] data_in_1;
input signed [DATA_WIDTH-1:0] data_in_2;
output [0:0] data_out;

assign data_out = (data_in_1 > data_in_2) ? 1'b1 : 1'b0;

endmodule
