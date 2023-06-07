from microdot_asyncio import Microdot
import json

from hidden_shades.layer import Layer

stacks_app = Microdot()


def layerEdgeById(id):
    return {
        "node": {
            "id": f"{id}",
        },
        "cursor": f"{id}",
    }

def init_stacks_app(stack_manager, canvas, layer_post_init_hook):
    ###############
    # stack control

    # list layers in stack
    @stacks_app.get("/<stackid>/layers_connection")
    async def get_info(request, stackid):
        stack = stack_manager.stacks[stackid]
        layers = list(str(layer.id) for layer in stack)
        edges = list(map(lambda id: layerEdgeById(id), layers))
        total = len(edges)

        if total == 0:
            pageInfo = {
                "hasNextPage": False,
                "hasPreviousPage": False,
                "startCursor": None,
                "endCursor": None,
            }
        else:
            pageInfo = {
                "hasNextPage": False,
                "hasPreviousPage": False,
                "startCursor": edges[0]["cursor"],
                "endCursor": edges[-1]["cursor"]
            }
        return {
            "total": total,
            "edges": edges,
            "pageInfo": pageInfo,
        }

    # add a layer to stack
    # curl -H "Content-Type: text/plain" -X POST http://localhost:1337/<stackid>/layer -d '{"shard_uuid": "noise"}'
    @stacks_app.post("/<stackid>/layer")
    async def put_stack_layer(request, active):
        data = json.loads(request.body.decode())
        stack = stack_manager.stacks[stackid]
        id, path, index = stack.get_new_layer_info()
        layer = Layer(
            id, path, canvas, init_info=data, post_init_hook=layer_post_init_hook
        )
        stack.add_layer(layer)

    # remove a layer from stack
    @stacks_app.delete("/<stackid>/layers/<layerid>")
    async def delete_stack_layer(request, stackid, layerid):
        stack = stack_manager.stacks[stackid]
        stack.remove_layer_by_id(str(layerid))

    ###############
    # layer control

    # get info
    @stacks_app.get("/<stackid>/layers/<layerid>/info")
    async def get_layer_info(request, stackid, layerid):
        stack = stack_manager.stacks[stackid]
        layer = stack.get_layer_by_id(str(layerid))
        return layer.info

    # list public variables
    @stacks_app.get("/<stackid>/layers/<layerid>/variables")
    async def get_layer_variables(request, stackid, layerid):
        stack = stack_manager.stacks[stackid]
        layer = stack.get_layer_by_id(str(layerid))
        names = list(
            variable.name for variable in layer.variable_manager.variables.values()
        )
        return names

    # list private variables
    @stacks_app.get("/<stackid>/layers/<layerid>/private_variables")
    async def get_layer_private_variables(request, stackid, layerid):
        stack = stack_manager.stacks[stackid]
        layer = stack.get_layer_by_id(str(layerid))
        return list(
            variable.name
            for variable in layer.private_variable_manager.variables.values()
        )

    # update layer info
    # curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/<stackid>/layers/<layerid>/info -d '{"composition_mode": 3}'
    @stacks_app.put("/<stackid>/layers/<layerid>/info")
    async def put_layer_info(request, stackid, layerid):
        stack = stack_manager.stacks[stackid]
        layer = stack.get_layer_by_id(str(layerid))
        layer.merge_info(json.loads(request.body.decode()))

    ########################
    # layer public variables
    @stacks_app.get("/<stackid>/layers/<layerid>/variables/<varname>/value")
    async def get_layer_variable_value(request, stackid, layerid, varname):
        stack = stack_manager.stacks[stackid]
        layer = stack.get_layer_by_id(str(layerid))
        variable = layer.variable_manager.variables[varname]
        return variable.serialize(variable.value)

    @stacks_app.get("/<stackid>/layers/<layerid>/variables/<varname>/info")
    async def get_layer_variable_info(request, stackid, layerid, varname):
        stack = stack_manager.stacks[stackid]
        layer = stack.get_layer_by_id(str(layerid))
        variable = layer.variable_manager.variables[varname]
        return variable.get_dict()

    # curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/<stackid>/layers/<layerid>/variables/<varname> -d 'value'
    @stacks_app.put("/<stackid>/layers/<layerid>/variables/<varname>")
    async def put_layer_variable(request, stackid, layerid, varname):
        stack = stack_manager.stacks[stackid]
        layer = stack.get_layer_by_id(str(layerid))
        variable = layer.variable_manager.variables[varname]
        variable.value = variable.deserialize(request.body.decode())

    #########################
    # layer private variables
    @stacks_app.get("/<stackid>/layers/<layerid>/private_variables/<varname>/value")
    async def get_layer_private_variable_value(request, stackid, layerid, varname):
        stack = stack_manager.stacks[stackid]
        layer = stack.get_layer_by_id(str(layerid))
        variable = layer.private_variable_manager.variables[varname]
        return variable.serialize(variable.value)

    @stacks_app.get("/<stackid>/layers/<layerid>/private_variables/<varname>/info")
    async def get_layer_private_variable_info(request, stackid, layerid, varname):
        stack = stack_manager.stacks[stackid]
        layer = stack.get_layer_by_id(str(layerid))
        variable = layer.private_variable_manager.variables[varname]
        return variable.get_dict()

    # curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/<stackid>/layers/<layerid>/private_variables/<varname> -d 'value'
    @stacks_app.put("/<stackid>/layers/<layerid>/private_variables/<varname>")
    async def put_layer_private_variable(request, stackid, layerid, varname):
        stack = stack_manager.stacks[stackid]
        layer = stack.get_layer_by_id(str(layerid))
        variable = layer.private_variable_manager.variables[varname]
        value = request.body.decode()
        variable.value = variable.deserialize(value)
