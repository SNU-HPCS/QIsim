
`include "define_pulse_circuit.v"

module pulse_amp_generator #(
    parameter AMP_MEMORY_NUM_ENTRY = 512,
    parameter AMP_MEMORY_ADDR_WIDTH = 9,
    parameter AMP_MEMORY_DATA_WIDTH = (12+7),
    parameter GLB_COUNTER_WIDTH = 24,
    parameter DIRECTION_WIDTH = 2,
    parameter AMP_WIDTH = 12,
    parameter LENGTH_WIDTH = 7,
    parameter INST_LIST_NUM_ENTRY = 32,
    parameter INST_LIST_ADDR_WIDTH = 5,
    parameter INST_LIST_DATA_WIDTH = (24+2),
    parameter PC_WIDTH = 5
)(
    clk,
    rst,

    `ifndef INCLUDE_MEMORY_IN_MODULE
        inst_list_wr_en_out,
        inst_list_wr_addr_out,
        inst_list_wr_data_out,
        inst_list_rd_addr_out,
        inst_list_rd_data_in,
        amp_memory_rd_addr_out,
        amp_memory_rd_data_in,
    `endif

    /* Internal memory initialization */
    amp_memory_wr_en,
    amp_memory_wr_addr,
    amp_memory_wr_data,

    default_amp_wr_en,
    default_amp_wr_data,

    /* Input */
    glb_counter,

    inst_list_wr_en,
    inst_list_wr_addr,
    inst_list_wr_data,

    /* Output */
    amp_out
);

localparam UPDATE_ADDR_VALUE = 3;

/* Port declaration */
input                                       clk;
input                                       rst;

input                                       amp_memory_wr_en;
input   [AMP_MEMORY_ADDR_WIDTH-1:0]         amp_memory_wr_addr;
input   [AMP_MEMORY_DATA_WIDTH-1:0]         amp_memory_wr_data;

input                                       default_amp_wr_en;
input   [AMP_WIDTH-1:0]                     default_amp_wr_data;

input   [GLB_COUNTER_WIDTH-1:0]             glb_counter;

input                                       inst_list_wr_en;
input   [INST_LIST_ADDR_WIDTH-1:0]          inst_list_wr_addr;
input   [INST_LIST_DATA_WIDTH-1:0]          inst_list_wr_data;

output  [AMP_WIDTH-1:0]                     amp_out;

`ifndef INCLUDE_MEMORY_IN_MODULE
    output                                  inst_list_wr_en_out;
    output      [INST_LIST_ADDR_WIDTH-1:0]  inst_list_wr_addr_out;
    output      [INST_LIST_DATA_WIDTH-1:0]  inst_list_wr_data_out;
    output      [INST_LIST_ADDR_WIDTH-1:0]  inst_list_rd_addr_out;
    input       [INST_LIST_DATA_WIDTH-1:0]  inst_list_rd_data_in;
    output      [AMP_MEMORY_ADDR_WIDTH-1:0] amp_memory_rd_addr_out;
    input       [AMP_MEMORY_DATA_WIDTH-1:0] amp_memory_rd_data_in;
`endif

/* Wire/reg declaration */
// PC
wire [PC_WIDTH-1:0] PC;
wire [PC_WIDTH-1:0] next_PC;
wire update_pc;

wire [INST_LIST_ADDR_WIDTH-1:0] inst_list_rd_addr;
wire [INST_LIST_DATA_WIDTH-1:0] inst_list_rd_data;

wire start_inst;

// reg                             valid_inst_list;
// reg [DIRECTION_WIDTH-1:0]       direction;
wire                             valid_inst_list;
wire [DIRECTION_WIDTH-1:0]       direction;

// amp_memory_addr_generator
wire [AMP_MEMORY_ADDR_WIDTH-1:0] amp_memory_addr;
wire update_addr;
reg is_next_addr;

// amp_memory
wire [AMP_MEMORY_ADDR_WIDTH-1:0] amp_memory_rd_addr;
wire [AMP_MEMORY_DATA_WIDTH-1:0] amp_memory_rd_data;

reg [AMP_WIDTH-1:0]     amp;
reg [LENGTH_WIDTH-1:0]  length;
reg                     set_counter;

wire                    fin_cond;

// pulse_length_counter
wire [LENGTH_WIDTH-1:0] cur_length_count;
wire [LENGTH_WIDTH-1:0] cur_count_out;
wire                    counter_running;

// dac_control
reg [AMP_WIDTH-1:0] default_amp;

wire [2*AMP_WIDTH-1:0]  mux_sel_amp_data_in;
wire                    mux_sel_amp_sel;
wire [AMP_WIDTH-1:0]    mux_sel_amp_data_out;


/* Module instantiation */
// PC
assign next_PC = PC + 1;

comparator_param #(
    .DATA_WIDTH(GLB_COUNTER_WIDTH),
    .EQUAL(1)
) glb_counter_comparator (
    .data_in_1(glb_counter),
    .data_in_2(inst_list_rd_data[DIRECTION_WIDTH +: GLB_COUNTER_WIDTH]),
    .data_out(update_pc)
);
// assign update_pc = (glb_counter == inst_list_rd_data[DIRECTION_WIDTH +: GLB_COUNTER_WIDTH]) ? 1'b1 : 1'b0;

pulse_pc #(
    .PC_WIDTH(PC_WIDTH)
) pc_0 (
    .clk(clk),
    .rst(rst),
    .update_pc(update_pc),
    .next_PC(next_PC),
    .PC(PC)
);

assign inst_list_rd_addr = PC;
`ifdef INCLUDE_MEMORY_IN_MODULE
    random_access_mem #(
        .NUM_ENTRY(INST_LIST_NUM_ENTRY),
        .ADDR_WIDTH(INST_LIST_ADDR_WIDTH),
        .DATA_WIDTH(INST_LIST_DATA_WIDTH)
    ) inst_list (
        .clk(clk),
        .wr_en(inst_list_wr_en),
        .wr_addr(inst_list_wr_addr),
        .wr_data(inst_list_wr_data),
        .rd_addr(inst_list_rd_addr),
        .rd_data(inst_list_rd_data)
    );
`else
    assign inst_list_wr_en_out = inst_list_wr_en; 
    assign inst_list_wr_addr_out = inst_list_wr_addr; 
    assign inst_list_wr_data_out = inst_list_wr_data; 
    assign inst_list_rd_addr_out = inst_list_rd_addr;
    assign inst_list_rd_data = inst_list_rd_data_in;
`endif


assign start_inst = update_pc;

ff #(
    .DATA_WIDTH(1)
) valid_inst_list_ff (
    .clk(clk),
    .rst(rst),
    .wr_en(1'b1), 
    .wr_data(start_inst), 
    .rd_data(valid_inst_list)
);

// always @(posedge clk) begin
//     valid_inst_list <= start_inst;
// end

ff #(
    .DATA_WIDTH(DIRECTION_WIDTH)
) direction_ff (
    .clk(clk),
    .rst(rst),
    .wr_en(start_inst), 
    .wr_data(inst_list_rd_data[0 +: DIRECTION_WIDTH]), 
    .rd_data(direction)
);

// always @(posedge clk) begin
//     if (start_inst) begin
//         direction <= inst_list_rd_data[0 +: DIRECTION_WIDTH];
//     end
// end

// amp_memory_addr_generator
assign update_addr = (cur_count_out == UPDATE_ADDR_VALUE) ? 1'b1 : 1'b0;

pulse_amp_memory_addr_generator #(
    .DIRECTION_WIDTH(DIRECTION_WIDTH),
    .AMP_MEMORY_ADDR_WIDTH(AMP_MEMORY_ADDR_WIDTH)
) pulse_amp_memory_addr_generator_instance (
    .clk(clk),
    .rst(rst),
    .reset_addr(valid_inst_list),
    .update_addr(update_addr),
    .direction_in(direction),
    .amp_memory_addr_out(amp_memory_addr)
);


always @(posedge clk) begin
    is_next_addr <= update_addr | valid_inst_list;
end

// amp_memory
assign amp_memory_rd_addr = amp_memory_addr;

`ifdef INCLUDE_MEMORY_IN_MODULE
    random_access_mem #(
        .NUM_ENTRY(AMP_MEMORY_NUM_ENTRY),
        .ADDR_WIDTH(AMP_MEMORY_ADDR_WIDTH),
        .DATA_WIDTH(AMP_MEMORY_DATA_WIDTH)
    ) pulse_amp_memory (
        .clk(clk),
        .wr_en(amp_memory_wr_en),
        .wr_addr(amp_memory_wr_addr),
        .wr_data(amp_memory_wr_data),
        .rd_addr(amp_memory_rd_addr),
        .rd_data(amp_memory_rd_data)
    );
`else
    assign amp_memory_rd_addr_out = amp_memory_rd_addr;
    assign amp_memory_rd_data = amp_memory_rd_data_in;
`endif

assign fin_cond = (amp_memory_addr[AMP_MEMORY_ADDR_WIDTH-DIRECTION_WIDTH-1:0] >= {((AMP_MEMORY_ADDR_WIDTH - DIRECTION_WIDTH)){1'b1}}) ? 1'b1 : 1'b0;
always @(posedge clk) begin
    amp <= amp_memory_rd_data[LENGTH_WIDTH +: AMP_WIDTH];
    length <= amp_memory_rd_data[0 +: LENGTH_WIDTH];
    set_counter <= (~fin_cond) & (is_next_addr);
end

// pulse_length_counter
assign cur_length_count = cur_count_out;

pulse_length_counter #(
    .LENGTH_WIDTH(LENGTH_WIDTH)
) pulse_length_counter_instance (
    .clk(clk),
    .rst(rst),
    .set_counter(set_counter),
    .length_in(length),
    .cur_count_out(cur_count_out),
    .counter_running(counter_running)
);

// dac_control
always @(posedge clk) begin
    if (rst) begin
        default_amp <= 0;
    end
    else begin
        if (default_amp_wr_en) begin
            default_amp <= default_amp_wr_data;
        end
        else begin
            default_amp <= default_amp;
        end
    end
end

assign mux_sel_amp_data_in = {amp, default_amp};
assign mux_sel_amp_sel = counter_running;

mux_param #(
    .NUM_INPUT(2),
    .SEL_WIDTH(1),
    .DATA_WIDTH(AMP_WIDTH)
) mux_sel_amp (
    .data_in(mux_sel_amp_data_in),
    .sel(mux_sel_amp_sel),
    .data_out(mux_sel_amp_data_out)
);

// output
assign amp_out = mux_sel_amp_data_out;


endmodule