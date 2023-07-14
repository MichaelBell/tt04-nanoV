import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

# Just executes whatever is in test.mem so you can inspect the waveform
# https://riscvasm.lucasteske.dev/# is useful for assembling hex for the file.
@cocotb.test()
async def test_start(nv):
    clock = Clock(nv.clk, 83, units="ns")
    cocotb.start_soon(clock.start())
    nv.rstn.value = 0
    await ClockCycles(nv.clk, 2)

    # Check the outputs are configured correctly
    assert nv.uio_oe.value == 0x17

    nv.rstn.value = 1
    await Timer(200, "us")
