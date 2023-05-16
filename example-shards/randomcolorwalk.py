# shows how to use a random color from the color palette
import random
from hidden_shades.variables.types import FloatingVariable

def frames(layer):
    value = 0.5

    layer.variable_manager.declare_variable(
        FloatingVariable("speed", 0.001)
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("randomness", 0.01)
    )

    while True:
        yield None

        # get variables
        speed = layer.variable_manager.variables["speed"].value
        randomness_strength = layer.variable_manager.variables["randomness"].value

        # increment value
        value += speed + (randomness_strength * (random.random() - 0.5))

        # fill canvas with interpolated color
        color = layer.palette.interpolate(value)
        layer.canvas.interface_fill(color)
