read_lef -lib_name milky-45nm-ideal -tech_lef_files ./freepdk-45nm/stdview/rtk-tech-ideal.lef -cell_lef_files "./freepdk-45nm/stdview/stdcells.lef"
cmDumpTech
setFormField "Dump Technology File" "Library Name" "milky-45nm-ideal"
setFormField "Dump Technology File" "Technology File Name" "milky-45nm-ideal.tf"
formOK "Dump Technology File"
exit
