define_design_lib WORK -path ./WORK

set TOP_MODULE readout_rx_circuit
set src_path "./src_vlg"
set PDK_path "./freepdk-45nm/stdview"
set SYN_path "/home/synopsys/dc_compiler_2019/syn/P-2019.03/libraries/syn"

set search_path "$src_path \ $PDK_path \ $SYN_path"

set target_library "$PDK_path/NangateOpenCellLibrary.db"
set synthetic_library "$SYN_path/dw_foundation.sldb"
set link_library "* $target_library $synthetic_library"
set mw_reference_library "./milky-45nm-ideal"
set mw_design_library "./mw_design_lib_ideal"
set technology_file "$PDK_path/rtk-tech-ideal.tf"
set hdlin_while_loop_iterations 100000

open_mw_lib $mw_design_library
check_library

read_ddc ${src_path}/../${TOP_MODULE}_4k.ddc

compile_ultra -incremental -only_design_rule -spg

write -hierarchy -format ddc -output ${TOP_MODULE}_4k_nowire.ddc

exit
