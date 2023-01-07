from microdot_asyncio import Microdot, Response
from semver import SemanticVersion

"""
The version of the API
"""
control_api_version = SemanticVersion.from_semver("0.0.0")

app = Microdot()

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
    from hardware import hw_version

    return Response(hw_version.to_string())


@app.get("/firmware/version")
async def get_fw_version(request):
    from firmware import fw_version

    return Response(fw_version.to_string())


@app.get("/api/version")
async def get_api_version(request):
    return Response(control_api_version.to_string())


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


# curl -H "Content-Type: text/plain" -X POST http://localhost:1337/expressions/active/layer -d '14e84711-7627-40a5-97ae-11fd5ff3b607'
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
