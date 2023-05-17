module subtractor_param #(
    // Assume (DATA_IN_WIDTH+1) >= DATA_OUT_WIDTH
	parameter DATA_IN_WIDTH = 8,
	parameter DATA_OUT_WIDTH = 8,
    parameter DATA_INTERMEDIATE_WIDTH = DATA_IN_WIDTH+1,
    parameter TAKE_MSB       = 1
)(
    data_in_1,
    data_in_2,
    data_out
);

// localparam DATA_INTERMEDIATE_WIDTH = DATA_IN_WIDTH+1;

input       [DATA_IN_WIDTH-1:0]             data_in_1;
input       [DATA_IN_WIDTH-1:0]             data_in_2;
output reg  [DATA_OUT_WIDTH-1:0]            data_out;

wire        [DATA_INTERMEDIATE_WIDTH-1:0]   data_intermediate;

assign data_intermediate = {1'b0, data_in_1} - {1'b0, data_in_2};

always @(*) begin
    if (TAKE_MSB) begin
        data_out = data_intermediate[(DATA_INTERMEDIATE_WIDTH-1) -: DATA_OUT_WIDTH];
    end
    else begin
        data_out = data_intermediate[0 +: DATA_OUT_WIDTH];
    end
end

endmodule
