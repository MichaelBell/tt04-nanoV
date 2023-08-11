import cocotb
import random
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles, First

async def send_byte(nv, val, wait_for_ready=False, bit_time = 1000000000 // 93750):
    if wait_for_ready and nv.uart_rts.value == 1:
        await First(FallingEdge(nv.uart_rts), Timer(200, "us"))

    assert nv.uart_rts.value == 0
    nv.uart_rxd.value = 0
    await Timer(bit_time, "ns")

    # Send value - LSB first
    nv.uart_rxd.value = val & 1
    await Timer(bit_time, "ns")
    assert nv.uart_rts.value == 1
    nv.uart_rxd.value = (val >> 1) & 1
    await Timer(bit_time, "ns")
    nv.uart_rxd.value = (val >> 2) & 1
    await Timer(bit_time, "ns")
    nv.uart_rxd.value = (val >> 3) & 1
    await Timer(bit_time, "ns")
    nv.uart_rxd.value = (val >> 4) & 1
    await Timer(bit_time, "ns")
    nv.uart_rxd.value = (val >> 5) & 1
    await Timer(bit_time, "ns")
    nv.uart_rxd.value = (val >> 6) & 1
    await Timer(bit_time, "ns")
    nv.uart_rxd.value = (val >> 7) & 1
    await Timer(bit_time, "ns")
    nv.uart_rxd.value = 1

async def recv_byte(nv, val, bit_time = 1000000000 // 93750):
    assert nv.uart_txd.value == 1
    await First(FallingEdge(nv.uart_txd), Timer(1000, "us"))
    assert nv.uart_txd.value == 0

    await Timer(bit_time//2, "ns")
    assert nv.uart_txd.value == 0

    recv_val = 0
    for i in range(8):
        recv_val >>= 1
        await Timer(bit_time, "ns")
        recv_val += nv.uart_txd.value << 7
    assert recv_val == val

    await Timer(bit_time, "ns")
    assert nv.uart_txd.value == 1

@cocotb.test()
async def test_start(nv):
    #random.seed(1691498696)
    clock = Clock(nv.clk, 83, units="ns")
    cocotb.start_soon(clock.start())
    nv.rstn.value = 0
    nv.uart_rxd.value = 1
    await ClockCycles(nv.clk, 2)
    assert nv.uio_oe.value == 0x50
    nv.rstn.value = 1
    await ClockCycles(nv.clk, 2)

    # Check the outputs are configured correctly
    assert nv.uio_oe.value == 0xD7
    assert nv.uart_txd.value == 1
    assert nv.uart_rts.value == 0

    # First byte is echoed back
    b = random.randint(0, 255)
    await send_byte(nv, b)
    await recv_byte(nv, b)
    
    # Second byte is echoed back inverted
    b = random.randint(0, 255)
    await send_byte(nv, b)
    await recv_byte(nv, b ^ 0xFF)
    
    # Third and fourth bytes are added
    a = random.randint(0, 255)
    b = random.randint(0, 255)
    print(a, b)
    await send_byte(nv, a)
    await send_byte(nv, b, True)
    await recv_byte(nv, (a + b) & 0xFF)

    # Four bytes are sent to the GPIO outputs
    for i in range(4):
        a = random.randint(0, 255)
        await send_byte(nv, a)
        await FallingEdge(nv.uart_rts)
        await Timer(50, "us")
        assert nv.uo_out.value == a

    # Four bytes are sent to the GPIO outputs and GPIO inpupts are read back
    for i in range(4):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        nv.ui_in.value = b
        await send_byte(nv, a)
        await recv_byte(nv, b)
        assert nv.uo_out.value == a

    a = random.randint(0, 0xFFFFFFFF)
    b = random.randint(0, 0xFFFFFFFF)
    print(a, b)
    await send_byte(nv, a >> 24)
    await send_byte(nv, a >> 16, True)
    await send_byte(nv, a >> 8, True)
    await send_byte(nv, a, True)
    await send_byte(nv, b >> 24, True)
    await send_byte(nv, b >> 16, True)
    await send_byte(nv, b >> 8, True)
    await send_byte(nv, b, True)

    a = (a * b) & 0xFFFFFFFF
    await recv_byte(nv, a & 0xFF)
    await recv_byte(nv, (a >> 8) & 0xFF)
    await recv_byte(nv, (a >> 16) & 0xFF)
    await recv_byte(nv, (a >> 24) & 0xFF)

    a = random.randint(0, 0x7FFFFFFFFFFFFFFF)
    b = random.randint(0, 0x7FFFFFFFFFFFFFFF)
    print(a, b)
    await send_byte(nv, a >> 56)
    await send_byte(nv, a >> 48, True)
    await send_byte(nv, a >> 40, True)
    await send_byte(nv, a >> 32, True)
    await send_byte(nv, a >> 24, True)
    await send_byte(nv, a >> 16, True)
    await send_byte(nv, a >> 8, True)
    await send_byte(nv, a, True)
    await send_byte(nv, b >> 56, True)
    await send_byte(nv, b >> 48, True)
    await send_byte(nv, b >> 40, True)
    await send_byte(nv, b >> 32, True)
    await send_byte(nv, b >> 24, True)
    await send_byte(nv, b >> 16, True)
    await send_byte(nv, b >> 8, True)
    await send_byte(nv, b, True)

    a = (a * b) & 0xFFFFFFFFFFFFFFFF
    await recv_byte(nv, a & 0xFF)
    await recv_byte(nv, (a >> 8) & 0xFF)
    await recv_byte(nv, (a >> 16) & 0xFF)
    await recv_byte(nv, (a >> 24) & 0xFF)    
    await recv_byte(nv, (a >> 32) & 0xFF)    
    await recv_byte(nv, (a >> 40) & 0xFF)    
    await recv_byte(nv, (a >> 48) & 0xFF)    
    await recv_byte(nv, (a >> 56) & 0xFF)    