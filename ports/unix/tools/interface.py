import requests
import json
from collections import namedtuple


def _to_dict(response):
    return json.loads(response.content.decode("utf-8"))


def _from_dict(data):
    return json.dumps(data)


def _to_list(response):
    return response.content.decode("utf-8").split("\n")


class HttpClient:
    def __init__(self, host, port=None):
        self.host = host
        self.port = port


class RestNode:
    @classmethod
    def fromBase(cls, base_node, extension):
        return cls(base_node.client, f"{base_node.root}{extension}")

    def __init__(self, client, root_path):
        self._client = client
        self._root_path = root_path

    def _endpoint(self, path):
        return f"http://{self._client.host}{':' if self._client.port is not None else ''}{self._client.port}{self._root_path}{path}"

    @property
    def root(self):
        return self._root_path

    @property
    def client(self):
        return self._client

    def get(self, path):
        return requests.get(self._endpoint(path))

    def put(self, path, value):
        return requests.put(self._endpoint(path), str(value))

    def post(self, path, value):
        return requests.post(self._endpoint(path), str(value))

    def delete(self, path):
        return requests.delete(self._endpoint(path))


class CitySkiesClient:
    def __init__(self, host, port=None):
        self._client = HttpClient(host, port)
        self._node = RestNode(self._client, "")

        Stacks = namedtuple("Stacks", ["active", "inactive"])
        self._stacks = Stacks(
            Stack(self._node, "active"),
            Stack(self._node, "inactive"),
        )

        self._audio = Audio(self._node)

    @property
    def audio(self):
        return self._audio

    @property
    def stacks(self):
        return self._stacks

    @property
    def global_variables(self):
        return _to_list(self._node.get(f"/globals/variables"))

    def add_shard_from_string(self, uuid, value):
        self._node.put(f"/shards/{uuid}", value)

    def set_global_variable(self, varname, value):
        self._node.put(f"/globals/vars/{varname}", value)


class Audio:
    def __init__(self, base_node):
        self._node = RestNode.fromBase(base_node, f"/audio")

    @property
    def info(self):
        return _to_dict(self._node.get(f"/info"))

    @property
    def sources(self):
        return _to_list(self._node.get(f"/sources"))

    def select_source(self, source_name):
        self._node.put(f"/source/{source_name}", None)

    def get_source(self, source_name):
        return AudioSource(self._node, source_name)


class AudioSource:
    def __init__(self, base_node, source_name):
        self._node = RestNode.fromBase(base_node, f"/sources/{source_name}")
        self._source_name = source_name

    def set_variable(self, varname, value):
        self._node.put(f"/vars/{varname}", value)

    def set_private_variable(self, varname, value):
        self._node.put(f"/private_vars/{varname}", value)

    @property
    def variables(self):
        return _to_list(self._node.get(f"/variables"))

    @property
    def private_variables(self):
        return _to_list(self._node.get(f"/private_variables"))


class Stack:
    def __init__(self, base_node, stack_id):
        self._node = RestNode.fromBase(base_node, f"/stacks/{stack_id}")
        self._stack_id = stack_id

    @property
    def name(self):
        return self._stack_id

    @property
    def layers(self):
        return _to_list(self._node.get(f"/layers"))

    def get_layer(self, layer_id):
        return Layer(self._node, layer_id)

    def add_layer(self, uuid):
        init_info = {
            "shard_uuid": uuid,
        }
        self._node.post(f"/layer", _from_dict(init_info))

    def remove_layer(self, layer_id):
        self._node.delete(f"/layers/{layer_id}")


class Layer:
    def __init__(self, base_node, layer_id):
        self._node = RestNode.fromBase(base_node, f"/layers/{layer_id}")
        self._layer_id = str(layer_id)

    @property
    def name(self):
        return self._layer_id

    @property
    def info(self):
        return _to_dict(self._node.get(f"/info"))

    @property
    def shards(self):
        return _to_list(self._node.get(f"/shards"))

    @property
    def variables(self):
        return _to_list(self._node.get(f"/variables"))

    @property
    def private_variables(self):
        return _to_list(self._node.get(f"/private_variables"))

    def update_info(self, value):
        self._node.put(f"/info", value)

    def set_variable(self, varname, value):
        self._node.put(f"/vars/{varname}", value)

    def set_private_variable(self, varname, value):
        self._node.put(f"/private_vars/{varname}", value)


class Variable:
    def __init__(self, base_node, name):
        self._node = RestNode.fromBase(base_node, f"/{name}")

    # def


if __name__ == "__main__":
    PATRIOT = [0xFF0000, 0xFFFFFF, 0x0000FF]
    RASTA = [0xFF0000, 0xFFFF00, 0x00FF00]
    MASK = [0xFF000000]

    def make_color_sequence_var_string(colors, map_type="continuous_circular"):
        return json.dumps(
            {
                "colors": colors,
                "map_type": map_type,
            }
        )

    c = CitySkiesClient("localhost", 1337)
