import uasyncio as asyncio


async def run_pipeline():
    from machine import Timer
    from uasyncio import ThreadSafeFlag
    from singletons import (
        expression_manager,
        canvas_interface,
        gamma_interface,
        layer_memory,
    )
    from board import display, driver
    import sicgl

    # rate-limit the output
    rate_limit_flag = ThreadSafeFlag()

    def timer_callback(self):
        rate_limit_flag.set()

    timer = Timer(0)
    timer.init(period=30, callback=timer_callback)

    # handle layers
    while True:
        # compute layers in reverse so that they can be composited into
        # the canvas in the same step
        for layer in expression_manager.active.layers_reversed:

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


async def main():
    # create async tasks
    asyncio.create_task(run_pipeline())
    asyncio.create_task(serve_api())

    # the main task should not return so that asyncio continues to handle tasks
    while True:
        await asyncio.sleep(1)


# run asyncio scheduler
asyncio.run(main())
