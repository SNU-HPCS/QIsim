TARGET = cacti
SHELL = /bin/sh
.PHONY: all depend clean
.SUFFIXES: .cc .o

ifndef NTHREADS
  NTHREADS = 8
endif


LIBS = -lm -lboost_serialization -lprotobuf
INCS = 

ifeq ($(TAG),dbg)
  DBG = -Wall 
  OPT = -ggdb -g -O0 -DNTHREADS=1  -gstabs+
else
  DBG = 
  OPT = -O3 -msse2 -mfpmath=sse -DNTHREADS=$(NTHREADS) -DNDEBUG
endif

#CXXFLAGS = -Wall -Wno-unknown-pragmas -Winline $(DBG) $(OPT) 
CXXFLAGS = -Wno-unknown-pragmas -std=c++17 $(DBG) $(OPT)
CXX = /opt/gcc-9.2/bin/g++-9.2 -m64
CC  = /opt/gcc-9.2/bin/gcc-9.2 -m64

SRCS  = arbiter.cc bank.cc basic_circuit.cc bob_conf.cc cacti_interface.cc calculate_time.cc channel_conf.cc \
component.cc crossbar.cc decoder.cc device_type.cc driver.cc dynamic_parameter.cc extio.cc htree2.cc \
input_parameter.cc interconnect_type.cc io.cc io_tech_param.cc main.cc mat.cc mem_array.cc mem_cad.cc \
mem_cad_parameters.cc memorybus.cc memory_conf.cc memory_parameters.cc memory_type.cc min_values_t.cc \
nuca.cc nuca_org_t.cc power_def.cc power_components.cc predec_blk.cc predec_blk_drv.cc predec.cc router.cc scaling_factor.cc \
sleep_tx.cc subarray.cc technology_parameter.cc tsv.cc uca.cc uca_org_t.cc wire.cc cacti_interface.pb.cc \
global_cacti_input.cc

OBJS = $(patsubst %.cc,obj_$(TAG)/%.o,$(SRCS))
OBJS_REPRODUCE = $(patsubst %.cc,obj_reproduce_$(TAG)/%.o,$(SRCS))

all: obj_$(TAG)/$(TARGET) obj_reproduce_$(TAG)/$(TARGET)_reproduce cacti_interface_pb2.py
	cp -f obj_$(TAG)/$(TARGET) .
	cp -f obj_reproduce_$(TAG)/$(TARGET)_reproduce .

-include dep
-include dep_reproduce

obj_$(TAG)/$(TARGET) : $(OBJS)
	$(CXX) $(OBJS) -o $@ $(INCS) $(CXXFLAGS) $(LIBS) -pthread

obj_reproduce_$(TAG)/$(TARGET)_reproduce : $(OBJS_REPRODUCE)
	$(CXX) $(OBJS_REPRODUCE) -o $@ $(INCS) $(CXXFLAGS) $(LIBS) -pthread

obj_$(TAG)/%.o : %.cc
	$(CXX) $(CXXFLAGS) -c $< -o $@

obj_reproduce_$(TAG)/%.o : %.cc
	$(CXX) $(CXXFLAGS) -DCACTI_REPRODUCE -c $< -o $@

%.pb.cc %.pb.h : %.proto
	protoc --cpp_out=. $<

cacti_interface_pb2.py : cacti_interface.proto
	protoc --python_out=. $<

depend: dep dep_reproduce

dep: ${SRCS}
	$(CXX) -MM ${SRCS} > $@

dep_reproduce: ${SRCS}
	$(CXX) -DCACTI_REPRODUCE -MM ${SRCS} > $@

clean:
	-rm -rf $(TARGET) $(TARGET)_reproduce *.pb.* cacti_interface_pb2.py
