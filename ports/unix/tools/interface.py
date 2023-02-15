import requests
import json


def _endpoint(host, port, path):
    return f"http://{host}{':' if port is not None else ''}{port}{path}"


def _to_dict(response):
    return json.loads(response.content.decode("utf-8"))


def _from_dict(data):
    return json.dumps(data)


def _to_list(response):
    return response.content.decode("utf-8").split("\n")


class CitySkiesClient:
    def __init__(self, host, port=None):
        self.host = host
        self.port = port

    def get_info(self):
        return _to_dict(requests.get(_endpoint(self.host, self.port, "/info")))

    def list_shards(self):
        return _to_list(requests.get(_endpoint(self.host, self.port, "/shards")))

    def list_layers(self, stack):
        return _to_list(
            requests.get(_endpoint(self.host, self.port, f"/stacks/{stack}/layers"))
        )

    def list_layer_variables(self, stack, layer):
        return _to_list(
            requests.get(
                _endpoint(
                    self.host, self.port, f"/stacks/{stack}/layers/{layer}/variables"
                )
            )
        )

    def list_layer_private_variables(self, stack, layer):
        return _to_list(
            requests.get(
                _endpoint(
                    self.host,
                    self.port,
                    f"/stacks/{stack}/layers/{layer}/private_variables",
                )
            )
        )

    def add_shard_from_string(self, uuid, value):
        requests.put(_endpoint(self.host, self.port, f"/shards/{uuid}"), value)

    def add_layer(self, stack, uuid):
        init_info = {
            "shard_uuid": uuid,
        }
        requests.post(
            _endpoint(self.host, self.port, f"/stacks/{stack}/layer"),
            _from_dict(init_info),
        )

    def set_layer_info(self, stack, layerid, info):
        requests.put(
            _endpoint(self.host, self.port, f"/stacks/{stack}/layers/{layerid}/info"),
            _from_dict(info),
        )

    def set_layer_variable(self, stack, layerid, varname, value):
        requests.put(
            _endpoint(
                self.host, self.port, f"/stacks/{stack}/layers/{layerid}/vars/{varname}"
            ),
            str(value),
        )

    def set_layer_private_variable(self, stack, layerid, varname, value):
        requests.put(
            _endpoint(
                self.host,
                self.port,
                f"/stacks/{stack}/layers/{layerid}/private_vars/{varname}",
            ),
            str(value),
        )

    def set_global_variable(self, varname, value):
        requests.put(
            _endpoint(self.host, self.port, f"/globals/vars/{varname}"),
            str(value),
        )


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
