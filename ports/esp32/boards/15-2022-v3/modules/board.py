import sicgl
from ws2812b_spi import WS2812B_SPI

# unique board identifier
# (identifies a single hardware configuration)
UUID = "d89d2bbd-d65c-4ec0-abd7-9967e0a461dd"

# diplay hardware
display = sicgl.Screen((23, 13))
driver = WS2812B_SPI((18, 23, 19), display)
