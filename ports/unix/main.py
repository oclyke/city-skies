import uasyncio as asyncio
import socket
import time
import json
import os
import sys

import cache
import pysicgl
import framerate
import profiling
import hardware
import pathutils
import config

from semver import SemanticVersion
from stack_manager import StackManager
from mock_audio import mock_audio_source
from microdot_asyncio import Microdot, Response, Request
from hidden_shades.layer import Layer
from hidden_shades import globals
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

        # zero the canvas to prevent artifacts from previous render loops
        # from leaking through
        # (sometimes it would be beneficial to persist the previous state,
        # but shards can do that by allocating their own memory as needed)
        canvas.interface_fill(0x000000)

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
            visualizer.compose(display, canvas_memory, layer.info["composition_mode"])

        # apply global brightness
        visualizer.interface_scale(globals.variables["brightness"].value)

        # gamma correct the canvas
        pysicgl.gamma_correct(visualizer, corrected)

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
    # set up server
    PORT = 1337

    # configure maximum request size
    Request.max_content_length = 128 * 1024  # 128 KB

    control_api_version = SemanticVersion.from_semver("0.0.0")
    app = Microdot()
    asyncio.create_task(app.start_server(debug=True, port=PORT))

    def get_list(l):
        return "\n".join(l)

    # curl -H "Content-Type: text/plain" -X GET http://localhost:1337/info
    @app.get("/info")
    async def get_info(request):
        info = {
            "hw_version": hardware.hw_version.to_string(),
        }
        return Response(info)

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

    # curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/globals/vars/<varname> -d 'value'
    @app.put("/globals/vars/<varname>")
    async def put_global_variable(request, varname):
        globals.variables[varname].value = request.body.decode()

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
    asyncio.create_task(mock_audio_source())
    asyncio.create_task(serve_api())
    asyncio.create_task(blink())

    # the main task should not return so that asyncio continues to handle tasks
    while True:
        await asyncio.sleep(1)


# run asyncio scheduler
asyncio.run(main())
