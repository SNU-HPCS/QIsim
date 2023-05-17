`timescale 1ns/100ps

module drive_z_corr_table_tb();

parameter NUM_BANK = 2;
parameter NUM_QUBIT_PER_BANK = 2;
parameter QUBIT_ADDR_WIDTH_PER_BANK = 1;
parameter Z_CORR_WIDTH = 4;

localparam TOTAL_QUBIT = NUM_QUBIT_PER_BANK * NUM_BANK;
localparam NUM_ENTRY = NUM_QUBIT_PER_BANK;
localparam ADDR_WIDTH = QUBIT_ADDR_WIDTH_PER_BANK;
localparam DATA_WIDTH = Z_CORR_WIDTH * TOTAL_QUBIT;

reg                               clk;
reg                               rst;
    
reg   [NUM_BANK-1:0]              z_corr_memory_wr_sel;
reg                               z_corr_memory_wr_en;
reg   [ADDR_WIDTH-1:0]            z_corr_memory_wr_addr;
reg   [DATA_WIDTH-1:0]            z_corr_memory_wr_data;

reg   [NUM_BANK*ADDR_WIDTH-1:0]   qubit_sel;
reg   [NUM_BANK-1:0]              local_is_read_env_fin;

wire  [DATA_WIDTH-1:0]            z_corr_out;

reg   [NUM_BANK*DATA_WIDTH-1:0]   rom_memory_0 [0:NUM_ENTRY-1];
reg   [NUM_BANK*DATA_WIDTH-1:0]   rom_memory_1 [0:NUM_ENTRY-1];


drive_z_corr_table #(
    .NUM_BANK(NUM_BANK),
    .NUM_QUBIT_PER_BANK(NUM_QUBIT_PER_BANK),
    .QUBIT_ADDR_WIDTH_PER_BANK(QUBIT_ADDR_WIDTH_PER_BANK),
    .Z_CORR_WIDTH(Z_CORR_WIDTH)
) UUT (
    .clk(clk),
    .rst(rst),
    .z_corr_memory_wr_sel(z_corr_memory_wr_sel),
    .z_corr_memory_wr_en(z_corr_memory_wr_en),
    .z_corr_memory_wr_addr(z_corr_memory_wr_addr),
    .z_corr_memory_wr_data(z_corr_memory_wr_data),
    .qubit_sel(qubit_sel),
    .local_is_read_env_fin(local_is_read_env_fin),
    .z_corr_out(z_corr_out)
);

integer I, J;

always #10 clk = ~clk;

initial begin
    $dumpfile("drive_z_corr_table.vcd");
    $dumpvars(0, drive_z_corr_table_tb);

    clk = 1'b0;
    rst = 1'b0;

    z_corr_memory_wr_sel = 0;
    z_corr_memory_wr_en = 0;
    z_corr_memory_wr_addr = 0;
    z_corr_memory_wr_data = 0;
    qubit_sel = 0;
    local_is_read_env_fin = 0;

    #5;
    rst = 1;
    #10;
    rst = 0;
    #5;
    
    // initialize z_corr_table
    for (I=0; I<NUM_BANK; I=I+1)
    begin
        for (J=0; J<NUM_QUBIT_PER_BANK; J=J+1)
        begin
            if (I == 0) z_corr_memory_wr_sel = 2'b01;
            else if (I == 1) z_corr_memory_wr_sel = 2'b10;
            else z_corr_memory_wr_sel = 2'b00;

            z_corr_memory_wr_en = 1;
            z_corr_memory_wr_addr = J;
            
            if (I == 0) begin
                z_corr_memory_wr_data = rom_memory_0[J];
            end
            else begin
                z_corr_memory_wr_data = rom_memory_1[J];
            end

            #20;
            
        end
    end
    z_corr_memory_wr_sel = 0;
    z_corr_memory_wr_en = 0;
    z_corr_memory_wr_addr = 0;
    z_corr_memory_wr_data = 0;

    // read z_corr_memory
    qubit_sel = 0;
    local_is_read_env_fin = 0;

    for (I=0; I<NUM_ENTRY; I=I+1)
    begin
        qubit_sel = {NUM_BANK{I[ADDR_WIDTH-1:0]}};

        local_is_read_env_fin = 2'b00;
        #40;

        if (I[0] == 0) begin
            local_is_read_env_fin = 2'b01;
        end
        else begin
            local_is_read_env_fin = 2'b10;
        end
        #20;

        local_is_read_env_fin = 2'b11;
        #20;


        // if (PC == I) $display("PASS: PC == %d, ANS == %d", PC, I);
        // else $display("FAIL: PC == %d, ANS == %d", PC, I);

    end
    
    #20;
    $finish;
end

// memory initialization
initial begin
    $readmemh("z_corr_table_n2_16b_0.mem", rom_memory_0, 0, NUM_ENTRY-1);
    $readmemh("z_corr_table_n2_16b_1.mem", rom_memory_1, 0, NUM_ENTRY-1);
end    

endmodule

/* Expected result */
/*
Cycle: 0 -> z_corr_out = 0x9999
Cycle: 1 -> z_corr_out = 0x9999
Cycle: 2 -> z_corr_out = 0x8888
Cycle: 3 -> z_corr_out = 0x0000

Cycle: 4 -> z_corr_out = 0x9999
Cycle: 5 -> z_corr_out = 0x9999
Cycle: 6 -> z_corr_out = 0x2222
Cycle: 7 -> z_corr_out = 0x0000
*/