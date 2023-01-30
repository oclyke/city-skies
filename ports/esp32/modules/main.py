import uasyncio as asyncio
import pysicgl
import framerate
import machine
import profiling
import semver
import netman
import csble
import config
import board

from stack_manager import StackManager
from hidden_shades.layer import Layer
from logging import LogManager

fw_version = semver.SemanticVersion.from_semver("0.0.0")
ble = csble.CSBLE()
network_manager = netman.NetworkManager(f"{config.EPHEMERAL_DIR}/network")


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


logger = LogManager(f"{config.PERSISTENT_DIR}/logs")


def exception_handler(loop, context):
    import factory
    import machine

    exc = context["exception"]
    logger.log_exception(exc)
    # factory.factory_reset()
    # machine.reset()
    raise exc


# make pysicgl interfaces
def create_interface(screen):
    mem = pysicgl.allocate_pixel_memory(screen.pixels)
    interface = pysicgl.Interface(screen, mem)
    return (interface, mem)


visualizer, visualizer_memory = create_interface(board.display)
corrected, corrected_memory = create_interface(board.display)
canvas, canvas_memory = create_interface(board.display)

# function to load a given shard uuid and return the module
def load_shard(uuid):
    return __import__(f"{config.PERSISTENT_DIR}/shards/{uuid}")


# a function which sets the shard for a given layer after
# initialization
def layer_post_init_hook(layer):
    uuid = layer.info.get("shard_uuid")
    shard = load_shard(uuid)
    layer.set_shard(shard)


# a function called for each layer in the stack upon creation
# this allows the program to keep the details of loading shards
# separate from the job of the Stack class
def stack_initializer(id, path):
    return Layer(id, path, canvas, post_init_hook=layer_post_init_hook)


# define stacks
stack_manager = StackManager(f"{config.EPHEMERAL_DIR}/stacks", stack_initializer)


frate = framerate.FramerateHistory()


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
        canvas.interface_fill(0x000000)

        # compute layers in reverse so that they can be composited into
        # the canvas in the same step
        for layer in stack_manager.active:
            # zero the layer interface for each shard
            # (if a layer wants to use persistent memory it can do whacky stuff
            # such as allocating its own local interface and copying out the results)
            canvas.interface_fill(0x000000)

            # run the layer
            try:
                layer.run()
            except Exception as e:
                logger.log_exception(e)
                layer.set_active(False)

            # composite the layer's canvas into the main canvas
            visualizer.compose(
                board.display, canvas_memory, layer.info["composition_mode"]
            )

        # gamma correct the canvas
        pysicgl.gamma_correct(visualizer, corrected)

        # allow driver to reformat the interface memory as needed
        board.driver.ingest(corrected)

        # compute framerate
        profiler.mark()
        frate.record_period_ms(profiler.period_ms)

        # wait for the next output opportunity
        await rate_limit_flag.wait()

        # push the corrected canvas out to display
        board.driver.push()


async def serve_api():
    import os
    import json
    import microdot_asyncio

    # set up server
    PORT = 1337
    control_api_version = semver.SemanticVersion.from_semver("0.0.0")
    app = microdot_asyncio.Microdot()

    def get_list(l):
        return "\n".join(l)

    # curl -H "Content-Type: text/plain" -X GET http://localhost:1337/info
    @app.get("/info")
    async def get_info(request):
        info = {
            "board_uuid": board.UUID,
        }
        return microdot_asyncio.Response(info)

    @app.get("/shards")
    async def get_shards(request):
        return get_list(os.listdir(f"{config.PERSISTENT_DIR}/shards"))

    @app.get("/stacks/<active>/layers")
    async def get_layers(request, active):
        stack = stack_manager.get(active)
        return get_list(layer.id for layer in stack)

    @app.get("/stacks/<active>/layers/<layerid>/variables")
    async def get_variables(request, active, layerid):
        stack = stack_manager.get(active)
        layer = stack.get_layer_by_id(layerid)
        return get_list(variable.name for variable in layer.variables.values())

    # curl -H "Content-Type: text/plain" -X POST http://localhost:1337/stacks/<active>/layer -d '{"shard_uuid": "noise"}'
    @app.post("/stacks/<active>/layer")
    async def put_stack_layer(request, active):
        data = json.loads(request.body.decode())
        stack = stack_manager.get(active)
        id, path, index = stack.get_new_layer_info()
        layer = Layer(
            id, path, canvas, init_info=data, post_init_hook=layer_post_init_hook
        )
        stack.add_layer(layer)

    # curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/stacks/<active>/layers/<layerid>/info -d '{"composition_mode": 3}'
    @app.put("/stacks/<active>/layers/<layerid>/info")
    async def put_layer_info(request, active, layerid):
        stack = stack_manager.get(active)
        layer = stack.get_layer_by_id(str(layerid))
        layer.merge_info(json.loads(request.body.decode()))

    # curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/stacks/<active>/layers/<layerid>/vars/<varname> -d 'value'
    @app.put("/stacks/<active>/layers/<layerid>/vars/<varname>")
    async def put_layer_variable(request, active, layerid, varname):
        stack = stack_manager.get(active)
        layer = stack.get_layer_by_id(str(layerid))
        layer.variables[varname].value = request.body.decode()

    # curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/shards/<uuid> -d $'def frames(l):\n\twhile True:\n\t\tyield None\n\t\tprint("hello world")\n\n'
    @app.put("/shards/<uuid>")
    async def put_shard(request, uuid):
        # shards are immutable once published, therefore if the specified UUID
        # exists on the filesystem it does not need to be written again
        path = f"{config.PERSISTENT_DIR}/shards/{uuid}"
        try:
            os.stat(path)
        except:
            with open(path, "w") as f:
                f.write(request.body)

    # configure maximum request size
    microdot_asyncio.Request.max_content_length = 128 * 1024  # 128 KB

    # start server
    asyncio.create_task(app.start_server(debug=True, port=PORT))


async def poll_network_status():
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
        print(f"{frate.average()} fps, ({len(stack_manager.active)} layers)")


async def main():
    # # set up watchdog timer
    # wdt = machine.WDT(timeout=2000)
    class FakeWatchdog:
        def feed(self):
            pass

    wdt = FakeWatchdog()
    wdt.feed()

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
    # if board.board_task is not None:
    #     asyncio.create_task(board.board_task())

    # set up BLE
    wdt.feed()
    from ble_services import ADV_UUID_CITY_SKIES

    wdt.feed()

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
