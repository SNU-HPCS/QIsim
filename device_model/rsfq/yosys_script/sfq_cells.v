module NOTT_RSFQ(A, Q);
input A;
output Q;
assign Q = ~A;
endmodule

module ANDT_RSFQ(A, B, Q);
input A, B;
output Q;
assign Q = (A & B);
endmodule

module ORT_RSFQ(A, B, Q);
input A, B;
output Q;
assign Q = (A | B);
endmodule

module XORT_RSFQ(A, B, Q);
input A, B;
output Q;
assign Q = (A ^ B);
endmodule

module XNORT_RSFQ(A, B, Q);
input A, B;
output Q;
assign Q = ~(A ^ B);
endmodule

module DFFT_RSFQ(C, A, Q);
input C, A;
output reg Q;
always @(posedge C)
	Q <= A;
endmodule

module NDROT_RSFQ(C, A, B, Q);
input C, A, B;
output reg Q;
reg S; 

always @ (posedge A)
    S <= 1'b1;

always @ (posedge B)
    S <= 1'b0;

always @ (posedge C)
    Q <= S;
endmodule
