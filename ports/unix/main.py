import uasyncio as asyncio
import socket
import time
from microdot_asyncio import Microdot, Request, Response

import cache
import pysicgl
import framerate
import profiling
import hardware
import hidden_shades
import pathutils
import config

from stack_manager import StackManager
from hidden_shades.layer import Layer
from hidden_shades import globals, artnet_provider
from logging import LogManager

logger = LogManager(f"{config.PERSISTENT_DIR}/logs")


def factory_reset():
    print("restoring factory defaults...", end="")
    pathutils.rmdirr(config.EPHEMERAL_DIR)
    print("done")


def exception_handler(loop, context):
    exc = context["exception"]
    logger.log_exception(exc)
    raise exc


# load hardware config
hw_config = cache.Cache(
    f"{config.PERSISTENT_DIR}/hw_config",
    {
        "width": 33,
        "height": 32,
    },
)


# make pysicgl interfaces
def create_interface(screen):
    mem = pysicgl.allocate_pixel_memory(screen.pixels)
    interface = pysicgl.Interface(screen, mem)
    return (interface, mem)


display = pysicgl.Screen((hw_config.get("width"), hw_config.get("height")))
visualizer, visualizer_memory = create_interface(display)
corrected, corrected_memory = create_interface(display)
canvas, canvas_memory = create_interface(display)


# function to load a given shard uuid and return the module
def load_shard(uuid):
    return __import__(f"{config.PERSISTENT_DIR}/shards/{uuid}")


# a function which sets the shard for a given layer after
# initialization
def layer_post_init_hook(layer):
    uuid = layer.info.get("shard_uuid")
    shard = load_shard(uuid)
    layer.set_shard(shard)
    layer.initialize_frame_generator()


# a function called for each layer in the stack upon creation
# this allows the program to keep the details of loading shards
# separate from the job of the Stack class
def stack_initializer(id, path):
    return Layer(id, path, canvas, post_init_hook=layer_post_init_hook)


# define stacks
stack_manager = StackManager(f"{config.EPHEMERAL_DIR}/stacks", stack_initializer)


frate = framerate.FramerateHistory()


async def run_pipeline():
    # make a timer for profiling the framerate
    profiler = profiling.ProfileTimer()

    # rate-limit the output
    output_event = asyncio.Event()

    async def rate_limiter(frequency):
        period_ms = 1000 / frequency

        next_frame_ms = time.ticks_ms() + period_ms
        while True:
            # wait for next time
            while time.ticks_ms() < next_frame_ms:
                await asyncio.sleep(0)

            # signal
            output_event.set()
            next_frame_ms += period_ms

    FRAMERATE = 30
    asyncio.create_task(rate_limiter(FRAMERATE))

    # handle layers
    while True:
        profiler.set()

        # zero the visualizer to prevent artifacts from previous render loops
        # from leaking through
        visualizer.interface_fill(pysicgl.ALPHA_TRANSPARENCY_FULL | 0x000000)

        # loop over all layers in the active stack manager
        for layer in stack_manager.active:
            # only compute active layers
            if layer.active:
                # zero the layer interface for each shard
                # (if a layer wants to use persistent memory it can do whacky stuff
                # such as allocating its own local interface and copying out the results)
                canvas.interface_fill(pysicgl.ALPHA_TRANSPARENCY_FULL | 0x000000)

                # run the layer
                try:
                    layer.run()
                except Exception as e:
                    logger.log_exception(e)
                    layer.set_active(False)

                # # blending is broken right now
                # canvas.blend(display, visualizer_memory, layer.blending_mode)

                # compose the canvas memory onto the visualizer memory
                visualizer.compose(display, canvas_memory, layer.composition_mode)

        # gamma correct the canvas
        pysicgl.gamma_correct(visualizer, corrected)

        # apply global brightness
        corrected.interface_scale(
            globals.variable_manager.variables["brightness"].value
        )

        # output the display data
        for driver in hardware.drivers:
            driver.push(corrected)

        # compute framerate
        profiler.mark()
        frate.record_period_ms(profiler.period_ms)

        # wait for the next output opportunity
        await output_event.wait()
        output_event.clear()


async def serve_api():
    from api import api_app, init_api_app, api_version

    # initialize the api app
    init_api_app(
        stack_manager,
        canvas,
        layer_post_init_hook,
    )

    # set up server
    PORT = 1337

    # configure maximum request size
    Request.max_content_length = 128 * 1024  # 128 KB
    Response.default_content_type = "application/json"

    # create application structure
    app = Microdot()
    app.mount(api_app, url_prefix="/api/v0")

    @app.get("/alive")
    async def get_alive(request):
        return None

    @app.get("/index")
    async def get_index(request):
        return {
            "hw_version": hardware.hw_version.to_string(),
            "api_version": api_version.to_string(),
            "api": {
                "latest": "v0",
                "versions": {
                    "v0": "/api/v0",
                },
            },
        }

    # serve the api
    asyncio.create_task(app.start_server(debug=True, port=PORT))


async def control_visualizer():
    # information about visualizer control server
    CONTROL_HOST = "0.0.0.0"
    CONTROL_PORT = 6969

    # format the control message which indicates the screen resolution
    config_message = f"{display.width} {display.height}\n"

    while True:
        try:
            # open a connection to the control server in the visualizer
            control = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            control.connect(socket.getaddrinfo(CONTROL_HOST, CONTROL_PORT)[0][-1])
            control.send(config_message.encode("utf-8"))
            control.close()
        except:
            pass
        await asyncio.sleep(5.0)


async def blink():
    while True:
        await asyncio.sleep(5)
        print(f"{frate.average()} fps, ({len(stack_manager.active)} layers)")


async def main():
    asyncio.get_event_loop().set_exception_handler(exception_handler)

    # create async tasks
    asyncio.create_task(run_pipeline())
    asyncio.create_task(control_visualizer())
    asyncio.create_task(serve_api())
    asyncio.create_task(blink())
    asyncio.create_task(artnet_provider.run())

    # start audio sources
    for source in hardware.audio_sources:
        print("Initializing audio source: ", source)
        hidden_shades.audio_manager.add_source(source)
        asyncio.create_task(source.run())

    # initialize the audio manager once all audio sources have been registered
    hidden_shades.audio_manager.initialize()

    # the main task should not return so that asyncio continues to handle tasks
    while True:
        await asyncio.sleep(1)


# run asyncio scheduler
asyncio.run(main())
