module counter_param #(
    parameter COUNT_WIDTH = 4
)(
    clk, 
    rst,
    en,
    count
);

input clk, en, rst; 
output reg [COUNT_WIDTH-1:0] count;


always @(posedge clk)
begin
    if (rst)
        count <= 0;
    else
    begin
        if (en)
            count <= count + 1;
        else
            count <= count;
    end
end

endmodule
