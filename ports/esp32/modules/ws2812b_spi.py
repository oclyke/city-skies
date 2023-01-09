from ws2812b_utils import sicgl_interface_to_spi_bitstream


class WS2812B_SPI:
    DEFAULT_SPI_HOST = 2  # vspi
    ORDER = (1, 0, 2, 3)
    RESET_BUF = bytearray(16)

    def __init__(self, pins, screen, spi_host=DEFAULT_SPI_HOST):
        from machine import SPI, Pin

        (self.sck, self.mosi, self.miso) = pins
        self.bus = SPI(
            spi_host,
            2500000,
            sck=Pin(self.sck),
            mosi=Pin(self.mosi),
            miso=Pin(self.miso),
            polarity=0,
            phase=0,
            bits=8,
            firstbit=0,
        )
        self.buf = bytearray(9 * screen.pixels)

    def ingest(self, interface):
        sicgl_interface_to_spi_bitstream(interface, self.buf)

    def push(self):
        # NOTE: there is some *actual bullshit* happening between the spi driver and the network interface, somehow
        # when the spi driver is made to be non-blocking (by commenting out code in mpy machine_hw_spi.c which waits for transactions to finish) _most_ writes to it cause the network to fail to get ota updates...
        # when the driver is restored to blocking it works fine but a lot of time is wasted (causing a host of other issues)
        self.bus.write(self.RESET_BUF)  # shift out a reset signal (all low)
        self.bus.write(self.buf)  # use the bus to shift out the data

        # NOTE: for the time being this is blocking code and takes approx 9.6 us per byte of pixel data (that's 900 bytes for 300 leds which would equate to 8.6 ms)
        # NOTE: it would be really nice to make this code back into non-blocking...
