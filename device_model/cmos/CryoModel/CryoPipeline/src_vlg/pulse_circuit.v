
`include "define_pulse_circuit.v"

module pulse_circuit (
    clk,
    rst,

    glb_counter, 

    `ifndef INCLUDE_MEMORY_IN_MODULE
        /* If the memory is instantiated outside of the module */
        inst_list_wr_en_out,
        inst_list_wr_addr_out,
        inst_list_wr_data_out,
        inst_list_rd_addr_out,
        inst_list_rd_data_in,
        amp_memory_rd_addr_out,
        amp_memory_rd_data_in,
    `endif

    /* Internal memory initialization */
    valid_in,
    mask_in,
    start_time_in,

    amp_memory_wr_sel,
    amp_memory_wr_en,
    amp_memory_wr_addr,
    amp_memory_wr_data,

    default_amp_wr_sel,
    default_amp_wr_en,
    default_amp_wr_data,

    /* output */
    amp_out

);

/* Port declaration */
input                                                               clk; 
input                                                               rst;

input           [`PULSE_GLB_COUNTER_WIDTH-1:0]                      glb_counter;

// mask decoder
input                                                               valid_in;
input           [`PULSE_NUM_QUBIT*`PULSE_MASK_WIDTH-1:0]            mask_in;
input           [`PULSE_GLB_COUNTER_WIDTH-1:0]                      start_time_in;

// map_generator
input           [`PULSE_QUBIT_ADDR_WIDTH-1:0]                       amp_memory_wr_sel;
input                                                               amp_memory_wr_en;
input           [`PULSE_AMP_MEMORY_ADDR_WIDTH-1:0]                  amp_memory_wr_addr;
input           [`PULSE_AMP_MEMORY_DATA_WIDTH-1:0]                  amp_memory_wr_data;
 
input           [`PULSE_QUBIT_ADDR_WIDTH-1:0]                       default_amp_wr_sel;
input                                                               default_amp_wr_en;
input           [`PULSE_AMP_WIDTH-1:0]                              default_amp_wr_data;

// output
output          [`PULSE_NUM_QUBIT*`PULSE_AMP_WIDTH-1:0]             amp_out;

// 
`ifndef INCLUDE_MEMORY_IN_MODULE
    output      [`PULSE_NUM_QUBIT-1:0]                              inst_list_wr_en_out;
    output      [`PULSE_NUM_QUBIT*`PULSE_INST_LIST_ADDR_WIDTH-1:0]  inst_list_wr_addr_out;
    output      [`PULSE_NUM_QUBIT*`PULSE_INST_LIST_DATA_WIDTH-1:0]  inst_list_wr_data_out;

    output      [`PULSE_NUM_QUBIT*`PULSE_INST_LIST_ADDR_WIDTH-1:0]  inst_list_rd_addr_out;
    input       [`PULSE_NUM_QUBIT*`PULSE_INST_LIST_DATA_WIDTH-1:0]  inst_list_rd_data_in;

    output      [`PULSE_NUM_QUBIT*`PULSE_AMP_MEMORY_ADDR_WIDTH-1:0] amp_memory_rd_addr_out;
    input       [`PULSE_NUM_QUBIT*`PULSE_AMP_MEMORY_DATA_WIDTH-1:0] amp_memory_rd_data_in;
`endif

/* Wire/reg declaration */


/* Module instantation and connection */
genvar i;
generate
    for (i = 0; i < `PULSE_NUM_QUBIT; i=i+1) begin: genblk_pulse_circuit
        // mask_decoder
        // Internal wire declaration
        wire                                        valid_in_i;
        wire    [`PULSE_MASK_WIDTH-1:0]             mask_in_i;
        wire    [`PULSE_GLB_COUNTER_WIDTH-1:0]      start_time_in_i;

        wire                                        inst_list_wr_en_i;
        wire    [`PULSE_INST_LIST_ADDR_WIDTH-1:0]   inst_list_wr_addr_i;
        wire    [`PULSE_INST_LIST_DATA_WIDTH-1:0]   inst_list_wr_data_i;

        // Module instantation and connection
        assign valid_in_i = valid_in;
        assign mask_in_i = mask_in[`PULSE_MASK_WIDTH*i +: `PULSE_MASK_WIDTH];
        assign start_time_in_i = start_time_in;

        pulse_mask_decoder #(
            .MASK_WIDTH(`PULSE_MASK_WIDTH),
            .GLB_COUNTER_WIDTH(`PULSE_GLB_COUNTER_WIDTH),
            .INST_LIST_ADDR_WIDTH(`PULSE_INST_LIST_ADDR_WIDTH),
            .INST_LIST_DATA_WIDTH(`PULSE_INST_LIST_DATA_WIDTH),
            .DIRECTION_WIDTH(`PULSE_DIRECTION_WIDTH)
        ) pulse_mask_decoder_instance (
            .clk(clk),
            .rst(rst),
            .valid_in(valid_in_i),
            .mask_in(mask_in_i),
            .start_time_in(start_time_in_i),
            .inst_list_wr_en(inst_list_wr_en_i),
            .inst_list_wr_addr(inst_list_wr_addr_i),
            .inst_list_wr_data(inst_list_wr_data_i)
        );


        // amp_generator
        // Internal wire declaration
        wire                                        amp_memory_wr_en_i;
        wire    [`PULSE_AMP_MEMORY_ADDR_WIDTH-1:0]  amp_memory_wr_addr_i;
        wire    [`PULSE_AMP_MEMORY_DATA_WIDTH-1:0]  amp_memory_wr_data_i;
        wire                                        default_amp_wr_en_i;
        wire    [`PULSE_AMP_WIDTH-1:0]              default_amp_wr_data_i;
        wire    [`PULSE_GLB_COUNTER_WIDTH-1:0]      glb_counter_i;
        wire    [`PULSE_AMP_WIDTH-1:0]              amp_out_i;

        `ifndef INCLUDE_MEMORY_IN_MODULE
            wire                                        inst_list_wr_en_out_i;
            wire    [`PULSE_INST_LIST_ADDR_WIDTH-1:0]   inst_list_wr_addr_out_i;
            wire    [`PULSE_INST_LIST_DATA_WIDTH-1:0]   inst_list_wr_data_out_i;
            wire    [`PULSE_INST_LIST_ADDR_WIDTH-1:0]   inst_list_rd_addr_out_i;
            wire    [`PULSE_INST_LIST_DATA_WIDTH-1:0]   inst_list_rd_data_in_i;
            wire    [`PULSE_AMP_MEMORY_ADDR_WIDTH-1:0]  amp_memory_rd_addr_out_i;
            wire    [`PULSE_AMP_MEMORY_DATA_WIDTH-1:0]  amp_memory_rd_data_in_i;
        `endif

        // Module instantation and connection
        assign amp_memory_wr_en_i = amp_memory_wr_en & (amp_memory_wr_sel == i);
        assign amp_memory_wr_addr_i = amp_memory_wr_addr;
        assign amp_memory_wr_data_i = amp_memory_wr_data;

        assign default_amp_wr_en_i = default_amp_wr_en & (default_amp_wr_sel == i);
        assign default_amp_wr_data_i = default_amp_wr_data;
        assign glb_counter_i = glb_counter;
        assign amp_out[`PULSE_AMP_WIDTH*i +: `PULSE_AMP_WIDTH] = amp_out_i;

        `ifndef INCLUDE_MEMORY_IN_MODULE
            assign inst_list_wr_en_out[i] = inst_list_wr_en_out_i;
            assign inst_list_wr_addr_out[`PULSE_INST_LIST_ADDR_WIDTH*i +: `PULSE_INST_LIST_ADDR_WIDTH] = inst_list_wr_addr_out_i;
            assign inst_list_wr_data_out[`PULSE_INST_LIST_DATA_WIDTH*i +: `PULSE_INST_LIST_DATA_WIDTH] = inst_list_wr_data_out_i;
            assign inst_list_rd_addr_out[`PULSE_INST_LIST_ADDR_WIDTH*i +: `PULSE_INST_LIST_ADDR_WIDTH] = inst_list_rd_addr_out_i;
            assign inst_list_rd_data_in_i = inst_list_rd_data_in[`PULSE_INST_LIST_DATA_WIDTH*i +: `PULSE_INST_LIST_DATA_WIDTH];
            assign amp_memory_rd_addr_out[`PULSE_AMP_MEMORY_ADDR_WIDTH*i +: `PULSE_AMP_MEMORY_ADDR_WIDTH] = amp_memory_rd_addr_out_i;
            assign amp_memory_rd_data_in_i = amp_memory_rd_data_in[`PULSE_AMP_MEMORY_DATA_WIDTH*i +: `PULSE_AMP_MEMORY_DATA_WIDTH];
        `endif

        pulse_amp_generator #(
            .AMP_MEMORY_NUM_ENTRY(`PULSE_AMP_MEMORY_NUM_ENTRY),
            .AMP_MEMORY_ADDR_WIDTH(`PULSE_AMP_MEMORY_ADDR_WIDTH),
            .AMP_MEMORY_DATA_WIDTH(`PULSE_AMP_MEMORY_DATA_WIDTH),
            .GLB_COUNTER_WIDTH(`PULSE_GLB_COUNTER_WIDTH),
            .DIRECTION_WIDTH(`PULSE_DIRECTION_WIDTH),
            .AMP_WIDTH(`PULSE_AMP_WIDTH),
            .LENGTH_WIDTH(`PULSE_LENGTH_WIDTH),
            .INST_LIST_NUM_ENTRY(`PULSE_INST_LIST_NUM_ENTRY),
            .INST_LIST_ADDR_WIDTH(`PULSE_INST_LIST_ADDR_WIDTH),
            .INST_LIST_DATA_WIDTH(`PULSE_INST_LIST_DATA_WIDTH),
            .PC_WIDTH(`PULSE_PC_WIDTH)
        ) pulse_amp_generator_instance (
            .clk(clk),
            .rst(rst),
            `ifndef INCLUDE_MEMORY_IN_MODULE
                .inst_list_wr_en_out(inst_list_wr_en_out_i),
                .inst_list_wr_addr_out(inst_list_wr_addr_out_i),
                .inst_list_wr_data_out(inst_list_wr_data_out_i),
                .inst_list_rd_addr_out(inst_list_rd_addr_out_i),
                .inst_list_rd_data_in(inst_list_rd_data_in_i),
                .amp_memory_rd_addr_out(amp_memory_rd_addr_out_i),
                .amp_memory_rd_data_in(amp_memory_rd_data_in_i),
            `endif
            .amp_memory_wr_en(amp_memory_wr_en_i),
            .amp_memory_wr_addr(amp_memory_wr_addr_i),
            .amp_memory_wr_data(amp_memory_wr_data_i),
            .default_amp_wr_en(default_amp_wr_en_i),
            .default_amp_wr_data(default_amp_wr_data_i),
            .glb_counter(glb_counter_i),
            .inst_list_wr_en(inst_list_wr_en_i),
            .inst_list_wr_addr(inst_list_wr_addr_i),
            .inst_list_wr_data(inst_list_wr_data_i),
            .amp_out(amp_out_i)
        );
    end
endgenerate


endmodule 
