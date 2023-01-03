import uasyncio as asyncio
from microdot_asyncio import Microdot, send_file, Request, Response
from semver import SemanticVersion
import os

# constants
hw_version = SemanticVersion.from_semver("0.0.0-unix")
fw_version = SemanticVersion.from_semver("0.0.0")

# configured values
class IdentityInfo:
    def __init__(self, path):
        self._path = path
        self._tag = None

    @property
    def tag(self):
        if self._tag is None:
            try:
                with open(f"{self._path}/tag", "r") as f:
                    self._tag = str(f.read())
            except:
                self._tag = ""
        return self._tag

    @tag.setter
    def tag(self, value):
        with open(f"{self._path}/tag", "w") as f:
            f.write(str(value))


identity = IdentityInfo("runtime/identity")


class Layer:
    READY = 0
    EXCEPTION = 1

    def __init__(self, shard):
        self._shard = shard
        self._state = Layer.READY
        self._exception = None

    async def run(self):
        if self._state == Layer.READY:
            try:
                await self._shard.run()
            except Exception as e:
                self.handle_exception(e)

    async def handle_exception(self, exception):
        self._state = Layer.EXCEPTION
        self._exception = exception
        raise exception


async def run_pipeline():
    # set up output
    import sicgl

    WIDTH = 22
    HEIGHT = 13
    screen = sicgl.Screen((WIDTH, HEIGHT))
    memory = sicgl.allocate_memory(screen)
    interface = sicgl.Interface(screen, memory)

    # set up layers
    layers = []

    # # make a demo shard
    # # (in reality this will be dynamically loaded from the controller)
    # shard = __import__('demo_shard')
    # layers.append(Layer(shard))

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

    FRAME_PERIOD_MS = 100
    asyncio.create_task(rate_limiter(FRAME_PERIOD_MS))

    # handle layers
    while True:
        for layer in layers:
            await layer.run()  # run the layer
            # layer.compose() # compose the output

        # wait for the next output opportunity
        await output_event.wait()
        output_event.clear()


# set up server
PORT = 1337
app = Microdot()
Request.max_content_length = 128 * 1024  # 128 KB

# an endpoint to which the user can send module names
# curl -d 'demo_dynamic_module' -H "Content-Type: text/plain" -X POST http://localhost:1337/upload
@app.post("/upload")
async def upload(request):
    # decode the payload assuming utf-8
    name = request.body.decode()
    print("importing: ", name)

    # import that module
    module = __import__(name)


@app.get("/identity/tag")
async def get_tag(request):
    return Response(identity.tag)


@app.put("/identity/tag")
async def set_tag(request):
    identity.tag = request.body.decode()


async def blink():
    import time

    while True:
        print("blink: ", time.ticks_ms(), "ms")
        await asyncio.sleep(3)


async def main():
    # create async tasks
    asyncio.create_task(app.start_server(debug=True, port=PORT))
    asyncio.create_task(run_pipeline())
    asyncio.create_task(blink())

    # the main task should not return so that asyncio continues to handle tasks
    while True:
        await asyncio.sleep(1)


# run asyncio scheduler
asyncio.run(main())
