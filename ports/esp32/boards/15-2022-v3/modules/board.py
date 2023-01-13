import sicgl
import snake
import ws2812b_spi


# unique board identifier
# (identifies a single hardware configuration)
UUID = "d89d2bbd-d65c-4ec0-abd7-9967e0a461dd"

# diplay hardware
display = sicgl.Screen((23, 13))
driver = snake.SnakeDriver(
    display, ws2812b_spi.WS2812B_SPI((18, 23, 19), display.pixels)
)


async def board_task():
    import factory
    import uasyncio as asyncio
    import machine

    # a pin used to reset the board to factory settings
    frp = machine.Pin(25, machine.Pin.IN)
    frcount = 0

    while True:
        await asyncio.sleep(0.25)

        # handle factory reset reqeuests
        if not frp.value():
            frcount += 1
            if frcount > 3:
                factory.factory_reset()
                machine.reset()
        else:
            frcount = 0
