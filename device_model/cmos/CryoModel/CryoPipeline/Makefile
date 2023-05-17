SRC=\
	./src/*

help:
	@echo "commands: make [ all ]"
	@echo "				  [ compile-all / critical-all / milky-all ]"
	@echo "               [ dc-topo-4k / dc-topo-4k-nowire ]"
	@echo "               [ lib-4k ]"
	@echo "               [ milky-300k / milky-77k / milky-ideal ]"
	@echo "               [ critical-4k / critical-4k-nowire ]"
	@echo "               [ clean ]"

all:
	+make dc-topo-4k
	rm latency_result/*/*
	+make critical-4k

critical-all:
	rm latency_result/*/*
	+make critical-4k

lib-all:
	+make lib-4k
	+make lib-ideal

milky-all:
	+make milky-4k
	+make milky-ideal

# logic synthesis (with accurate wire latency)
dc-topo-4k:
	dc_shell -64bit -topo -f dc_compile/logic_synthesis/dc_compile_drive_4k.tcl | tee dc-drive-4k.txt
	dc_shell -64bit -topo -f dc_compile/logic_synthesis/dc_compile_pulse_4k.tcl | tee dc-pulse-4k.txt
	dc_shell -64bit -topo -f dc_compile/logic_synthesis/dc_compile_readrx_4k.tcl | tee dc-readrx-4k.txt
	dc_shell -64bit -topo -f dc_compile/logic_synthesis/dc_compile_readtx_4k.tcl | tee dc-readtx-4k.txt

# Critical-path latency extraction
critical-4k:
	dc_shell -64bit -topo -f dc_compile/critical_path_extraction/critical_path_drive_4k.tcl | tee c-drive-4k.txt
	dc_shell -64bit -topo -f dc_compile/critical_path_extraction/critical_path_pulse_4k.tcl | tee c-pulse-4k.txt
	dc_shell -64bit -topo -f dc_compile/critical_path_extraction/critical_path_readrx_4k.tcl | tee c-readrx-4k.txt
	dc_shell -64bit -topo -f dc_compile/critical_path_extraction/critical_path_readtx_4k.tcl | tee c-readtx-4k.txt

# Library validation
lib-4k:
	dc_shell -64bit -topo -f dc_compile/library_validation/dc_lib_test_77k.tcl | tee lib-77k.txt
lib-ideal:
	dc_shell -64bit -topo -f dc_compile/library_validation/dc_lib_test_ideal.tcl | tee lib-ideal.txt

# Generate milkyway library
# # convert Cadence-style physical library (.lef) to Synopsys-style physical library (milkyway, .tf)
milky-4k:
	Milkyway -galaxy -nogui -tcl -log log.txt -file dc_compile/physical_library_generation/gen_milky_4k.tcl
	mv milky-45nm-4k.tf ./freepdk-45nm/stdview/rtk-tech-4k.tf
milky-ideal:
	Milkyway -galaxy -nogui -tcl -log log.txt -file dc_compile/physical_library_generation/gen_milky_ideal.tcl
	mv milky-45nm-ideal.tf ./freepdk-45nm/stdview/rtk-tech-ideal.tf

# Clean-up
clean:
	rm -rf *.mr *.sdc *.vh *.v *.syn *.pvl *.max *.min *.sdf *.log WORK_autoread default.svf *.script Milkyway.tcl.* rtk-tech.lef* stdcells.lef.* *.sum alib-52 Milkyway.*.* rtk-tech-* *.txt
