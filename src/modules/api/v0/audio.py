from microdot_asyncio import Microdot
import hidden_shades
import json

audio_app = Microdot()


@audio_app.get("")
async def get_audio_info(request):
    hidden_shades.audio_manager.info
    return {
        "sources": {
            "selected": hidden_shades.audio_manager.info["selected"],
            "ids": list(hidden_shades.audio_manager.sources.keys()),
        },
    }

@audio_app.put("/source")
async def put_audio_source(request):
    data = json.loads(request.body.decode())
    hidden_shades.audio_manager.select_source(data["id"])

@audio_app.get("/source/<id>")
async def put_audio_source(request, id):
    source = hidden_shades.audio_manager.sources[id]
    return {
        "privateVariables": source.private_variable_manager.variable_names,
        "variables": source.variable_manager.variable_names,
    }

@audio_app.get("/source/<source_id>/variables/<var_id>")
async def get_audio_source_variable(request, source_id, var_id):
    source = hidden_shades.audio_manager.sources[source_id]
    variable = source.variable_manager.variables[var_id]
    return variable.get_dict()

@audio_app.put("/source/<source_id>/variables/<var_id>")
async def put_audio_source_variable(request, source_id, var_id):
    data = json.parse(request.body.decode())
    source = hidden_shades.audio_manager.sources[source_id]
    variable = source.variable_manager.variables[var_id]
    variable.value = variable.deserialize(data["value"])

@audio_app.get("/source/<source_id>/private_variable/<var_id>")
async def get_audio_source_variable(request, source_id, var_id):
    source = hidden_shades.audio_manager.sources[source_id]
    variable = source.private_variable_manager.variables[var_id]
    return variable.get_dict()

@audio_app.put("/source/<source_id>/private_variable/<var_id>")
async def put_audio_source_variable(request, source_id, var_id):
    data = json.parse(request.body.decode())
    source = hidden_shades.audio_manager.sources[source_id]
    variable = source.private_variable_manager.variables[var_id]
    variable.value = variable.deserialize(data["value"])