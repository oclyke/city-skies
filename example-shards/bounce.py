# demonstration of dynamic secondary color palette usage
from hidden_shades.variables.types import ColorSequenceVariable


def frames(layer):
    layer.variable_manager.declare_variable(
        ColorSequenceVariable(scale.x, "scaleX", responders=[responder])
    )

    while True:
        yield None

        layer.canvas.interface_fill(layer.palette[0])
