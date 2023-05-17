module readout_rx_pc #(
	parameter PC_WIDTH = 11
)(
    clk,
    rst,
    update_pc,
    next_PC,
    PC
);

// Port declaration
input                       clk;
input                       rst;
input                       update_pc;
input       [PC_WIDTH-1:0]  next_PC;

output reg  [PC_WIDTH-1:0]  PC;

// reg enable; // Do not update PC at first cycle

always @(posedge clk) begin
    if (rst) begin
        // enable <= 0;
        PC <= 0;
    end
    else begin
        if (update_pc) begin
            PC <= next_PC;
            // if (enable) begin
            //     PC <= next_PC;
            // end
            // enable <= 1;
        end
    end
end

endmodule
