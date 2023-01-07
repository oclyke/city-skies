import time

boot_time_ms = time.ticks_ms()
first_light = True

import sicgl
import uasyncio as asyncio
from singletons import expression_manager
from singletons import canvas_interface, gamma_interface, layer_memory, display


async def run_pipeline():
    # rate-limit the output
    output_event = (
        asyncio.Event()
    )  # on esp32 this would be a threadsafe flag set in a timer callback

    async def rate_limiter(period_ms):
        import time

        next_frame_ticks_ms = time.ticks_ms() + period_ms
        while True:
            # wait for next time
            while time.ticks_ms() < next_frame_ticks_ms:
                await asyncio.sleep(0)

            # signal
            output_event.set()
            next_frame_ticks_ms = time.ticks_ms() + period_ms

    FRAME_PERIOD_MS = 1000
    asyncio.create_task(rate_limiter(FRAME_PERIOD_MS))

    # make a tool to reverse a list
    # (too lazy to do it for real, this is meant to be illustrative)
    # ((* es eeh-loo-straw-teeve *))
    def reverse(iter):
        return iter

    # handle layers
    while True:
        # compute layers in reverse so that they can be composited into
        # the canvas in the same step
        for layer in reverse(expression_manager.active.layers):

            # run the layer
            layer.run()

            # composite the layer's canvas into the main canvas
            canvas_interface.compose(display, layer_memory, layer.composition_mode)

        # gamma correct the canvas
        sicgl.gamma_correct(canvas_interface, gamma_interface)

        # # push the corrected canvas out to display
        # display.push(gamma_interface.memory)

        global first_light
        if first_light:
            global boot_time_ms
            first_light = False
            first_time_ms = time.ticks_ms()
            print("time to first light: ", time.ticks_diff(first_time_ms, boot_time_ms))

        # wait for the next output opportunity
        await output_event.wait()
        output_event.clear()


async def blink():
    import time

    while True:
        print("blink: ", time.ticks_ms(), "ms")
        await asyncio.sleep(3)


async def serve_api():
    # set up server
    PORT = 1337

    # configure maximum request size
    from microdot_asyncio import Request

    Request.max_content_length = 128 * 1024  # 128 KB

    from control_api import app

    asyncio.create_task(app.start_server(debug=True, port=PORT))


async def main():
    from mock_audio import mock_audio_source

    # create async tasks
    asyncio.create_task(run_pipeline())
    asyncio.create_task(mock_audio_source())
    asyncio.create_task(serve_api())
    asyncio.create_task(blink())

    # the main task should not return so that asyncio continues to handle tasks
    while True:
        await asyncio.sleep(1)


# run asyncio scheduler
asyncio.run(main())
