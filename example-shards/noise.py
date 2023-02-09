import pysicgl
import noise
from hidden_shades import timebase, palette
from hidden_shades.timewarp import TimeWarp
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import FloatingVariable


def frames(layer):
    # use the TimeWarp class to make an offset from the base time
    # this begins at unity speed (1.0) but will be updated by the
    # declared speed variable
    timewarp = TimeWarp(timebase.local)

    # a callback function to handle changes to declared variables
    def handle_variable_changes(name, value):
        if name == "speed":
            timewarp.set_frequency(value)

    # a responder which injects the handle_variable_changes()
    # callback into the declared variables (as needed)
    responder = VariableResponder(handle_variable_changes)

    # declare variables
    # these are all of the floating point variety but there are a
    # few different choices (Boolean, Integer, Floating, Option,
    # and ColorSequence)
    # note: only the "speed" variable is assinged the responder
    layer.declare_variable(FloatingVariable(1.0, "speed", responders=[responder]))
    layer.declare_variable(FloatingVariable(1.0, "scaleX"))
    layer.declare_variable(FloatingVariable(1.0, "scaleY"))
    layer.declare_variable(FloatingVariable(0.0, "centerX"))
    layer.declare_variable(FloatingVariable(0.0, "centerY"))

    # prepare a few static variables
    screen = layer.canvas.screen
    field = pysicgl.ScalarField(screen.pixels)
    osn = noise.OpenSimplexNoise()

    while True:
        yield None

        # the timewarp uses its internal speed, as well as the speed
        # of the reference time (in this case timebase.local) to
        # compute its own local time
        # the hard-coded division here it to make the 1.0x speed
        # (unity) case look good. usually variables should be used.
        z = timewarp.local() / 1000

        # use variable values as arguments to the drawig functions
        # these values are dynamic and may change between frame renders
        scale = (layer.variables["scaleX"].value, layer.variables["scaleY"].value)
        center = (layer.variables["centerX"].value, layer.variables["centerY"].value)

        # use the OpenSimplexNoise utility to fill the scalar field
        osn.fill_scalar_field(field, screen, z, scale, center)

        # apply the scalar field to the canvas mapping against the
        # primary color palette
        layer.canvas.scalar_field(layer.canvas.screen, field, palette.primary)
