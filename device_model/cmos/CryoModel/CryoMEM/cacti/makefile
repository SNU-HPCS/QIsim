TAR = cacti

.PHONY: dbg opt depend clean clean_dbg clean_opt

all: opt

dbg: $(TAR).mk obj_dbg obj_reproduce_dbg
	@$(MAKE) TAG=dbg -C . -f $(TAR).mk

opt: $(TAR).mk obj_opt obj_reproduce_opt
	@$(MAKE) TAG=opt -C . -f $(TAR).mk

depend:
	@$(MAKE) -C . -f $(TAR).mk depend

obj_dbg:
	mkdir $@

obj_reproduce_dbg:
	mkdir $@

obj_opt:
	mkdir $@

obj_reproduce_opt:
	mkdir $@

clean: clean_dbg clean_opt

clean_dbg: obj_dbg obj_reproduce_dbg
	@$(MAKE) TAG=dbg -C . -f $(TAR).mk clean
	rm -rf $^

clean_opt: obj_opt obj_reproduce_opt
	@$(MAKE) TAG=opt -C . -f $(TAR).mk clean
	rm -rf $^

format:
	find . -name "*.cc" -o -name "*.h" | xargs clang-format -i -style=file
