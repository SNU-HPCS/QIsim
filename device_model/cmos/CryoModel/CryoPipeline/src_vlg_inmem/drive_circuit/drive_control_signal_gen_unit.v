// Drive circuit (based on Horse Ridge I)

/*
`define WAITING 0
`define FETCHING 1
*/

// `define STATE_WIDTH 2
// `define PREPARING   2'b00
// `define WAITING     2'b01
// `define FETCHING    2'b10

module drive_control_signal_gen_unit 
(
    clk,
    rst,
    glb_is_read_env_fin,
    trigger,
    is_rz_fin,

    update_pc
);

// Port declaration
input                       clk;
input                       rst;
input                       glb_is_read_env_fin;
input                       trigger;
input                       is_rz_fin;

output reg [0:0]            update_pc;

// 
// reg     [STATE_WIDTH-1:0]   state;
reg                         prev_glb_is_read_env_fin;

wire                        fetch_cond;
/*
always @(posedge clk) begin
    if (rst) begin
        update_pc <= 0;
        state <= `WAITING;
    end
    else begin
        if (state == `WAITING) begin
            if (glb_is_read_env_fin | trigger | is_rz_fin) begin
                update_pc <= 1;
                state <= `FETCHING;
            end
            else begin
                update_pc <= 0;
                state <= `WAITING;
            end
        end
        else begin
            if (glb_is_read_env_fin) begin
                state <= `FETCHING;
                update_pc <= 0;
            end
            else begin
                state <= `WAITING;
                update_pc <= 0;
            end
        end
    end
end
*/

always @(posedge clk) begin
    if (rst) begin
        update_pc <= 0;
    end
    else begin
        if (fetch_cond) begin
            update_pc <= 1;
        end
        else begin
            update_pc <= 0;
        end
    end
end

always @(posedge clk) begin
    prev_glb_is_read_env_fin <= glb_is_read_env_fin;
end

assign fetch_cond = ((~prev_glb_is_read_env_fin) & glb_is_read_env_fin) | is_rz_fin | trigger;

endmodule
