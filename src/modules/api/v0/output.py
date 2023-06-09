from microdot_asyncio import Microdot
import json

from hidden_shades.layer import Layer

output_app = Microdot()

def init_output_app(stack_manager, canvas, layer_post_init_hook):
    @output_app.get("")
    async def get_output_index(request):
        """
        return information about the output state
        """
        return {
            "stacks": {
                "total": 2,
                "ids": list(stack_manager.stacks.keys()),
                "active": stack_manager.info.get("active"),
            },
        }

    @output_app.get("/stack/<stack_id>")
    def get_stack(request, stack_id):
        """
        get information about the stack
        """
        stack = stack_manager.stacks[stack_id]
        layers = list(str(layer.id) for layer in stack)
        return {
            "id": stack.id,
            "layers": {
                "total": len(layers),
                "ids": layers,
            }
        }

    @output_app.put("/stack/<stack_id>")
    def activate_stack(request, stack_id):
        """
        activate the given stack id
        """
        stack_manager.activate(stack_id)

    @output_app.get("/stack/<stack_id>/layer/<layer_id>")
    async def get_layer_info(request, stack_id, layer_id):
        stack = stack_manager.stacks[stack_id]
        layer = stack.get_layer_by_id(str(layer_id))
        info = layer.info
        return {
            "variables": layer.variable_manager.info,
            "privateVariables":  layer.private_variable_manager.info,
            "config": layer.info,
        }

    @output_app.post("/stack/<stack_id>/layer")
    async def put_stack_layer(request, stack_id):
        """
        add a layer to the stack
        """
        data = json.loads(request.body.decode())
        stack = stack_manager.stacks[stack_id]
        id, path, index = stack.get_new_layer_info()
        layer = Layer(
            id, path, canvas, init_info=data, post_init_hook=layer_post_init_hook
        )
        stack.add_layer(layer)

    @output_app.delete("/stack/<stack_id>/layer/<layer_id>")
    async def delete_stack_layer(request, stack_id, layer_id):
        """
        remove a layer from the stack
        """
        stack = stack_manager.stacks[stack_id]
        stack.remove_layer_by_id(str(layer_id))

    @output_app.put("/stack/<stack_id>/layer/<layer_id>/config")
    async def put_layer_config(request, stack_id, layer_id):
        """
        change the config values of a layer
        """
        data = json.loads(request.body.decode())
        stack = stack_manager.stacks[stack_id]
        layer = stack.get_layer_by_id(str(layer_id))
        layer.merge_info(data)

    @output_app.get("/stack/<stack_id>/layer/<layer_id>/variable/<variable_id>")
    async def get_layer_variable_info(request, stack_id, layer_id, variable_id):
        """
        get variable info
        """
        stack = stack_manager.stacks[stack_id]
        layer = stack.get_layer_by_id(str(layer_id))
        variable = layer.variable_manager.variables[variable_id]
        return variable.get_dict()

    @output_app.put("/stack/<stack_id>/layer/<layer_id>/variable/<variable_id>")
    async def put_layer_variable(request, stack_id, layer_id, variable_id):
        """
        set variable value
        """
        data = json.loads(request.body.decode())
        stack = stack_manager.stacks[stack_id]
        layer = stack.get_layer_by_id(str(layer_id))
        variable = layer.variable_manager.variables[variable_id]
        variable.value = variable.deserialize(data["value"])

    @output_app.get("/stack/<stack_id>/layer/<layer_id>/private_variable/<variable_id>")
    async def get_layer_private_variable_info(request, stack_id, layer_id, variable_id):
        stack = stack_manager.stacks[stack_id]
        layer = stack.get_layer_by_id(str(layer_id))
        variable = layer.private_variable_manager.variables[variable_id]
        return variable.get_dict()

    @output_app.put("/stack/<stack_id>/layer/<layer_id>/private_variable/<variable_id>")
    async def put_layer_private_variable(request, stack_id, layer_id, variable_id):
        """
        set private variable value
        """
        data = json.loads(request.body.decode())
        stack = stack_manager.stacks[stack_id]
        layer = stack.get_layer_by_id(str(layer_id))
        variable = layer.private_variable_manager.variables[variable_id]
        variable.value = variable.deserialize(data["value"])