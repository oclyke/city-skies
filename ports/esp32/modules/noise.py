import sicgl
import noise
from singletons import speed_manager
from variables import DoubleVariable


def frames(l):
    sequence = sicgl.ColorSequence(l.palette, "continuous_linear")
    screen = l.canvas.screen
    field = sicgl.ScalarField(screen.pixels)
    osn = noise.OpenSimplexNoise()

    l._variable_manager.declare_variable(DoubleVariable, 1.0, "scaleX")
    l._variable_manager.declare_variable(DoubleVariable, 1.0, "scaleY")
    l._variable_manager.declare_variable(DoubleVariable, 0.0, "centerX")
    l._variable_manager.declare_variable(DoubleVariable, 0.0, "centerY")

    while True:
        yield None

        z = speed_manager.ticks_ms() / 1000
        scale = (l.variables["scaleX"].value, l.variables["scaleY"].value)
        center = (l.variables["centerX"].value, l.variables["centerY"].value)
        osn.fill_scalar_field(field, screen, z, scale, center)
        l.canvas.scalar_field(l.canvas.screen, field, sequence)
