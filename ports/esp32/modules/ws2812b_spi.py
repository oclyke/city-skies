import ws2812b_utils
import machine

DEFAULT_SPI_HOST = 2  # vspi


class WS2812B_SPI:
    RESET_BUF = bytearray(16)

    def __init__(self, pins, pixels, spi_host=DEFAULT_SPI_HOST):
        (self.sck, self.mosi, self.miso) = pins
        self.bus = machine.SPI(
            spi_host,
            2500000,
            sck=machine.Pin(self.sck),
            mosi=machine.Pin(self.mosi),
            miso=machine.Pin(self.miso),
            polarity=0,
            phase=0,
            bits=8,
            firstbit=0,
        )
        self.buf = bytearray(9 * pixels)

    def ingest(self, memory):
        ws2812b_utils.sicgl_memory_to_spi_bitstream(memory, self.buf)

    def push(self):
        # NOTE: there is some *actual bullshit* happening between the spi driver and the network interface, somehow
        # when the spi driver is made to be non-blocking (by commenting out code in mpy machine_hw_spi.c which waits for transactions to finish) _most_ writes to it cause the network to fail to get ota updates...
        # when the driver is restored to blocking it works fine but a lot of time is wasted (causing a host of other issues)
        self.bus.write(self.RESET_BUF)  # shift out a reset signal (all low)
        self.bus.write(self.buf)  # use the bus to shift out the data

        # NOTE: for the time being this is blocking code and takes approx 9.6 us per byte of pixel data (that's 900 bytes for 300 leds which would equate to 8.6 ms)
        # NOTE: it would be really nice to make this code back into non-blocking...
