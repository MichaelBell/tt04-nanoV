![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/wokwi_test/badge.svg)

# nanoV: A minimal RV32E for Tiny Tapeout

A minimal RV32E processor using an SPI RAM for instructions and data.

The SPI RAM and a UART are connected to the bidi IOs.  The SPI RAM is clocked at the same speed as the input clock.
      
The CPU has no instruction or data cache and effectively runs at clock speed / 32.  More details on th eimplementation can be found in the [nanoV](https://github.com/MichaelBell/nanoV) repo.

# What is Tiny Tapeout?

TinyTapeout is an educational project that aims to make it easier and cheaper than ever to get your digital designs manufactured on a real chip!

Go to https://tinytapeout.com for instructions!

## Tiny Tapeout Resources

- [FAQ](https://tinytapeout.com/faq/)
- [Digital design lessons](https://tinytapeout.com/digital_design/)
- [Learn how semiconductors work](https://tinytapeout.com/siliwiz/)
- [Join the community](https://discord.gg/rPK2nSjxy8)
