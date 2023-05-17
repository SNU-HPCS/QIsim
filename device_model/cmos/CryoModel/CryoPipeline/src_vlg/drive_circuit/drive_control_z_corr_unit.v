`define WAITING 0
`define RUNNING 1

module drive_control_z_corr_unit # (
    parameter NUM_QUBIT_PER_BANK = 16,
    parameter QUBIT_ADDR_WIDTH_PER_BANK = 4
)
(
    clk,
    rst,
    valid_inst_table_in,
    glb_is_read_env_fin,
    local_is_read_env_fin,

    qubit_sel,

    nco_z_corr_wr_en,
    nco_phase_wr_en,
    nco_z_corr_mode
);

// Port declaration
input                                       clk;
input                                       rst;
input                                       valid_inst_table_in;
input                                       glb_is_read_env_fin; // glb_is_read_env_fin
input                                       local_is_read_env_fin; // glb_is_read_env_fin
input       [QUBIT_ADDR_WIDTH_PER_BANK-1:0] qubit_sel;


output reg  [NUM_QUBIT_PER_BANK-1:0]        nco_z_corr_wr_en;
output reg  [NUM_QUBIT_PER_BANK-1:0]        nco_phase_wr_en;
output reg  [NUM_QUBIT_PER_BANK-1:0]        nco_z_corr_mode;

// 
/*
reg                                         state;

always @(posedge clk) begin
    if (rst) begin
        state <= `WAITING;
        nco_z_corr_wr_en <= {NUM_QUBIT_PER_BANK{1'b1}};
        // nco_phase_wr_en <= {NUM_QUBIT_PER_BANK{1'b0}};
        nco_z_corr_mode <= {NUM_QUBIT_PER_BANK{1'b1}};
    end
    else begin
        if (state == `WAITING) begin
            if (valid_inst_table_in) begin
                state <= `RUNNING;
                nco_z_corr_wr_en <= {NUM_QUBIT_PER_BANK{1'b1}};
                // nco_phase_wr_en <= {NUM_QUBIT_PER_BANK{1'b1}}; // start NCO accumulation
                nco_z_corr_mode[qubit_sel] <= 1'b0;
            end
            else begin
                state <= `WAITING;
                nco_z_corr_wr_en <= {NUM_QUBIT_PER_BANK{1'b1}};
                // nco_phase_wr_en <= {NUM_QUBIT_PER_BANK{1'b0}};
                nco_z_corr_mode <= {NUM_QUBIT_PER_BANK{1'b1}};
            end
        end
        else begin
            if (glb_is_read_env_fin) begin
                state <= `WAITING;
                nco_z_corr_wr_en <= {NUM_QUBIT_PER_BANK{1'b1}};
                // nco_phase_wr_en <= {NUM_QUBIT_PER_BANK{1'b0}};
                nco_z_corr_mode <= {NUM_QUBIT_PER_BANK{1'b1}};
            end
            else begin
                state <= `RUNNING;
                nco_z_corr_wr_en <= {NUM_QUBIT_PER_BANK{1'b1}};
                // nco_phase_wr_en <= {NUM_QUBIT_PER_BANK{1'b1}}; // NCO accumulation
                nco_z_corr_mode[qubit_sel] <= 1'b0;
            end
        end
    end
end
*/
integer i;
always @(posedge clk) begin
    // nco_phase_wr_en
    if (glb_is_read_env_fin) begin
        nco_phase_wr_en <= {NUM_QUBIT_PER_BANK{1'b0}};
    end
    else begin
        nco_phase_wr_en <= {NUM_QUBIT_PER_BANK{1'b1}};
    end
    
    // nco_z_corr_mode
    // nco_z_corr_mode = (~glb_is_read_env_fin) & (local_is_read_env_fin);
    for(i = 0; i < NUM_QUBIT_PER_BANK; i = i +1) begin
        if (i == qubit_sel) begin
            nco_z_corr_mode[i] = (~glb_is_read_env_fin) & (local_is_read_env_fin);
        end
        else begin
            nco_z_corr_mode[i] = 1'b1;
        end
    end

    nco_z_corr_wr_en <= {NUM_QUBIT_PER_BANK{1'b1}};
end
endmodule
