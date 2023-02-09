from cache import Cache
from .variables.manager import VariableManager


class Layer:
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

        # mutable info recorded in a cache
        # (this must be done after default values are set because it
        # will automatically enable the module if possible)
        initial_info = {
            "shard_uuid": None,
            "composition_mode": 0,
            "index": None,
            "active": True,
            "palette": None,
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
            if value is not None:
                return list(int(element) for element in value)

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

    def reset_canvas(self):
        self.canvas.interface_fill(0x000000)

    def declare_variable(self, variable):
        self._variable_manager.declare_variable(variable)

    def set_index(self, idx):
        self._info.set("index", idx)

    def set_active(self, active):
        self._info.set("active", bool(active))

    def merge_info(self, info):
        self._info.merge(info)

    @property
    def info(self):
        return dict(**self._info.cache, **self._static_info)

    @property
    def variables(self):
        return self._variable_manager.variables
