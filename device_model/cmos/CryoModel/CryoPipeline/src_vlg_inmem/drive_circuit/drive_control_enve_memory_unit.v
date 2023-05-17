// Drive circuit (based on Horse Ridge I)

`define WAITING 0
`define RUNNING 1

module drive_control_enve_memory_unit 
(
    /*
    clk,
    rst,
    valid_inst_table_in,
    is_read_env_fin,

    valid_addr,
    set_enve_memory_addr,
    increment_enve_memory_addr
    */
    // /*

    clk,
    rst,
    valid_inst_table_in,
    is_read_env_fin,

    start_read_addr,
    set_enve_memory_addr,
    increment_enve_memory_addr
    // */
);

// Port declaration
/*
input                       clk;
input                       rst;
input                       valid_inst_table_in;
input                       is_read_env_fin;

output reg [0:0]            valid_addr;
output reg [0:0]            set_enve_memory_addr;
output reg [0:0]            increment_enve_memory_addr;
*/
input                       clk;
input                       rst;
input                       valid_inst_table_in;
input                       is_read_env_fin;

output reg [0:0]            start_read_addr;
output reg [0:0]            set_enve_memory_addr;
output reg [0:0]            increment_enve_memory_addr;
// 

// /*
reg                         state;

always @(posedge clk) begin
    if (rst) begin
        state <= `WAITING;
        start_read_addr <= 1'b0;
        set_enve_memory_addr <= 1'b0;
        increment_enve_memory_addr <= 1'b0;
    end
    else begin
        if (state == `WAITING) begin
            if (valid_inst_table_in) begin
                state <= `RUNNING;
                start_read_addr <= 1'b1;
                set_enve_memory_addr <= 1'b1;
                increment_enve_memory_addr <= 1'b0;
            end
            else begin
                state <= `WAITING;
                start_read_addr <= 1'b0;
                set_enve_memory_addr <= 1'b0;
                increment_enve_memory_addr <= 1'b0;
            end
        end
        else begin
            if (is_read_env_fin) begin
                state <= `WAITING;
                start_read_addr <= 1'b0;
                set_enve_memory_addr <= 1'b0;
                increment_enve_memory_addr <= 1'b0;
            end
            else begin
                state <= `RUNNING;
                start_read_addr <= 1'b0;
                set_enve_memory_addr <= 1'b0;
                increment_enve_memory_addr <= 1'b1;
            end
        end
    end
end
// */

/*
always @(posedge clk) begin
    if (rst) begin
        start_read_addr <= 1'b0;
        set_enve_memory_addr <= 1'b0;
        increment_enve_memory_addr <= 1'b0;
    end
    else begin
        if (valid_inst_table_in) begin
            start_read_addr <= 1'b1;
            set_enve_memory_addr <= 1'b1;
            increment_enve_memory_addr <= 1'b0;
        end
        else begin
            start_read_addr <= 1'b0;
            set_enve_memory_addr <= 1'b0;
            increment_enve_memory_addr <= 1'b0;
        end
     end
end
*/

endmodule
