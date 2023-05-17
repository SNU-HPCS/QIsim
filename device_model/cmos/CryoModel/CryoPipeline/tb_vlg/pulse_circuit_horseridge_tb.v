`timescale 1ns/100ps

module pulse_circuit_horseridge_tb();

parameter NUM_CHANNEL                       = 22;

parameter GLB_COUNTER_WIDTH                 = 24;

// inst_list
parameter INST_LIST_NUM_ENTRY               = 2048;
parameter INST_LIST_ADDR_WIDTH              = 11;
parameter INST_LIST_DATA_WIDTH              = 35; 

// pulse_memory
parameter PULSE_MEMORY_NUM_BANK             = 4;
parameter PULSE_MEMORY_BANK_ADDR_WIDTH      = 2; // log2(PULSE_MEMORY_NUM_BANK)
parameter PULSE_MEMORY_NUM_ENTRY_PER_BANK   = 512;
parameter PULSE_MEMORY_ADDR_WIDTH_PER_BANK  = 9;
parameter PULSE_MEMORY_DATA_WIDTH_PER_BANK  = 284; // DC_VALUE_WIDTH*NUM_CHANNEL+PULSE_LENGTH_WIDTH
parameter DC_VALUE_WIDTH                    = 12;
parameter PULSE_LENGTH_WIDTH                = 20;

reg                                                 clk; 
reg                                                 rst;
reg       [GLB_COUNTER_WIDTH-1:0]                   glb_counter;

// inst_list
reg                                                 inst_list_wr_en;
reg       [INST_LIST_ADDR_WIDTH-1:0]                inst_list_wr_addr;
reg       [INST_LIST_DATA_WIDTH-1:0]                inst_list_wr_data;

// pulse_memory
reg       [PULSE_MEMORY_BANK_ADDR_WIDTH-1:0]        pulse_memory_wr_sel;
reg                                                 pulse_memory_wr_en;
reg       [PULSE_MEMORY_ADDR_WIDTH_PER_BANK-1:0]    pulse_memory_wr_addr;
reg       [PULSE_MEMORY_DATA_WIDTH_PER_BANK-1:0]    pulse_memory_wr_data;
 
// dac_control
reg                                                 default_dc_value_wr_en;
reg       [DC_VALUE_WIDTH*NUM_CHANNEL-1:0]          default_dc_value_wr_data;

wire      [DC_VALUE_WIDTH*NUM_CHANNEL-1:0]          dc_value_out;
wire                                                valid_dc_value_out;

///
// localparam NUM_ITER_INIT  = 2048;
localparam NUM_ITER_INIT  = 2080;
localparam NUM_ITER_TEST1 = 256;
localparam NUM_ITER_TEST2 = 512;

reg [INST_LIST_DATA_WIDTH-1:0]                      inst_list_mem [0:INST_LIST_NUM_ENTRY-1];
reg [PULSE_MEMORY_DATA_WIDTH_PER_BANK-1:0]          pulse_mem [0:PULSE_MEMORY_NUM_ENTRY_PER_BANK*PULSE_MEMORY_NUM_BANK-1];


// pulse_circuit #(
pulse_circuit_horseridge #(
    .NUM_CHANNEL(NUM_CHANNEL),
    .GLB_COUNTER_WIDTH(GLB_COUNTER_WIDTH),
    .INST_LIST_NUM_ENTRY(INST_LIST_NUM_ENTRY),
    .INST_LIST_ADDR_WIDTH(INST_LIST_ADDR_WIDTH),
    .INST_LIST_DATA_WIDTH(INST_LIST_DATA_WIDTH),
    .PULSE_MEMORY_NUM_BANK(PULSE_MEMORY_NUM_BANK),
    .PULSE_MEMORY_BANK_ADDR_WIDTH(PULSE_MEMORY_BANK_ADDR_WIDTH),
    .PULSE_MEMORY_NUM_ENTRY_PER_BANK(PULSE_MEMORY_NUM_ENTRY_PER_BANK),
    .PULSE_MEMORY_ADDR_WIDTH_PER_BANK(PULSE_MEMORY_ADDR_WIDTH_PER_BANK),
    .PULSE_MEMORY_DATA_WIDTH_PER_BANK(PULSE_MEMORY_DATA_WIDTH_PER_BANK),
    .DC_VALUE_WIDTH(DC_VALUE_WIDTH),
    .PULSE_LENGTH_WIDTH(PULSE_LENGTH_WIDTH)
) UUT (
    .clk(clk),
    .rst(rst),
    .glb_counter(glb_counter), 
    .inst_list_wr_en(inst_list_wr_en),
    .inst_list_wr_addr(inst_list_wr_addr),
    .inst_list_wr_data(inst_list_wr_data),
    .pulse_memory_wr_sel(pulse_memory_wr_sel),
    .pulse_memory_wr_en(pulse_memory_wr_en),
    .pulse_memory_wr_addr(pulse_memory_wr_addr),
    .pulse_memory_wr_data(pulse_memory_wr_data),
    .default_dc_value_wr_en(default_dc_value_wr_en),
    .default_dc_value_wr_data(default_dc_value_wr_data),
    .dc_value_out(dc_value_out),
    .valid_dc_value_out(valid_dc_value_out)
);

integer I;
integer WAIT_DURATION;

always #10 clk = ~clk;

initial begin
    $dumpfile("pulse_circuit_horseridge.vcd");
    $dumpvars(0, pulse_circuit_horseridge_tb);

    clk = 1'b0;
    rst = 1'b0;
    
    // Manually reset reg signals
    default_dc_value_wr_en = 0;
    glb_counter = 0;

    #5;
    rst = 1;
    #10;
    rst = 0;
    #5;
    
    // initialize default dc_value
    default_dc_value_wr_en = 1'b1;
    #20;
    default_dc_value_wr_en = 1'b0;
    #20;

    // initialize memory

    for (I=0; I< NUM_ITER_INIT; I=I+1) begin
        // inst_list
        if (I < INST_LIST_NUM_ENTRY) begin
            inst_list_wr_en = 1'b1;
            inst_list_wr_addr = I[INST_LIST_ADDR_WIDTH-1:0];
            
            inst_list_wr_data = inst_list_mem[inst_list_wr_addr];
        end
        else begin
            inst_list_wr_en = 1'b0;
            inst_list_wr_addr = 0;
            inst_list_wr_data = 0;
        end
        
        // inst_table
        if (I < PULSE_MEMORY_NUM_ENTRY_PER_BANK * PULSE_MEMORY_NUM_BANK) begin
            pulse_memory_wr_en = 1'b1;
            pulse_memory_wr_sel = I[PULSE_MEMORY_ADDR_WIDTH_PER_BANK +: PULSE_MEMORY_BANK_ADDR_WIDTH];
            pulse_memory_wr_addr = I[0 +: PULSE_MEMORY_ADDR_WIDTH_PER_BANK];
            pulse_memory_wr_data = pulse_mem[I[0 +: (PULSE_MEMORY_ADDR_WIDTH_PER_BANK+PULSE_MEMORY_BANK_ADDR_WIDTH)]];
            
            // $display("### I: %h", I);
            // $display("pulse_memory_wr_en: %h", pulse_memory_wr_en);
            // $display("pulse_memory_wr_sel: %h", pulse_memory_wr_sel);
            // $display("pulse_memory_wr_addr: %h", pulse_memory_wr_addr);
            // $display("pulse_memory_wr_data: %h", pulse_memory_wr_data);
        end
        else begin
            pulse_memory_wr_en = 1'b0;
            pulse_memory_wr_sel = 0;
            pulse_memory_wr_addr = 0;
            pulse_memory_wr_data = 0;
        end

        #20;
    end

    // Test 1
    // inst_list[0] = 000010203 (counter = 32, pulse_memory_bank = 1, pulse_memory_addr = 3)
    // pulse_memory[1][3] = 1551441331221111000ff0ee0dd0cc0bb0aa09908807706605504403302201100000080
    // -> dc_value: {155,144,133,122,111,100,0ff,...,000}, length = 128
    #20;
    for (I=0; I< NUM_ITER_TEST1; I=I+1) begin
        glb_counter = I;
        #20;
    end
    #20;

    // Test 2
    // inst_list[0] = 000010203 (counter = 320, pulse_memory_bank = 1, pulse_memory_addr = 3)
    // pulse_memory[1][3] = 1551441331221111000ff0ee0dd0cc0bb0aa09908807706605504403302201100000080
    // -> dc_value: {155,144,133,122,111,100,0ff,...,000}, length = 128
    #20;
    for (I=NUM_ITER_TEST1; I< NUM_ITER_TEST2; I=I+1) begin
        glb_counter = I;
        #20;
    end
    #20;
    
    $finish;
end

genvar J;
generate
    for(J = 0; J < NUM_CHANNEL; J = J +1) begin: genblk_default_dc_value_wr_data
        initial begin
            default_dc_value_wr_data[J*DC_VALUE_WIDTH +: DC_VALUE_WIDTH] = J[DC_VALUE_WIDTH-1:0];
        end
    end
endgenerate

initial begin
    // inst_list
    $readmemh("inst_list_n2048_35b.mem", inst_list_mem, 0, INST_LIST_NUM_ENTRY-1);
    // pulse_memory
    $readmemh("pulse_memory_n2048_284b.mem", pulse_mem, 0, PULSE_MEMORY_NUM_ENTRY_PER_BANK*PULSE_MEMORY_NUM_BANK-1);
end


endmodule

/* Expected result */
/*
*/