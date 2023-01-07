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
