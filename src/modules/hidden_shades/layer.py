import pysicgl
from cache import Cache
from .variables.manager import VariableManager
from .variables.types import OptionVariable, FloatingVariable, ColorSequenceVariable
from .variables.responder import VariableResponder
from hidden_shades import globals
from pathutils import rmdirr


class Layer:
    BLENDING_MODE_OPTIONS = pysicgl.get_blending_types().keys()
    COMPOSITION_MODE_OPTIONS = pysicgl.get_composition_types().keys()

    DEFAULT_BLENDING_MODE = pysicgl.get_blending_types()['normal']
    DEFAULT_COMPOSITION_MODE = pysicgl.get_composition_types()['direct_set']

    def __init__(self, id, path, interface, init_info={}, post_init_hook=None):
        self.id = id

        # the root path for this layer will not change during its lifetime
        self._root_path = path
        self._vars_path = f"{self._root_path}/vars"
        self._info_path = f"{self._root_path}/info"

        # a pysicgl interface will be provided
        self.canvas = interface

        # the shard related items are left uninitialized
        # it is possible to set these in the post-init hook
        self._shard = None
        self._frame_generator_obj = None
        self._ready = False

        # static info does not change
        self._static_info = {
            "id": self.id,
        }

        # variables which may be dynamically registered for external control
        self._variable_manager = VariableManager(f"{self._root_path}/vars")

        # declare private variables
        self._private_variable_manager = VariableManager(
            f"{self._root_path}/private_vars"
        )
        self._private_variable_manager.declare_variable(
            OptionVariable(
                "blending_mode",
                Layer.DEFAULT_BLENDING_MODE,
                Layer.BLENDING_MODE_OPTIONS,
            )
        )
        self._private_variable_manager.declare_variable(
            OptionVariable(
                "composition_mode",
                Layer.DEFAULT_COMPOSITION_MODE,
                Layer.COMPOSITION_MODE_OPTIONS,
            )
        )
        self._private_variable_manager.declare_variable(
            ColorSequenceVariable(
                "palette",
                pysicgl.ColorSequence([0x000000, 0xFFFFFF]),
            )
        )
        self._private_variable_manager.declare_variable(
            FloatingVariable(
                "brightness",
                1.0,
            )
        )
        self._private_variable_manager.initialize_variables()

        # mutable info recorded in a cache
        # (this must be done after default values are set because it
        # will automatically enable the module if possible)
        initial_info = {
            "shard_uuid": None,
            "index": None,
            "active": True,
            "use_local_palette": False,
        }
        self._info = Cache(
            f"{self._root_path}/info",
            dict(**initial_info, **init_info),
            lambda key, value: self._handle_info_change(key, value),
        )

        # allow for post-init
        if post_init_hook is not None:
            post_init_hook(self)

    def _handle_info_change(self, key, value):
        self.reset_canvas()
        if key == "active":
            active = bool(value)
            self._ready = active
            return active
        if key == "palette":
            if value is None:
                self._palette = None
            else:
                l = list(int(element) for element in value)
                self._palette = pysicgl.ColorSequence(l)
                return l

    def destroy_storage(self):
        """
        Removes the layer information from storage
        """
        rmdirr(self._root_path)

    def set_shard(self, shard):
        self._shard = shard
        self._frame_generator_obj = self._shard.frames(self)
        self._ready = True

    def run(self):
        """
        Gets the next frame from the frame generator object, only if the layer is ready and active
        """
        if self._ready:
            next(self._frame_generator_obj)
            self.canvas.interface_scale(
                self._private_variable_manager.variables["brightness"].value
            )

    def reset_canvas(self):
        self.canvas.interface_fill(0x000000)

    def set_index(self, idx):
        self._info.set("index", idx)

    def set_active(self, active):
        self._info.set("active", bool(active))

    def merge_info(self, info):
        self._info.merge(info)

    def use_local_palette(self, use_local):
        self._info.set("use_local_palette", bool(use_local))

    @property
    def info(self):
        return dict(**self._info.cache, **self._static_info)

    @property
    def variable_manager(self):
        return self._variable_manager

    @property
    def private_variable_manager(self):
        return self._private_variable_manager

    @property
    def palette(self):
        if self._info.get("use_local_palette"):
            return self._private_variable_manager.variables["palette"].value
        else:
            return globals.variable_manager.variables["palette"].value

    @property
    def blending_mode(self):
        return self.private_variable_manager.variables["blending_mode"].value

    @property
    def composition_mode(self):
        return self.private_variable_manager.variables["composition_mode"].value
