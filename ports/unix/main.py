import uasyncio as asyncio
from microdot_asyncio import Microdot, send_file, Request, Response
from semver import SemanticVersion
from shard import ShardManager
from speed import speed_manager
from audio import audio_manager, AudioSource
import os

# constants
hw_version = SemanticVersion.from_semver("0.0.0-unix")
fw_version = SemanticVersion.from_semver("0.0.0")
api_version = SemanticVersion.from_semver("0.0.0")

# shard manager
shard_manager = ShardManager("runtime/shards")

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


async def run_pipeline():
    # set up output
    import sicgl

    WIDTH = 22
    HEIGHT = 13
    screen = sicgl.Screen((WIDTH, HEIGHT))
    memory = sicgl.allocate_memory(screen)
    canvas_interface = sicgl.Interface(screen, memory)

    # memory into which to place the gamma corrected output
    gamma_memory = sicgl.allocate_memory(screen)
    gamma_interface = sicgl.Interface(screen, gamma_memory)

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

    # make a tool to reverse a list
    # (too lazy to do it for real, this is meant to be illustrative)
    # ((* es eeh-loo-straw-teeve *))
    def reverse(iter):
        return iter

    # handle layers
    while True:
        # compute layers in reverse so that they can be composited into
        # the canvas in the same step
        for layer in reverse(layers):

            # run the layer
            await layer.run()

            # composite the layer's canvas into the main canvas
            canvas_interface.compose(
                layer.canvas.screen, layer.canvas.memory, layer.composition_mode
            )

        # gamma correct the canvas
        sicgl.gamma_correct(canvas_interface, gamma_interface)

        # # push the corrected canvas out to display
        # display.push(gamma_interface.memory)

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


@app.get("/hardware/version")
async def get_hw_version(request):
    return Response(hw_version.to_string())


@app.get("/firmware/version")
async def get_fw_version(request):
    return Response(fw_version.to_string())


@app.get("/api/version")
async def get_api_version(request):
    return Response(api_version.to_string())


@app.get("/identity/tag")
async def get_tag(request):
    return Response(identity.tag)


@app.put("/identity/tag")
async def set_tag(request):
    identity.tag = request.body.decode()


@app.get("/shards")
async def get_shards(request):
    return Response(shard_manager.shards)


@app.put("/shard/<name>")
async def add_shard_source(request, name):
    shard_manager.store_shard(name, {}, request.body.decode())


@app.get("/speed/variables")
async def get_speed_variables(request):
    return Response(list(speed_manager.variables.keys()))


@app.get("/speed/variable/<name>")
async def get_speed_variable(request, name):
    print("getting speed variable: ", name)
    return Response(speed_manager.variables[name].serialize())


@app.get("/audio/sources")
async def get_speed_variables(request):
    return Response(list(audio_manager.sources.keys()))


@app.get("/audio/source/<source>/volume")
async def get_audio_source_volume(request, source):
    return Response(str(audio_manager.sources[source].volume))


@app.put("/audio/source/<source>/volume")
async def set_audio_source_volume(request, source):
    audio_manager.sources[source].volume = request.body.decode()


async def mock_audio_source():
    sample_frequency = 16000
    sample_length = 256
    source = AudioSource("SineTest", (sample_frequency, sample_length))

    # register this audio source
    audio_manager.register_source(source)

    import math

    def sine_wave(freq, sample_freq):
        # the time period between each step is 1/sample_freq seconds long
        # one full cycle should take 1/freq seconds
        count = 0
        while True:
            phase = count / sample_freq
            # weird note: I thought this should be 2 * math.pi but no matter what I do
            # I get a frequency that is double what I expected, so for now let's just
            # use math.pi
            yield math.sin(math.pi * freq * phase)
            count += 1
            if count > sample_freq:
                count = 0

    # make the test signal
    sine_400hz = sine_wave(8000, sample_frequency)

    # output to view the fft strengths
    strengths = [0.0] * 32

    while True:
        # simulate waiting for a real audio source to fill the buffer
        for idx in range(sample_length):
            source._samples[idx] = next(sine_400hz)
        await asyncio.sleep(sample_length / sample_frequency)

        # now that the audio source is filled with data compute the fft
        source.compute_fft()
        stats = source.fft_stats
        _, _, max_idx = stats
        bin_width = source.fft_bin_width
        strongest_freq = max_idx * source.fft_bin_width
        source.get_fft_strengths(strengths)

        # print(strengths)
        # print('')
        # print(stats, bin_width, strongest_freq)


async def blink():
    import time

    while True:
        print("blink: ", time.ticks_ms(), "ms")
        await asyncio.sleep(3)


async def main():
    # create async tasks
    asyncio.create_task(app.start_server(debug=True, port=PORT))
    asyncio.create_task(run_pipeline())
    asyncio.create_task(mock_audio_source())
    asyncio.create_task(blink())

    # the main task should not return so that asyncio continues to handle tasks
    while True:
        await asyncio.sleep(1)


# run asyncio scheduler
asyncio.run(main())
