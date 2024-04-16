# GET       /api/v0/shards
# PUT       /api/v0/shards/<uuid>

# GET       /api/v0/output
# GET       /api/v0/output/stack/<stack_id>
# PUT       /api/v0/output/stack/<stack_id>/activate
# GET       /api/v0/output/stack/<stack_id>/layers
# DELETE    /api/v0/output/stack/<stack_id>/layers
# POST      /api/v0/output/stack/<stack_id>/layers
# POST      /api/v0/output/stack/<stack_id>/layer
# GET       /api/v0/output/stack/<stack_id>/layer/<layer_id>
# DELETE    /api/v0/output/stack/<stack_id>/layer/<layer_id>
# PUT       /api/v0/output/stack/<stack_id>/layer/<layer_id>/config
# GET       /api/v0/output/stack/<stack_id>/layer/<layer_id>/variable/<variable_id>
# PUT       /api/v0/output/stack/<stack_id>/layer/<layer_id>/variable/<variable_id>
# GET       /api/v0/output/stack/<stack_id>/layer/<layer_id>/standard_variable/<variable_id>
# PUT       /api/v0/output/stack/<stack_id>/layer/<layer_id>/standard_variable/<variable_id>

# GET       /api/v0/global
# GET       /api/v0/global/variable/<id>
# PUT       /api/v0/global/variable/<id>

# GET       /api/v0/audio
# PUT       /api/v0/audio/source
# GET       /api/v0/audio/source/<id>
# GET       /api/v0/audio/source/<source_id>/variables/<var_id>
# PUT       /api/v0/audio/source/<source_id>/variables/<var_id>
# GET       /api/v0/audio/source/<source_id>/standard_variable/<var_id>
# PUT       /api/v0/audio/source/<source_id>/standard_variable/<var_id>

import requests
import json

class HttpClient:
    def __init__(self, host, port=None):
        self.host = host
        self.port = port

def json_from_response(response):
    return json.loads(response.content.decode("utf-8"))

def check_http_response_status(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if response.status_code != 200:
            raise Exception(f"HTTP request failed with status code {response.status_code}")
        return response
    return wrapper

@check_http_response_status
def get(client, path):
    endpoint = f"http://{client.host}{':' if client.port is not None else ''}{client.port}{path}"
    return requests.get(endpoint)

@check_http_response_status
def put(client, path, data):
    endpoint = f"http://{client.host}{':' if client.port is not None else ''}{client.port}{path}"
    return requests.put(endpoint, data)

@check_http_response_status
def post(client, path, data):
    endpoint = f"http://{client.host}{':' if client.port is not None else ''}{client.port}{path}"
    return requests.post(endpoint, data)

@check_http_response_status
def delete(client, path):
    endpoint = f"http://{client.host}{':' if client.port is not None else ''}{client.port}{path}"
    return requests.delete(endpoint)

def get_shard_info(client):
    return json_from_response(get(client, "/api/v0/shards"))

def get_output_info(client):
    return json_from_response(get(client, "/api/v0/output"))

def get_stack_info(client, stack_id):
    return json_from_response(get(client, f"/api/v0/output/stack/{stack_id}"))

def activate_stack(client, stack_id):
    return json_from_response(put(client, f"/api/v0/output/stack/{stack_id}/activate", ""))

def get_stack_layers_info(client, stack_id):
    return json_from_response(get(client, f"/api/v0/output/stack/{stack_id}/layers"))

def delete_stack_layers(client, stack_id):
    return json_from_response(delete(client, f"/api/v0/output/stack/{stack_id}/layers"))

def post_stack_layers(client, stack_id, layers):
    data = json.dumps({"layers": layers})
    return json_from_response(post(client, f"/api/v0/output/stack/{stack_id}/layers", data))

def post_stack_layer(client, stack_id, shard_uuid):
    data = json.dumps({"config": {"shard_uuid": shard_uuid}})
    return json_from_response(post(client, f"/api/v0/output/stack/{stack_id}/layer", data))

def get_stack_layer_info(client, stack_id, layer_id):
    return json_from_response(get(client, f"/api/v0/output/stack/{stack_id}/layer/{layer_id}"))

def delete_stack_layer(client, stack_id, layer_id):
    return json_from_response(delete(client, f"/api/v0/output/stack/{stack_id}/layer/{layer_id}"))

def put_stack_layer_config(client, stack_id, layer_id, config):
    data = json.dumps(config)
    return json_from_response(put(client, f"/api/v0/output/stack/{stack_id}/layer/{layer_id}/config", data))

def get_stack_layer_variable(client, stack_id, layer_id, variable_id):
    return json_from_response(get(client, f"/api/v0/output/stack/{stack_id}/layer/{layer_id}/variable/{variable_id}"))

def put_stack_layer_variable(client, stack_id, layer_id, variable_id, value):
    data = json.dumps({"value": value})
    return json_from_response(put(client, f"/api/v0/output/stack/{stack_id}/layer/{layer_id}/variable/{variable_id}", data))

def get_stack_layer_standard_variable(client, stack_id, layer_id, variable_id):
    return json_from_response(get(client, f"/api/v0/output/stack/{stack_id}/layer/{layer_id}/standard_variable/{variable_id}"))

def put_stack_layer_standard_variable(client, stack_id, layer_id, variable_id, value):
    data = json.dumps({"value": value})
    return json_from_response(put(client, f"/api/v0/output/stack/{stack_id}/layer/{layer_id}/standard_variable/{variable_id}", data))

def get_globals_info(client):
    return json_from_response(get(client, "/api/v0/global"))

def get_global_variable_info(client, variable_id):
    return json_from_response(get(client, f"/api/v0/global/variable/{variable_id}"))

def put_global_variable(client, variable_id, value):
    data = json.dumps({"value": value})
    return json_from_response(put(client, f"/api/v0/global/variable/{variable_id}", data))
