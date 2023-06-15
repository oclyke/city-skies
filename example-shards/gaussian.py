import pysicgl
import noise
from hidden_shades import timebase
from hidden_shades.timewarp import TimeWarp
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import FloatingVariable
from pysicgl_utils import Display
import math


def gaussian(x):
    return 10 * x * math.sin(2 * x / math.pi) / 3.0


def frames(layer):
    screen = layer.canvas.screen
    display = Display(screen)
    (numx, numy) = display.extent
    (maxx, maxy) = display.shape

    layer.variable_manager.declare_variable(
        FloatingVariable("offset", 0.0)
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("scaleX", 1.0)
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("scaleY", 1.0)
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("centerX", 0.0)
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("centerY", 0.0)
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("amplitude", 1.0)
    )
    layer.variable_manager.initialize_variables()

    # prepare a few static variables
    screen = layer.canvas.screen
    field = pysicgl.ScalarField(screen.pixels)
    osn = noise.OpenSimplexNoise()

    while True:
        yield None

        # get variables
        offset = layer.variable_manager.variables["offset"].value
        amplitude = layer.variable_manager.variables["amplitude"].value
        scaleX = layer.variable_manager.variables["scaleX"].value
        scaleY = layer.variable_manager.variables["scaleY"].value
        centerX = layer.variable_manager.variables["centerX"].value
        centerY = layer.variable_manager.variables["centerY"].value

        # add a gaussian value to the scalar field
        for pixel in display.pixel_info():
            (idx, (u, v), (x, y)) = pixel

            gx = gaussian((((x + centerX) / maxx) * scaleX) - 0.5)
            gy = gaussian((((y + centerY) / maxy) * scaleY) - 0.5)

            field[idx] = -(gx + gy) * amplitude

        # apply the scalar field to the canvas mapping against the
        # layer color palette
        layer.canvas.scalar_field(layer.canvas.screen, field, layer.palette, offset)
