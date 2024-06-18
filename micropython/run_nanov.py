import time
import sys
import rp2
import machine
from machine import UART, Pin, PWM, SPI

from ttboard.mode import RPMode
from ttboard.demoboard import DemoBoard

@rp2.asm_pio(autopush=True, push_thresh=32, in_shiftdir=rp2.PIO.SHIFT_RIGHT)
def pio_capture():
    wait(1, gpio, 22)
    wait(0, gpio, 22)
    wrap_target()
    in_(pins, 8)

from load_spi_ram import load_spi_ram

tt = DemoBoard()
tt.shuttle.tt_um_MichaelBell_nanoV.enable()

def run(query=True, stop=True):
    machine.mem32[0x40064000] = 0xd1
    machine.freq(266_000_000)

    if query:
        input("Reset? ")

    tt.uio1.pull = Pin.PULL_UP
    tt.reset_project(True)
    for i in range(10):
        tt.clock_project_once()

    tt.reset_project(False)

    capture = False
    if capture:
        sm = rp2.StateMachine(0, pio_capture, 4_000_000, in_base=Pin(21))

        capture_len=1024
        buf = bytearray(capture_len)

        rx_dma = rp2.DMA()
        c = rx_dma.pack_ctrl(inc_read=False, treq_sel=4) # Read using the SM0 RX DREQ
        sm.restart()
        sm.exec("wait(%d, gpio, %d)" % (0, 22))
        rx_dma.config(
            read=0x5020_0020,        # Read from the SM0 RX FIFO
            write=buf,
            ctrl=c,
            count=capture_len//4,
            trigger=True
        )
        sm.active(1)

    if query:
        input("Start? ")

    #uart = UART(0, baudrate=93750//6, tx=Pin(0), rx=Pin(1), timeout=100, timeout_char=10)
    time.sleep(0.001)
    tt.clock_project_PWM(14_777_777)
    print(machine.mem32[0x400140c4])

    if capture:
        # Wait for DMA to complete
        while rx_dma.active():
            time.sleep_us(100)
            
        sm.active(0)
        del sm

    if not stop:
        return

    if query:
        input("Stop? ")

    if False:
        try:
            sm = rp2.StateMachine(0, pio_capture, 6_000, in_base=Pin(21))
            rx_dma = rp2.DMA()
            capture_len=64
            buf = bytearray(capture_len)
            
            cs = Pin(22, Pin.IN)

            while True:
                c = rx_dma.pack_ctrl(inc_read=False, treq_sel=4) # Read using the SM0 RX DREQ
                #while cs.value() == 0: pass
                sm.restart()
                #sm.exec("wait(%d, gpio, %d)" % (0, 22))
                rx_dma.config(
                    read=0x5020_0020,        # Read from the SM0 RX FIFO
                    write=buf,
                    ctrl=c,
                    count=capture_len//4,
                    trigger=True
                )
                sm.active(1)

                while rx_dma.active():
                    time.sleep_us(100)
                    
                sm.active(0)

                val = 0
                for i in range(32):
                    val <<= 1
                    if buf[2*i] & 1:
                        val |= 1
                print(f"{val:08x}")
                
                if rp2.bootsel_button() != 0:
                    raise KeyboardInterrupt()

        except KeyboardInterrupt:
            pass
        finally:
            tt.clock_project_stop()        
    elif False:
        try:
            while True:
                data = uart.read(16)
                if data is not None:
                    for d in data:
                        if d > 0 and d <= 127:
                            print(chr(d), end="")
                time.sleep_us(100)
                
                if rp2.bootsel_button() != 0:
                    raise KeyboardInterrupt()

        except KeyboardInterrupt:
            pass
        finally:
            tt.clock_project_stop()
    else:
        tt.clock_project_stop()
        
    if capture:
        for j in range(4):
            print("%02d: " % (j+21,), end="")
            for d in buf:
                print("-" if (d & (1 << j)) != 0 else "_", end = "")
            print()

def execute(filename, stop=False):
    load_spi_ram(filename)
    rp2.enable_sim_spi_ram()
    run(query=False, stop=stop)
