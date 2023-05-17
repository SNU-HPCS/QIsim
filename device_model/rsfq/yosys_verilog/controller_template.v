`include "define.v"

`define BS                  **BS                // Number of bitstream broadcasted at once; 8.
`define NUM_BS              **NUM_BS            // Number of bitstreams in group; 256.
`define BS_SELECT           `log2(`BS)            // Bitstream select bits (log2 (BS)); 3.
`define NUM_BS_SELECT       `log2(`NUM_BS)        // Bitstream select bits (log2 (NUM_BS)); 8.


// Controller.
module controller_param (bs_in, bs_select, bs_out);

input [`NUM_BS-1:0] bs_in;
input [`NUM_BS_SELECT*`BS-1:0] bs_select;
output [`BS-1:0] bs_out;

genvar i1;
generate
    for (i1 = 0; i1 < `BS; i1 = i1+1) begin
        wire [`NUM_BS_SELECT-1:0] select;
        assign select = bs_select[`NUM_BS_SELECT*i1 +: `NUM_BS_SELECT];
        assign bs_out[i1] = bs_in[select];
    end
endgenerate

endmodule
