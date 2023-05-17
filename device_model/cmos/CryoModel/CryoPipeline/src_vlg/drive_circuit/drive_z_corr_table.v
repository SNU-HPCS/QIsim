module drive_z_corr_table #(
    parameter NUM_BANK = 2,
	parameter NUM_QUBIT_PER_BANK = 16,
    parameter QUBIT_ADDR_WIDTH_PER_BANK = 4,
    parameter Z_CORR_WIDTH = 12
)(
    clk,
    rst,
    z_corr_memory_wr_sel,
    z_corr_memory_wr_en,
    z_corr_memory_wr_addr,
    z_corr_memory_wr_data,

    qubit_sel,
    is_read_env_fin,

    z_corr_out,

    valid_inst_list_in,
    phase_imm_in,
    rz_mode_in,
    
    rz_mode_out,
    valid_z_corr_out,

    z_corr_memory_rd_addr_out,
    z_corr_memory_rd_data_in
);

localparam TOTAL_QUBIT = NUM_QUBIT_PER_BANK * NUM_BANK;
localparam NUM_ENTRY = NUM_QUBIT_PER_BANK;
localparam ADDR_WIDTH = QUBIT_ADDR_WIDTH_PER_BANK;
localparam DATA_WIDTH = Z_CORR_WIDTH * TOTAL_QUBIT;

localparam MUX_NUM_INPUT = 2;
localparam MUX_SEL_WIDTH = 1;

// Port declaration
input                                   clk;
input                                   rst;
    
input       [NUM_BANK-1:0]              z_corr_memory_wr_sel;
input                                   z_corr_memory_wr_en;
input       [ADDR_WIDTH-1:0]            z_corr_memory_wr_addr;
input       [DATA_WIDTH-1:0]            z_corr_memory_wr_data;

input       [NUM_BANK*ADDR_WIDTH-1:0]   qubit_sel;
input       [NUM_BANK-1:0]              is_read_env_fin;

output      [DATA_WIDTH-1:0]            z_corr_out;

input       [NUM_BANK-1:0]              valid_inst_list_in;
input       [NUM_BANK*Z_CORR_WIDTH-1:0] phase_imm_in;
input       [NUM_BANK-1:0]              rz_mode_in;

output      [NUM_BANK-1:0]              rz_mode_out;
output      [NUM_BANK-1:0]              valid_z_corr_out;

output [NUM_BANK*ADDR_WIDTH-1:0] z_corr_memory_rd_addr_out;
input  [NUM_BANK*DATA_WIDTH-1:0] z_corr_memory_rd_data_in; 

//

reg         [NUM_BANK*DATA_WIDTH-1:0]   selected_z_corr;
wire        [NUM_BANK*DATA_WIDTH-1:0]   selected_z_corr_out;
reg         [DATA_WIDTH-1:0]            z_corr;

reg         [NUM_BANK*Z_CORR_WIDTH-1:0] phase_imm_0_2;
reg         [NUM_BANK*Z_CORR_WIDTH-1:0] phase_imm_1_2;
reg         [NUM_BANK*Z_CORR_WIDTH-1:0] phase_imm_2_2;

reg [NUM_BANK-1:0] read_z_corr_table_0_0;
reg [NUM_BANK-1:0] valid_z_corr_mem;
reg [NUM_BANK-1:0] valid_z_corr_mux;
reg [NUM_BANK-1:0] valid_z_corr;

reg [NUM_BANK-1:0] rz_mode_0_3;
reg [NUM_BANK-1:0] rz_mode_1_3;
reg [NUM_BANK-1:0] rz_mode_2_3;
reg [NUM_BANK-1:0] rz_mode_3_3;

genvar i;
// /*
generate
    for(i = 0; i < NUM_BANK; i = i +1) begin: genblk_z_corr_table
        wire                  z_corr_memory_wr_en_i;
        wire [ADDR_WIDTH-1:0] z_corr_memory_rd_addr_i;
        wire [DATA_WIDTH-1:0] z_corr_memory_rd_data_out_i;
        wire [DATA_WIDTH-1:0] selected_z_corr_i;
        wire                  is_read_env_fin_i;
        wire                  valid_inst_list_in_i;
        wire                  read_z_corr_table_0_0_i;

        reg  [DATA_WIDTH-1:0] z_corr_memory_rd_data_i;

        assign is_read_env_fin_i = is_read_env_fin[i];
        assign valid_inst_list_in_i = valid_inst_list_in[i];
        assign z_corr_memory_wr_en_i   = z_corr_memory_wr_en & z_corr_memory_wr_sel[i];
        assign z_corr_memory_rd_addr_i = qubit_sel[i*ADDR_WIDTH +: ADDR_WIDTH];
        assign read_z_corr_table_0_0_i = read_z_corr_table_0_0[i];
        
        /*
        random_access_mem #(
            .NUM_ENTRY(NUM_ENTRY),
            .ADDR_WIDTH(ADDR_WIDTH),
            .DATA_WIDTH(DATA_WIDTH)
        ) z_corr_table (
            .clk(clk),
            .wr_en(z_corr_memory_wr_en_i),
            .wr_data(z_corr_memory_wr_data),
            .wr_addr(z_corr_memory_wr_addr),
            .rd_addr(z_corr_memory_rd_addr_i),
            .rd_data(z_corr_memory_rd_data_i)
        );
        */
        
        /*
        wire z_corr_csb0, z_corr_web0;
        wire [ADDR_WIDTH-1:0] z_corr_addr0;
        assign z_corr_csb0 = ~(valid_inst_list_in_i || z_corr_memory_wr_en_i);
        assign z_corr_web0 = ~z_corr_memory_wr_en_i;
        assign z_corr_addr0 = z_corr_web0 ? z_corr_memory_rd_addr_i : z_corr_memory_wr_addr;
        sram_1rw0r0w_param_freepdk45 #(
            .RAM_DEPTH(NUM_ENTRY),
            .ADDR_WIDTH(ADDR_WIDTH),
            .DATA_WIDTH(DATA_WIDTH)
        ) z_corr_table (
            .clk0(clk),
            .csb0(z_corr_csb0),
            .web0(z_corr_web0),
            .addr0(z_corr_addr0),
            .din0(z_corr_memory_wr_data),
            .dout0(z_corr_memory_rd_data_out_i)
        );
        */


        assign selected_z_corr_i = is_read_env_fin_i ? {DATA_WIDTH{1'b0}} : z_corr_memory_rd_data_i;
        assign selected_z_corr_out[i*DATA_WIDTH +: DATA_WIDTH] = selected_z_corr_i;

        always @(posedge clk) begin
            if (read_z_corr_table_0_0_i) begin
                z_corr_memory_rd_data_i <= z_corr_memory_rd_data_out_i;
            end
        end
        
        // /*
        assign z_corr_memory_rd_data_out_i = z_corr_memory_rd_data_in[i*DATA_WIDTH +: DATA_WIDTH];
        assign z_corr_memory_rd_addr_out[i*ADDR_WIDTH +: ADDR_WIDTH] = z_corr_memory_rd_addr_i;
        // */
    end
endgenerate
// */

always @(posedge clk) begin
    read_z_corr_table_0_0 <= valid_inst_list_in;
    valid_z_corr_mem <= read_z_corr_table_0_0;
    valid_z_corr_mux <= valid_z_corr_mem;

    phase_imm_0_2 <= phase_imm_in;
    phase_imm_1_2 <= phase_imm_0_2;
    phase_imm_2_2 <= phase_imm_1_2;

    rz_mode_0_3 <= rz_mode_in;  // read_z_corr_table_0_0
    rz_mode_1_3 <= rz_mode_0_3; // z_corr_memory_rd_data
    rz_mode_2_3 <= rz_mode_1_3; // selected_z_corr
end

generate
    for(i = 0; i < TOTAL_QUBIT; i = i +1) begin: genblk_z_corr_adder
        wire [Z_CORR_WIDTH-1:0] selected_z_corr_out_i;
        if (NUM_BANK == 2) begin: genblk_z_corr_adder_bank2
            assign selected_z_corr_out_i = selected_z_corr_out[(0*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH]
                                + selected_z_corr_out[(1*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH];
        end
        else if (NUM_BANK == 3) begin: genblk_z_corr_adder_bank3
            assign selected_z_corr_out_i = selected_z_corr_out[(0*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH]
                                + selected_z_corr_out[(1*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH]
                                + selected_z_corr_out[(2*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH];
        end
        else if (NUM_BANK == 4) begin: genblk_z_corr_adder_bank4
            assign selected_z_corr_out_i = selected_z_corr_out[(0*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH]
                                + selected_z_corr_out[(1*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH]
                                + selected_z_corr_out[(2*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH]
                                + selected_z_corr_out[(3*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH];
        end
        else if (NUM_BANK == 8) begin: genblk_z_corr_adder_bank8
            assign selected_z_corr_out_i = selected_z_corr_out[(0*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH]
                                + selected_z_corr_out[(1*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH]
                                + selected_z_corr_out[(2*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH]
                                + selected_z_corr_out[(3*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH]
                                + selected_z_corr_out[(4*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH]
                                + selected_z_corr_out[(5*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH]
                                + selected_z_corr_out[(6*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH]
                                + selected_z_corr_out[(7*DATA_WIDTH + i*Z_CORR_WIDTH) +: Z_CORR_WIDTH];
        end
        else begin: genblk_z_corr_adder_bank1 // assume NUM_BANK == 1
            assign selected_z_corr_out_i = selected_z_corr_out;
        end

        always @(posedge clk) begin
            selected_z_corr[i*Z_CORR_WIDTH +: Z_CORR_WIDTH] = selected_z_corr_out_i;
        end
    end
endgenerate

wire [DATA_WIDTH-1:0] z_corr_temp;
generate
    for(i = 0; i < NUM_BANK; i = i + 1) begin: genblk_phase_imm
        wire [NUM_QUBIT_PER_BANK*Z_CORR_WIDTH-1:0] z_corr_i;
        assign z_corr_i = {NUM_QUBIT_PER_BANK{phase_imm_2_2[i*Z_CORR_WIDTH +: Z_CORR_WIDTH]}};
        assign z_corr_temp[i*NUM_QUBIT_PER_BANK +: NUM_QUBIT_PER_BANK] = z_corr_i;
    end
endgenerate

always @(posedge clk) begin
    if (rz_mode_2_3) begin
        z_corr <= z_corr_temp;
    end
    else begin
        z_corr <= selected_z_corr;
    end
    rz_mode_3_3 <= rz_mode_2_3;
    valid_z_corr <= valid_z_corr_mux;
end

assign rz_mode_out = rz_mode_3_3;
assign valid_z_corr_out = valid_z_corr;
assign z_corr_out = z_corr;

endmodule
