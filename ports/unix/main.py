import sicgl
import uasyncio as asyncio
from microdot_asyncio import Microdot, send_file, Request, Response
from semver import SemanticVersion
from shard import ShardManager
from speed import speed_manager
from audio import audio_manager, AudioSource
from cache import Cache
from variables import VariableResponder

# constants
hw_version = SemanticVersion.from_semver("0.0.0-unix")
fw_version = SemanticVersion.from_semver("0.0.0")
api_version = SemanticVersion.from_semver("0.0.0")

# diplay hardware
WIDTH = 22
HEIGHT = 13

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


class Layer:
    def __init__(self, expression, id, interface):
        # layers require a parent expression
        self._expression = expression
        self._id = id

        # the root path for this layer will not change during its lifetime
        self._root_path = f"{self._expression._layers_path}/{self._id}"
        self._vars_path = f"{self._root_path}/vars"
        self._info_path = f"{self._root_path}/info"

        # a sicgl interface will be provided
        self._interface = interface

        # set defaults for shard execution
        self._ready = False
        self._frame_generator_obj = None

        # variables which may be dynamically registered for external control
        self._variables = {}
        self._variable_responder = VariableResponder(
            lambda name, value: self.store_variable_value(name, value)
        )

        # ensure that variables will have a directory
        from pathutils import ensure_dirs

        ensure_dirs(self._vars_path)

        # info recorded in a cache
        # (this must be done after default values are set because it will automatically enable the module if possible)
        initial_info = {
            "active": True,
            "shard": None,
            "composition_mode": 1,
            "palette": None,
            "index": None,
        }
        self._info = Cache(
            f"{self._root_path}/info",
            initial_info,
            lambda key, value: self._handle_info_change(key, value),
        )

    def _load_shard(self, uuid):
        if uuid is not None:
            module = shard_manager.get_shard_module(uuid)
            self._frame_generator_obj = module.frames(self)
            self._ready = True

    def _handle_info_change(self, key, value):
        print(f"({self}) layer info changed. [{key}]: {value}")
        if key == "shard":
            self._load_shard(value)

    @property
    def id(self):
        return self._id

    @property
    def shard(self):
        return self._info.get("shard")

    @shard.setter
    def shard(self, uuid):
        self._info.set("shard", uuid)

    @property
    def active(self):
        return self._info.get("active")

    @active.setter
    def active(self, value):
        self._info.set("active", value)

    @property
    def composition_mode(self):
        return self._info.get("composition_mode")

    @composition_mode.setter
    def composition_mode(self, mode):
        self._info.set("composition_mode", mode)

    @property
    def index(self):
        return self._info.get("index")

    @index.setter
    def index(self, value):
        self._info.set("index", value)

    def store_variable_value(self, name, value):
        with open(f"{self._vars_path}/{name}", "w") as f:
            f.write(str(value))

    def load_variable_value(self, name):
        with open(f"{self._vars_path}/{name}", "r") as f:
            return str(f.read())

    def declare_variable(self, cls, *args, **kwargs):
        """
        This method allows automatic association of a declared variable
        to this layer so that it may be properly cached.
        """
        # create the variable
        var = cls(*args, **kwargs, responder=self._variable_responder)

        # register it into the layer's list
        self._variables[var.name] = var

        # try loading an existing value for the registered variable
        try:
            var.value = self.load_variable_value(var.name)
        except:
            pass

        # finally store the current value
        self.store_variable_value(var.name, var.value)

        return var

    def run(self):
        """
        Gets the next frame from the frame generator object, only if the layer is ready and active
        """
        if self._ready and self.active:
            next(self._frame_generator_obj)


class Expression:
    @staticmethod
    def layer_id_generator(path):
        """
        This generator gets the next layer id given the path to a dir containing
        layer directories with numeric decimal names in ascending order.
        """
        import os

        id = 0
        while True:

            try:
                os.stat(f"{path}/layers/{id}")
                id += 1
            except:
                yield id

    def __init__(self, path, interface):
        from pathutils import ensure_dirs
        import os

        self._path = path
        self._layers_path = f"{self._path}/layers"
        self._layer_id_generator = Expression.layer_id_generator(self._path)

        # store a reference to the interface that will be passed to layers
        self._interface = interface

        # ensure that a directory exists for layers
        ensure_dirs(self._layers_path)

        # layer map allows access to layers by id while layer stack
        # maintains the order of layers in composition
        self._layer_map = {}
        self._layer_stack = []

        # load layers from the filesystem
        for id in os.listdir(self._layers_path):
            layer = self._make_layer(id)
            self._layer_map[id] = layer
            self._layer_stack.append(layer)

        # now arrange the layers by index
        self._arrange_layers_by_index()

    def _arrange_layers_by_index(self):
        # sort the layers in the stack by index
        self._layer_stack.sort(key=lambda layer: layer.index)

    def _recompute_layer_indices(self):
        for idx, layer in enumerate(self._layer_stack):
            layer.index = idx

    def _make_layer(self, id):
        return Layer(self, id, self._interface)

    def add_layer(self, shard):
        import os

        id = next(self._layer_id_generator)
        os.mkdir(f"{self._layers_path}/{id}")
        layer = self._make_layer(id)
        layer.shard = shard
        self._layer_stack.append(layer)
        self._layer_map[str(id)] = layer
        self._recompute_layer_indices()

    def move_layer_to_index(self, id, dest_idx):
        original_index = self._layer_map[id].index
        self._layer_stack.insert(dest_idx, self._layer_stack.pop(original_index))
        self._recompute_layer_indices()

    def get_layer_index(self, id):
        return self.layer_map[id].index

    def remove_layer(self, id):
        import os

        os.rmdir(f"{self._layers_path}/{id}")

    def clear_layers(self):
        """remove all layers"""
        self._layer_stack = []
        self._layer_map = {}
        import os
        from pathutils import rmdirr

        rmdirr(self._layers_path)
        os.mkdir(self._layers_path)

    @property
    def layers(self):
        return self._layer_stack


# sicgl interfaces
screen = sicgl.Screen((WIDTH, HEIGHT))
memory = sicgl.allocate_memory(screen)
canvas_interface = sicgl.Interface(screen, memory)

# memory into which to place the gamma corrected output
gamma_memory = sicgl.allocate_memory(screen)
gamma_interface = sicgl.Interface(screen, gamma_memory)

# memory for intermediate layer action
layer_memory = sicgl.allocate_memory(screen)
layer_interface = sicgl.Interface(screen, layer_memory)

# define expressions
expressionA = Expression("runtime/expressions/A", layer_interface)
expressionB = Expression("runtime/expressions/B", layer_interface)

# make references for active and inactive expressions
expressions = {
    "active": None,
    "inactive": None,
}

# a tool to activate an expression while simultaneously deactivating the other
def activate_expression(name):
    global expressions
    if name == "A":
        expressions["active"] = expressionA
        expressions["inactive"] = expressionB
    elif name == "B":
        expressions["active"] = expressionB
        expressions["inactive"] = expressionA
    else:
        raise ValueError


# expression selection information
def onExpressionCacheChange(key, value):
    if key == "active":
        activate_expression(value)


expressions_cache = Cache(
    "runtime/expressions/info", {"active": "A"}, onExpressionCacheChange
)


async def run_pipeline():
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

    FRAME_PERIOD_MS = 1000
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
        for layer in reverse(expressions["active"].layers):

            # run the layer
            layer.run()

            # composite the layer's canvas into the main canvas
            canvas_interface.compose(screen, layer_memory, layer.composition_mode)

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
# curl -H "Content-Type: text/plain" -X POST http://localhost:1337/upload -d 'demo_dynamic_module'
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


# curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/expressions/info/active -d 'A'
@app.put("/expressions/info/active")
async def set_expression_active(request):
    name = str(request.body.decode())
    if name in ["A", "B"]:
        expressions_cache.set("active", name)
    else:
        return Response(status_code=406)


@app.post("/expressions/<expression>/layer")
async def add_layer(request, expression):
    shard = request.body.decode()
    expressions[expression].add_layer(shard)


@app.put("/expressions/<expression>/layer/<id>/index")
async def set_layer_index(request, expression, id):
    index = request.body.decode()
    expressions[expression].move_layer_to_index(id, int(index))


@app.delete("/expressions/<expression>/layer/<id>")
async def delete_layer(request, expression, id):
    expressions[expression].remove_layer(id)


@app.delete("/expressions/<expression>/layers")
async def clear_layers(request, expression):
    expressions[expression].clear_layers()


# curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/shards/14e84711-7627-40a5-97ae-11fd5ff3b607 -d $'def frames(l):\n\twhile True:\n\t\tyield None\n\t\tprint("hello world")\n\n'
@app.put("/shards/<uuid>")
async def store_shard(request, uuid):
    shard_manager.store_shard(uuid, request.body.decode())


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
