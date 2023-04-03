from microdot_asyncio import Microdot
from hidden_shades import globals

globals_app = Microdot()


@globals_app.get("/variables")
async def get_global_variables(request):
    return list(
        variable.name for variable in globals.variable_manager.variables.values()
    )


@globals_app.get("/variables/<varname>/value")
async def get_global_variable_value(request, varname):
    variable = globals.variable_manager.variables[varname]
    return variable.serialize(variable.value)


@globals_app.get("/variables/<varname>/info")
async def get_global_variable_info(request, varname):
    variable = globals.variable_manager.variables[varname]
    return variable.get_dict()


# curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/variables/<varname> -d 'value'
@globals_app.put("/variables/<varname>")
async def put_global_variable(request, varname):
    variable = globals.variable_manager.variables[varname]
    variable.value = variable.deserialize(request.body.decode())
