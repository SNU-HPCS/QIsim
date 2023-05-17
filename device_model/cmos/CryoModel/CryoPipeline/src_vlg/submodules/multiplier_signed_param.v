module multiplier_signed_param #(
    // Assume (DATA_IN_WIDTH*2) >= DATA_OUT_WIDTH
	parameter DATA_IN_WIDTH = 8,
	parameter DATA_OUT_WIDTH = 8,
    parameter DATA_INTERMEDIATE_WIDTH = DATA_IN_WIDTH*2,
    parameter TAKE_MSB       = 1
)(
    data_in_1,
    data_in_2,
    data_out
);

// localparam DATA_INTERMEDIATE_WIDTH = DATA_IN_WIDTH*2;

input      signed [DATA_IN_WIDTH-1:0]             data_in_1;
input      signed [DATA_IN_WIDTH-1:0]             data_in_2;
output reg signed [DATA_OUT_WIDTH-1:0]            data_out;

wire       signed [DATA_INTERMEDIATE_WIDTH-1:0]    data_intermediate;

assign data_intermediate = {{(DATA_INTERMEDIATE_WIDTH-DATA_IN_WIDTH){data_in_1[DATA_IN_WIDTH-1]}}, data_in_1} 
                            * {{(DATA_INTERMEDIATE_WIDTH-DATA_IN_WIDTH){data_in_2[DATA_IN_WIDTH-1]}}, data_in_2};

always @(*) begin
    if (TAKE_MSB) begin
        data_out = data_intermediate[(DATA_INTERMEDIATE_WIDTH-1) -: DATA_OUT_WIDTH];
    end
    else begin
        data_out = data_intermediate[0 +: DATA_OUT_WIDTH];
    end
end

endmodule
