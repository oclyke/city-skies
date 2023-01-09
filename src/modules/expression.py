class Layer:
    def __init__(self, expression, id, interface):
        from variables import VariableManager
        from cache import Cache

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
        self._variable_manager = VariableManager(f"{self._root_path}/vars")

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
            from singletons import shard_manager

            module = shard_manager.get_shard_module(uuid)
            self._frame_generator_obj = module.frames(self)
            self._ready = True

    def _handle_info_change(self, key, value):
        if key == "shard":
            self._load_shard(value)

    def run(self):
        """
        Gets the next frame from the frame generator object, only if the layer is ready and active
        """
        if self._ready and self.info.get("active"):
            next(self._frame_generator_obj)

    @property
    def id(self):
        return self._id

    @property
    def info(self):
        return self._info

    @property
    def variables(self):
        return self._variable_manager.variables


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
        self._layer_stack_reverse = []

        # load layers from the filesystem
        for id in os.listdir(self._layers_path):
            layer = self._make_layer(id)
            self._layer_map[id] = layer
            self._layer_stack.append(layer)

        # now arrange the layers by index
        self._arrange_layers_by_index()

    def _update_reverse_layer_stack(self):
        # update the reversed layer stack
        # (it is necessary to copy the layer stack into a new list before
        # reversing otherwise the original will be affected by reference)
        self._layer_stack_reverse = list(self._layer_stack)
        self._layer_stack_reverse.reverse()

    def _arrange_layers_by_index(self):
        # sort the layers in the stack by index
        self._layer_stack.sort(key=lambda layer: layer.info.get("index"))
        self._update_reverse_layer_stack()

    def _recompute_layer_indices(self):
        for idx, layer in enumerate(self._layer_stack):
            layer.info.set("index", idx)
        self._update_reverse_layer_stack()

    def _make_layer(self, id):
        return Layer(self, id, self._interface)

    def add_layer(self, shard):
        import os

        id = next(self._layer_id_generator)
        os.mkdir(f"{self._layers_path}/{id}")
        layer = self._make_layer(id)
        layer.info.set("shard", shard)
        self._layer_stack.append(layer)
        self._layer_map[str(id)] = layer
        self._recompute_layer_indices()

    def move_layer_to_index(self, id, dest_idx):
        original_index = self._layer_map[id].index
        self._layer_stack.insert(dest_idx, self._layer_stack.pop(original_index))
        self._recompute_layer_indices()

    def get_layer_index(self, id):
        return self.get_layer_by_id(id).info.get("index")

    def get_layer_by_id(self, id):
        return self._layer_map[id]

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

    @property
    def layers_reversed(self):
        return self._layer_stack_reverse


class ExpressionManager:
    def __init__(self, path, interface):
        from cache import Cache

        self._expressionA = Expression(f"{path}/A", interface)
        self._expressionB = Expression(f"{path}/B", interface)

        self._active = None
        self._inactive = None

        initial_info = {
            "active": "A",
        }
        self._info = Cache(
            f"{path}/info",
            initial_info,
            lambda key, value: self._handle_info_change(key, value),
        )

    # expression selection information
    def _handle_info_change(self, key, value):
        if key == "active":
            self._handle_active_change(value)

    def _handle_active_change(self, name):
        if name == "A":
            self._active = self._expressionA
            self._inactive = self._expressionB
        elif name == "B":
            self._active = self._expressionB
            self._inactive = self._expressionA
        else:
            raise ValueError

    # a tool to activate an expression while simultaneously deactivating the other
    def activate(self, name):
        if name in ["A", "B"]:
            self._info.set("active", name)
        else:
            raise ValueError

    def get(self, name):
        if name == "active":
            return self._active
        if name == "inactive":
            return self._inactive
        else:
            raise ValueError

    @property
    def active(self):
        return self._active

    @property
    def inactive(self):
        return self._inactive
