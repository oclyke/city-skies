import pysicgl
import snake
import ws2812b_spi
import config

from audio_ics43432 import ICS43432AudioSource

# unique board identifier
# (identifies a single hardware configuration)
UUID = "ac79bb5e-dc0c-4799-bcc4-2587fd898faf"

# diplay hardware
display = pysicgl.Screen((23, 13))
driver = snake.SnakeDriver(
    display, ws2812b_spi.WS2812B_SPI((18, 23, 19), display.pixels)
)

# audio sources
audio_source_root_path = f"{config.EPHEMERAL_DIR}/audio/sources"
audio_sources = [
    ICS43432AudioSource(audio_source_root_path, "mic", (16000, 512), (14, 13, 34))
]


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
