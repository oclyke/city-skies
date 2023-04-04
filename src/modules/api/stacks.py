from microdot_asyncio import Microdot
import json

from hidden_shades.layer import Layer

stacks_app = Microdot()


def init_stacks_app(stack_manager, canvas, layer_post_init_hook):
    ###############
    # stack control

    # change the active stack
    @stacks_app.put("/manager/switch")
    async def switch_stacks(request):
        stack_manager.switch()

    # list layers in stack
    @stacks_app.get("/<active>/layers")
    async def get_layers(request, active):
        stack = stack_manager.get(active)
        return list(str(layer.id) for layer in stack)

    # add a layer to stack
    # curl -H "Content-Type: text/plain" -X POST http://localhost:1337/<active>/layer -d '{"shard_uuid": "noise"}'
    @stacks_app.post("/<active>/layer")
    async def put_stack_layer(request, active):
        data = json.loads(request.body.decode())
        stack = stack_manager.get(active)
        id, path, index = stack.get_new_layer_info()
        layer = Layer(
            id, path, canvas, init_info=data, post_init_hook=layer_post_init_hook
        )
        stack.add_layer(layer)

    # remove a layer from stack
    @stacks_app.delete("/<active>/layers/<layerid>")
    async def delete_stack_layer(request, active, layerid):
        stack = stack_manager.get(active)
        stack.remove_layer_by_id(str(layerid))

    ###############
    # layer control

    # get info
    @stacks_app.get("/<active>/layers/<layerid>/info")
    async def get_layer_info(request, active, layerid):
        stack = stack_manager.get(active)
        layer = stack.get_layer_by_id(str(layerid))
        return layer.info

    # list public variables
    @stacks_app.get("/<active>/layers/<layerid>/variables")
    async def get_layer_variables(request, active, layerid):
        stack = stack_manager.get(active)
        layer = stack.get_layer_by_id(str(layerid))
        names = list(
            variable.name for variable in layer.variable_manager.variables.values()
        )
        return names

    # list private variables
    @stacks_app.get("/<active>/layers/<layerid>/private_variables")
    async def get_layer_private_variables(request, active, layerid):
        stack = stack_manager.get(active)
        layer = stack.get_layer_by_id(str(layerid))
        return list(
            variable.name
            for variable in layer.private_variable_manager.variables.values()
        )

    # update layer info
    # curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/<active>/layers/<layerid>/info -d '{"composition_mode": 3}'
    @stacks_app.put("/<active>/layers/<layerid>/info")
    async def put_layer_info(request, active, layerid):
        stack = stack_manager.get(active)
        layer = stack.get_layer_by_id(str(layerid))
        layer.merge_info(json.loads(request.body.decode()))

    ########################
    # layer public variables
    @stacks_app.get("/<active>/layers/<layerid>/variables/<varname>/value")
    async def get_layer_variable_value(request, active, layerid, varname):
        stack = stack_manager.get(active)
        layer = stack.get_layer_by_id(str(layerid))
        variable = layer.variable_manager.variables[varname]
        return variable.serialize(variable.value)

    @stacks_app.get("/<active>/layers/<layerid>/variables/<varname>/info")
    async def get_layer_variable_info(request, active, layerid, varname):
        stack = stack_manager.get(active)
        layer = stack.get_layer_by_id(str(layerid))
        variable = layer.variable_manager.variables[varname]
        return variable.get_dict()

    # curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/<active>/layers/<layerid>/variables/<varname> -d 'value'
    @stacks_app.put("/<active>/layers/<layerid>/variables/<varname>")
    async def put_layer_variable(request, active, layerid, varname):
        stack = stack_manager.get(active)
        layer = stack.get_layer_by_id(str(layerid))
        variable = layer.variable_manager.variables[varname]
        variable.value = variable.deserialize(request.body.decode())

    #########################
    # layer private variables
    @stacks_app.get("/<active>/layers/<layerid>/private_variables/<varname>/value")
    async def get_layer_private_variable_value(request, active, layerid, varname):
        stack = stack_manager.get(active)
        layer = stack.get_layer_by_id(str(layerid))
        variable = layer.private_variable_manager.variables[varname]
        return variable.serialize(variable.value)

    @stacks_app.get("/<active>/layers/<layerid>/private_variables/<varname>/info")
    async def get_layer_private_variable_info(request, active, layerid, varname):
        stack = stack_manager.get(active)
        layer = stack.get_layer_by_id(str(layerid))
        variable = layer.private_variable_manager.variables[varname]
        return variable.get_dict()

    # curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/<active>/layers/<layerid>/private_variables/<varname> -d 'value'
    @stacks_app.put("/<active>/layers/<layerid>/private_variables/<varname>")
    async def put_layer_private_variable(request, active, layerid, varname):
        stack = stack_manager.get(active)
        layer = stack.get_layer_by_id(str(layerid))
        variable = layer.private_variable_manager.variables[varname]
        value = request.body.decode()
        variable.value = variable.deserialize(value)
