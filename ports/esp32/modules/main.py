import uasyncio as asyncio
from framerate import FramerateHistory
from singletons import expression_manager
from board import board_task


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
    # configure maximum request size
    from microdot_asyncio import Request
    from control_api import app

    # set up server
    PORT = 1337
    Request.max_content_length = 32 * 1024  # 32 KB
    asyncio.create_task(app.start_server(debug=True, port=PORT))


async def poll_network_status():
    from singletons import ble, network_manager

    prev = network_manager.wlan.isconnected()
    while True:
        await asyncio.sleep(1)
        current = network_manager.wlan.isconnected()
        if prev != current:
            print("net status changed: ", current, network_manager.wlan.ifconfig())

            ble.write(ble.netcfg_handles["sta_ipaddr"], network_manager.station.ipaddr)
            ble.notify(ble.netcfg_handles["sta_ipaddr"])

            ble.write(
                ble.netcfg_handles["ap_ipaddr"], network_manager.access_point.ipaddr
            )
            ble.notify(ble.netcfg_handles["ap_ipaddr"])
        prev = current


async def blink():
    from singletons import network_manager

    while True:
        await asyncio.sleep(5)
        print(
            f"{framerate.average} fps, ({len(expression_manager.active.layers)} layers)"
        )


async def main():
    import machine

    # set up watchdog timer
    wdt = machine.WDT(timeout=2000)

    # create async tasks
    asyncio.create_task(run_pipeline())
    asyncio.create_task(serve_api())
    asyncio.create_task(poll_network_status())
    asyncio.create_task(blink())
    if board_task is not None:
        asyncio.create_task(board_task())

    # set up BLE
    from singletons import ble, network_manager
    from ble_services import ADV_UUID_CITY_SKIES

    ble.add_write_handler(
        ble.netcfg_handles["mode"], lambda v: network_manager.set_mode(v.decode())
    )
    ble.add_write_handler(
        ble.netcfg_handles["active"],
        lambda v: network_manager.set_active(True if v == b"true" else False),
    )

    ble.add_write_handler(
        ble.netcfg_handles["sta_ssid"],
        lambda v: network_manager.station.set_ssid(v.decode()),
    )
    ble.add_write_handler(
        ble.netcfg_handles["sta_pass"],
        lambda v: network_manager.station.set_password(v.decode()),
    )

    ble.add_write_handler(
        ble.netcfg_handles["ap_ssid"],
        lambda v: network_manager.access_point.set_ssid(v.decode()),
    )
    ble.add_write_handler(
        ble.netcfg_handles["ap_pass"],
        lambda v: network_manager.access_point.set_password(v.decode()),
    )

    ble.write(ble.netcfg_handles["sta_ipaddr"], network_manager.station.ipaddr)
    ble.write(ble.netcfg_handles["ap_ipaddr"], network_manager.access_point.ipaddr)

    ble.advertise([ADV_UUID_CITY_SKIES])

    # the main task should not return so that asyncio continues to handle tasks
    while True:
        await asyncio.sleep(1)

        # feed the watchdog
        wdt.feed()


# run asyncio scheduler
asyncio.run(main())
