import uasyncio as asyncio
from framerate import FramerateHistory
from singletons import expression_manager


framerate = FramerateHistory()


async def run_pipeline():
    from singletons import (
        canvas_interface,
        gamma_interface,
        layer_interface,
        layer_memory,
        display,
    )
    from hardware import driver
    from profiling import ProfileTimer
    import sicgl

    # make a timer for profiling the framerate
    profiler = ProfileTimer()

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

    FRAME_PERIOD_MS = 30
    asyncio.create_task(rate_limiter(FRAME_PERIOD_MS))

    # handle layers
    while True:
        profiler.set()

        # zero the canvas to prevent artifacts from previous render loops
        # from leaking through
        # (sometimes it would be beneficial to persist the previous state,
        # but shards can do that by allocating their own memory as needed)
        canvas_interface.interface_fill(0x000000)

        for layer in expression_manager.active.layers:
            # zero the layer interface for each shard
            # (if a layer wants to use persistent memory it can do whacky stuff
            # such as allocating its own local interface and copying out the results)
            layer_interface.interface_fill(0x000000)

            # run the layer
            layer.run()

            # composite the layer's canvas into the main canvas
            canvas_interface.compose(
                display, layer_memory, layer.info.get("composition_mode")
            )

        # gamma correct the canvas
        sicgl.gamma_correct(canvas_interface, gamma_interface)

        # output the display data
        driver.push(gamma_interface)

        # compute framerate
        profiler.mark()
        framerate.record_period_ms(profiler.period_ms)

        # wait for the next output opportunity
        await output_event.wait()
        output_event.clear()


async def serve_api():
    # set up server
    PORT = 1337

    # configure maximum request size
    from microdot_asyncio import Request

    Request.max_content_length = 128 * 1024  # 128 KB

    from control_api import app

    asyncio.create_task(app.start_server(debug=True, port=PORT))


async def blink():
    while True:
        await asyncio.sleep(5)
        print(
            f"{framerate.average} fps, ({len(expression_manager.active.layers)} layers)"
        )


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
