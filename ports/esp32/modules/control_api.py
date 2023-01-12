import microdot_asyncio
import semver
import singletons

"""
The version of the API
"""
control_api_version = semver.SemanticVersion.from_semver("0.0.0")

app = microdot_asyncio.Microdot()


# curl -H "Content-Type: text/plain" -X GET http://localhost:1337/firmware/version
@app.get("/firmware/version")
async def get_fw_version(request):
    return microdot_asyncio.Response(singletons.fw_version.to_string())


# curl -H "Content-Type: text/plain" -X GET http://localhost:1337/api/version
@app.get("/api/version")
async def get_api_version(request):
    return microdot_asyncio.Response(control_api_version.to_string())


# curl -H "Content-Type: text/plain" -X GET http://localhost:1337/identity/tag
@app.get("/identity/tag")
async def get_tag(request):
    return microdot_asyncio.Response(singletons.identity.tag)


# curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/identity/tag -d 'johnny5'
@app.put("/identity/tag")
async def set_tag(request):
    singletons.identity.tag = request.body.decode()


# curl -H "Content-Type: text/plain" -X GET http://localhost:1337/shards
@app.get("/shards")
async def get_shards(request):
    return microdot_asyncio.Response(singletons.shard_manager.shards)


# curl -H "Content-Type: text/plain" -X GET http://localhost:1337/speed/info
@app.get("/speed/info")
async def get_speed_variables(request):
    return microdot_asyncio.Response(singletons.speed_manager.info)


# curl -H "Content-Type: text/plain" -X GET http://localhost:1337/speed/variables
@app.get("/speed/variables")
async def get_speed_variables(request):
    return microdot_asyncio.Response(list(singletons.speed_manager.variables.keys()))


# curl -H "Content-Type: text/plain" -X GET http://localhost:1337/speed/variable/PrimarySpeed
@app.get("/speed/variable/<name>")
async def get_speed_variable(request, name):
    return microdot_asyncio.Response(
        singletons.speed_manager.variables[name].serialize()
    )


# curl -H "Content-Type: text/plain" -X GET http://localhost:1337/audio/sources
@app.get("/audio/sources")
async def get_speed_variables(request):
    return microdot_asyncio.Response(list(singletons.audio_manager.sources.keys()))


# curl -H "Content-Type: text/plain" -X GET http://localhost:1337/audio/SineTest/info
@app.get("/audio/<source>/info")
async def get_speed_variables(request, source):
    return microdot_asyncio.Response(singletons.audio_manager.sources[source].info)


# curl -H "Content-Type: text/plain" -X GET http://localhost:1337/audio/source/SineTest/info/volume
@app.get("/audio/source/<source>/info/volume")
async def get_audio_source_volume(request, source):
    return microdot_asyncio.Response(
        str(singletons.audio_manager.sources[source].volume)
    )


# curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/audio/source/SineTest/volume -d '0.69'
@app.put("/audio/source/<source>/volume")
async def set_audio_source_volume(request, source):
    singletons.audio_manager.sources[source].volume = request.body.decode()


# curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/expressions/info/active -d 'A'
@app.put("/expressions/info/active")
async def set_expression_active(request):
    name = str(request.body.decode())
    if name in ["A", "B"]:
        singletons.expression_manager.activate(name)
    else:
        return microdot_asyncio.Response(status_code=406)


# curl -H "Content-Type: text/plain" -X POST http://localhost:1337/expressions/active/layer -d '14e84711-7627-40a5-97ae-11fd5ff3b607'
@app.post("/expressions/<expression>/layer")
async def add_layer(request, expression):
    shard = request.body.decode()
    singletons.expression_manager.get(expression).add_layer(shard)


# curl -H "Content-Type: text/plain" -X GET http://localhost:1337/expressions/active/layer/<id>/info
@app.get("/expressions/<expression>/layer/<layer_id>/info")
async def add_layer(request, expression, layer_id):
    info = singletons.expression_manager.get(expression).layers[int(layer_id)].info
    return microdot_asyncio.Response(info)


@app.put("/expressions/<expression>/layer/<id>/index")
async def set_layer_index(request, expression, id):
    index = request.body.decode()
    singletons.expression_manager.get(expression).move_layer_to_index(id, int(index))


@app.delete("/expressions/<expression>/layer/<id>")
async def delete_layer(request, expression, id):
    singletons.expression_manager.get(expression).remove_layer(id)


@app.delete("/expressions/<expression>/layers")
async def clear_layers(request, expression):
    singletons.expression_manager.get(expression).clear_layers()


# curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/shards/14e84711-7627-40a5-97ae-11fd5ff3b607 -d $'def frames(l):\n\twhile True:\n\t\tyield None\n\t\tprint("hello world")\n\n'
@app.put("/shards/<uuid>")
async def store_shard(request, uuid):
    singletons.shard_manager.store_shard(uuid, request.body.decode())
