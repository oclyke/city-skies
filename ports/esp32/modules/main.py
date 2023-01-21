import uasyncio as asyncio
import profiling
import framerate
import board
import sicgl
import machine
import early


# import json
# import uasyncio

# from net.utils import fetch, fetch_stream, HTTPResponse
# from ota import otainfo
# from ver import ver, VER
# from ota import ESP32OTA, otainfo
# from ble import ble
# import board

# FIRMWARE = "precious-time"


# def set_ota_info(download=None):
#     info = {
#         "version": ver.semver,
#         "available": otainfo.available.semver,
#         "next": {"version": otainfo.next.semver, "verified": otainfo.next.verified},
#     }
#     if download is not None:
#         info["download"] = download
#     ble.ota.info = json.dumps(info)


# async def init():
#     def cmd(data):
#         print("ble ota command: ", data)

#         if data == b"check":
#             uasyncio.create_task(check())

#         if data == b"download":
#             uasyncio.create_task(download())

#     ble.ota._register("cmd", cmd)

#     def update_ble_ota_info(value=None):
#         set_ota_info()

#     otainfo._register(update_ble_ota_info)
#     update_ble_ota_info()

#     print(f"'{FIRMWARE}' version: {ver.semver}")
#     if otainfo.next.semver is not None:
#         if not ver.precedes(otainfo.next.semver):
#             otainfo.next.semver = None
#             otainfo.next.verified = False


# async def check():
#     overrides = {
#         "protocol": "http"
#     }  # todo: fix ssl error with cloudfront so overrides are no longer needed
#     resp = await fetch(
#         f"https://ota.customlitt.com/api/v0/{board.UUID}/index.json", overrides
#     )

#     fwinfo = resp.json["firmware"][FIRMWARE]
#     stable = fwinfo["stable"]
#     if ver.precedes(stable):
#         print("a firmware update is available to: ", stable)
#         info = fwinfo["releases"][stable]

#         otainfo.available.semver = stable
#         otainfo.available.info = info

#         print("completed updating ota data")


# async def download():
#     if (otainfo.available.semver is None) or (
#         not ver.precedes(otainfo.available.semver)
#     ):
#         print("firmware update unavailable - try checking for updates later")
#         return

#     # check if update already exists
#     if otainfo.next.semver is not None:
#         if (
#             VER.match(otainfo.available.semver, otainfo.next.semver)
#             and otainfo.next.verified
#         ):
#             print(
#                 "update is already downloaded and verified - you may apply the update now (by rebooting)"
#             )
#             return

#     print("proceeding to apply firmware update")

#     # clear out next partition info
#     otainfo.next.semver = None
#     otainfo.next.verified = False

#     # get update source info
#     update = otainfo.available.info
#     size = update.size
#     ota = ESP32OTA()

#     def header_handler(data):
#         print("received header data")
#         print(data)

#     def body_handler(data):
#         if not data:
#             print("finishing ota update with sha256: ", update.sha256)
#             ota.finish(bytearray(update.sha256))

#             otainfo.next.semver = otainfo.available.semver
#             otainfo.next.verified = True

#             return
#         ota.ingest(data)
#         set_ota_info({"complete": False, "progress": f"{100*ota._processed/size:.2f}%"})
#         print("update: ", 100 * ota._processed / size, "%")

#     resp = HTTPResponse()
#     resp.set_header_handler(header_handler)
#     resp.set_body_handler(body_handler)

#     async def handler(data):
#         resp.ingest(data)

#     print("downloading update from: ", update.url)
#     await fetch_stream(
#         update.url, handler, overrides={"protocol": "http"}
#     )  # todo: resolve ssl issues so this override to http is not required

#     set_ota_info({"complete": True})
#     print("update downloaded + verified: reboot to apply")


framerate = framerate.FramerateHistory()


async def run_pipeline():
    # rate-limit the output
    rate_limit_flag = asyncio.ThreadSafeFlag()

    def timer_callback(self):
        rate_limit_flag.set()

    timer = machine.Timer(0)
    timer.init(period=30, callback=timer_callback)

    # make a timer for profiling
    profiler = profiling.ProfileTimer()

    # handle layers
    while True:
        # start timing
        profiler.set()

        # explicitly give other tasks processing time, in case
        # frame generation is using up the full output period
        await asyncio.sleep(0)

        # zero the canvas to prevent artifacts from previous render loops from leaking through
        # (sometimes it would be beneficial to persist the previous state,
        # but shards can do that by allocating their own memory as needed)
        early.canvas_interface.interface_fill(0x000000)

        # compute layers in reverse so that they can be composited into
        # the canvas in the same step
        for layer in early.expression_manager.active.layers:
            # zero the layer interface for each shard
            # (if a layer wants to use persistent memory it can do whacky stuff
            # such as allocating its own local interface and copying out the results)
            early.layer_interface.interface_fill(0x000000)

            # run the layer
            layer.run()

            # composite the layer's canvas into the main canvas
            early.canvas_interface.compose(
                board.display,
                early.layer_interface.memory,
                layer.info.get("composition_mode"),
            )

        # gamma correct the canvas
        sicgl.gamma_correct(early.canvas_interface, early.gamma_interface)

        # allow driver to reformat the interface memory as needed
        board.driver.ingest(early.gamma_interface)

        # compute framerate
        profiler.mark()
        framerate.record_period_ms(profiler.period_ms)

        # wait for the next output opportunity
        await rate_limit_flag.wait()

        # push the corrected canvas out to display
        board.driver.push()


async def serve_api():
    # configure maximum request size
    import microdot_asyncio
    import control_api

    # set up server
    PORT = 1337
    microdot_asyncio.Request.max_content_length = 32 * 1024  # 32 KB
    asyncio.create_task(control_api.app.start_server(debug=True, port=PORT))


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
    while True:
        await asyncio.sleep(5)
        print(
            f"{framerate.average} fps, ({len(early.expression_manager.active.layers)} layers)"
        )


async def main():
    # set up watchdog timer
    wdt = machine.WDT(timeout=2000)

    # start the pipeline as soon as possible and provide it a chance to run
    asyncio.create_task(run_pipeline())
    wdt.feed()
    await asyncio.sleep(0)
    wdt.feed()
    await asyncio.sleep(0)

    # create async tasks
    asyncio.create_task(serve_api())
    asyncio.create_task(poll_network_status())
    asyncio.create_task(blink())
    if board.board_task is not None:
        asyncio.create_task(board.board_task())

    # set up BLE
    wdt.feed()
    from singletons import ble, network_manager
    from ble_services import ADV_UUID_CITY_SKIES

    wdt.feed()
    ble.add_write_handler(
        ble.netcfg_handles["mode"], lambda v: network_manager.set_mode(v.decode())
    )
    ble.add_write_handler(
        ble.netcfg_handles["active"],
        lambda v: network_manager.set_active(True if v == b"true" else False),
    )

    wdt.feed()
    ble.add_write_handler(
        ble.netcfg_handles["sta_ssid"],
        lambda v: network_manager.station.set_ssid(v.decode()),
    )
    ble.add_write_handler(
        ble.netcfg_handles["sta_pass"],
        lambda v: network_manager.station.set_password(v.decode()),
    )

    wdt.feed()
    ble.add_write_handler(
        ble.netcfg_handles["ap_ssid"],
        lambda v: network_manager.access_point.set_ssid(v.decode()),
    )
    ble.add_write_handler(
        ble.netcfg_handles["ap_pass"],
        lambda v: network_manager.access_point.set_password(v.decode()),
    )

    wdt.feed()
    ble.write(ble.netcfg_handles["sta_ipaddr"], network_manager.station.ipaddr)
    ble.write(ble.netcfg_handles["ap_ipaddr"], network_manager.access_point.ipaddr)

    wdt.feed()
    ble.advertise([ADV_UUID_CITY_SKIES])

    # the main task should not return so that asyncio continues to handle tasks
    wdt.feed()
    while True:
        await asyncio.sleep(1)

        # feed the watchdog
        wdt.feed()


# run asyncio scheduler
asyncio.run(main())
