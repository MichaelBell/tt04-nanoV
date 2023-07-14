# Makefile
# See https://docs.cocotb.org/en/stable/quickstart.html for more info

# defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
PROG_FILE ?= test.mem

COMPILE_ARGS    += -DSIM -DPROG_FILE=\"$(PROG_FILE)\"

# normal simulation
ifneq ($(GATES),yes)

# this is the only part you should need to modify:
VERILOG_SOURCES += $(PWD)/tb_tt_with_ram.v $(PWD)/nanoV/sim_sram.v $(PWD)/tt_top.v
VERILOG_SOURCES += $(PWD)/nanoV/alu.v $(PWD)/nanoV/core.v $(PWD)/nanoV/cpu.v $(PWD)/nanoV/register.v $(PWD)/nanoV/shift.v 
VERILOG_SOURCES += $(PWD)/uart/uart_tx.v

else

# gate level simulation requires some extra setup, you shouldn't need to touch this
COMPILE_ARGS    += -DGL_TEST
COMPILE_ARGS    += -DFUNCTIONAL
COMPILE_ARGS    += -DUSE_POWER_PINS
COMPILE_ARGS    += -DUNIT_DELAY=#1
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v

# this gets copied in by the GDS action workflow
VERILOG_SOURCES += $(PWD)/tb_tt_with_ram.v $(PWD)/nanoV/sim_sram.v $(PWD)/../runs/wokwi/results/final/verilog/gl/tt_um_MichaelBell_nanoV.v
endif

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL = tb_tt_with_ram

# MODULE is the basename of the Python test file
MODULE = test

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
