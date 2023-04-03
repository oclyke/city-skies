from microdot_asyncio import Microdot
import hidden_shades

audio_app = Microdot()


@audio_app.get("/info")
async def get_audio_info(request):
    hidden_shades.audio_manager.info
    return hidden_shades.audio_manager.info


@audio_app.get("/sources")
async def get_audio_sources(request):
    return list(hidden_shades.audio_manager.sources.keys())


# curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/source/<source_name> -d 'MockAudio'
@audio_app.put("/source/<source_name>")
async def put_audio_source(request, source_name):
    if source_name == "NULL":
        source_name = None
    hidden_shades.audio_manager.select_source(source_name)


@audio_app.get("/sources/<source_name>/variables")
async def get_audio_source_variables(request, source_name):
    source = hidden_shades.audio_manager.sources[source_name]
    return list(
        variable.name for variable in source.variable_manager.variables.values()
    )


@audio_app.get("/sources/<source_name>/private_variables")
async def get_audio_source_private_variables(request, source_name):
    source = hidden_shades.audio_manager.sources[source_name]
    return list(
        variable.name for variable in source.private_variable_manager.variables.values()
    )


###############################
# audio source public variables
@audio_app.get("/sources/<source_name>/variables/<varname>/value")
async def get_audio_source_variable_value(request, source_name, varname):
    source = hidden_shades.audio_manager.sources[source_name]
    variable = source.variable_manager.variables[varname]
    return variable.serialize(variable.value)


@audio_app.get("/sources/<source_name>/variables/<varname>/info")
async def get_audio_source_variable_info(request, source_name, varname):
    source = hidden_shades.audio_manager.sources[source_name]
    variable = source.variable_manager.variables[varname]
    return variable.info


# curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/sources/<source_name>/private_variables/<varname> -d 'value'
@audio_app.put("/sources/<source_name>/variables/<varname>")
async def put_audio_source_variable(request, source_name, varname):
    source = hidden_shades.audio_manager.sources[source_name]
    variable = source.variable_manager.variables[varname]
    variable.value = variable.deserialize(request.body.decode())


###############################
# audio source private variables
@audio_app.get("/sources/<source_name>/private_variables/<varname>/value")
async def get_audio_source_private_variable_value(request, source_name, varname):
    source = hidden_shades.audio_manager.sources[source_name]
    variable = source.private_variable_manager.variables[varname]
    return variable.serialize(variable.value)


@audio_app.get("/sources/<source_name>/private_variables/<varname>/info")
async def get_audio_source_private_variable_info(request, source_name, varname):
    source = hidden_shades.audio_manager.sources[source_name]
    variable = source.private_variable_manager.variables[varname]
    return variable.info


# curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/sources/<source_name>/private_variables/<varname> -d 'value'
@audio_app.put("/sources/<source_name>/private_variables/<varname>")
async def put_audio_source_private_variable(request, source_name, varname):
    source = hidden_shades.audio_manager.sources[source_name]
    variable = source.private_variable_manager.variables[varname]
    variable.value = variable.deserialize(request.body.decode())
