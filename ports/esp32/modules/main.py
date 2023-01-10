import uasyncio as asyncio
from framerate import FramerateHistory
from singletons import expression_manager


framerate = FramerateHistory()


async def run_pipeline():
    from singletons import (
        layer_interface,
        canvas_interface,
        gamma_interface,
        layer_memory,
    )
    from uasyncio import ThreadSafeFlag
    from board import display, driver
    from profiling import ProfileTimer
    from machine import Timer
    import sicgl

    # rate-limit the output
    rate_limit_flag = ThreadSafeFlag()

    def timer_callback(self):
        rate_limit_flag.set()

    timer = Timer(0)
    timer.init(period=30, callback=timer_callback)

    # make a timer for profiling
    profiler = ProfileTimer()

    # handle layers
    while True:
        # start timing
        profiler.set()

        # zero the canvas to prevent artifacts from previous render loops
        # from leaking through
        # (sometimes it would be beneficial to persist the previous state,
        # but shards can do that by allocating their own memory as needed)
        canvas_interface.interface_fill(0x000000)

        # compute layers in reverse so that they can be composited into
        # the canvas in the same step
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

        # allow driver to reformat the interface memory as needed
        driver.ingest(gamma_interface)

        # compute framerate
        profiler.mark()
        framerate.record_period_ms(profiler.period_ms)

        # wait for the next output opportunity
        await rate_limit_flag.wait()

        # push the corrected canvas out to display
        driver.push()


async def serve_api():

    # connect to the network
    import network

    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect("magnolia", "maxwellyke1999")

    while not sta_if.isconnected():
        print("waiting for network...")
        await asyncio.sleep(1)

    print(sta_if.ifconfig())

    # set up server
    PORT = 1337

    # configure maximum request size
    from microdot_asyncio import Request

    Request.max_content_length = 32 * 1024  # 32 KB

    from control_api import app

    asyncio.create_task(app.start_server(debug=True, port=PORT))


async def blink():
    while True:
        await asyncio.sleep(5)
        print(
            f"{framerate.average} fps, ({len(expression_manager.active.layers)} layers)"
        )


async def main():
    # create async tasks
    asyncio.create_task(run_pipeline())
    asyncio.create_task(serve_api())
    asyncio.create_task(blink())

    # the main task should not return so that asyncio continues to handle tasks
    while True:
        await asyncio.sleep(1)


# run asyncio scheduler
asyncio.run(main())
