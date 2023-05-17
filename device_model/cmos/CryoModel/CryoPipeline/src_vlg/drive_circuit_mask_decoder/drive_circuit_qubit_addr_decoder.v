// Drive circuit (based on Horse Ridge I)

`include "define_drive_circuit_mask_decoder.v"

module drive_circuit_qubit_addr_decoder #(
    parameter NUM_QUBIT = 32,
    parameter NUM_QUBIT_PER_BANK = 16,
    parameter NUM_BANK = 2,
    parameter BANK_ADDR_WIDTH = 1,

    parameter QUBIT_ADDR_WIDTH = 5,
    parameter QUBIT_ADDR_WIDTH_PER_BANK = 4,

    parameter START_TIME_WIDTH = 24,
    parameter PHASE_WIDTH = 12,
    parameter INST_WIDTH_PER_BANK = (START_TIME_WIDTH+QUBIT_ADDR_WIDTH+1+PHASE_WIDTH)
)(
    clk,
    rst,

    mask_in,

    valid_in,
    global_wr_en_in,
    start_time_in,
    z_corr_mode_in,
    phase_in,

    inst_out,
    inst_wr_en_out
);

// Port declaration
input                                               clk;
input                                               rst;

input   [NUM_QUBIT-1:0]                             mask_in;

input                                               valid_in;
input                                               global_wr_en_in;
input   [START_TIME_WIDTH-1:0]                      start_time_in;
input                                               z_corr_mode_in;
input   [PHASE_WIDTH-1:0]                           phase_in;

output  [INST_WIDTH_PER_BANK*NUM_BANK-1:0]          inst_out;
output  [NUM_BANK-1:0]                              inst_wr_en_out;

// Internal connections

reg [NUM_BANK-1:0] local_wr_en_y;
reg [QUBIT_ADDR_WIDTH_PER_BANK*NUM_BANK-1:0] qubit_addr;

genvar i;
integer j;
generate
    for(i = 0; i < NUM_BANK; i = i +1) begin: genblk_qubit_addr_decoder
        wire local_wr_en_y_i;
        assign local_wr_en_y_i = |mask_in[NUM_QUBIT_PER_BANK*i +: NUM_QUBIT_PER_BANK];
        
        always @(posedge clk) begin
            if (rst) begin
                local_wr_en_y[i] <= 0;
            end
            else if (valid_in) begin
                local_wr_en_y[i] <= local_wr_en_y_i;
            end
        end

        reg [QUBIT_ADDR_WIDTH_PER_BANK-1:0] qubit_addr_i;
        // /*
        always @(*) begin
            qubit_addr_i = 0;
            for(j = 0; j < NUM_QUBIT_PER_BANK; j = j +1) begin
                if (mask_in[NUM_QUBIT_PER_BANK*i + j])
                    qubit_addr_i = j;
            end
        end
        // */
        /*
        qubit_addr_i = (mask_in[NUM_QUBIT_PER_BANK*i +: ]

        )
        */

        always @(posedge clk) begin
            if (rst) begin
                qubit_addr[QUBIT_ADDR_WIDTH_PER_BANK*i +: QUBIT_ADDR_WIDTH_PER_BANK] <= 0;
            end
            else if (valid_in) begin
                qubit_addr[QUBIT_ADDR_WIDTH_PER_BANK*i +: QUBIT_ADDR_WIDTH_PER_BANK] <= qubit_addr_i;
            end
        end

        wire inst_wr_en_i;
        assign inst_wr_en_i = global_wr_en_in & local_wr_en_y[i];
        assign inst_wr_en_out[i] = inst_wr_en_i;

        wire [INST_WIDTH_PER_BANK-1:0] inst_out_i;
        assign inst_out_i = {start_time_in, i[BANK_ADDR_WIDTH-1:0], qubit_addr[QUBIT_ADDR_WIDTH_PER_BANK*i +: QUBIT_ADDR_WIDTH_PER_BANK], z_corr_mode_in, phase_in};
        
        assign inst_out[INST_WIDTH_PER_BANK*i +: INST_WIDTH_PER_BANK] = inst_out_i;
    end
endgenerate

endmodule
