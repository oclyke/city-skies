import pysicgl
import noise
from hidden_shades import timebase
from hidden_shades.timewarp import TimeWarp
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import FloatingVariable


class FloatVec2:
    def __init__(self, name, initial_values):
        self._name = name
        self._x = float(initial_values[0])
        self._y = float(initial_values[1])

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = float(value)

    @property
    def y(self):
        return self._y

    @x.setter
    def y(self, value):
        self._y = float(value)

    @property
    def vector(self):
        return (self._x, self._y)


def frames(layer):
    # use the TimeWarp class to make an offset from the base time
    # this begins at unity speed (1.0) but will be updated by the
    # declared speed variable
    timewarp = TimeWarp(timebase.local)

    # declare some 2-element floating point vectors.
    # the values here are used as the default values for declared variables
    # but will be reset by the stored value when the
    # layer_manager.initialize_variables() method is called.
    scale = FloatVec2("scale", (0.2, 0.2))
    offset = 0.0

    # a callback function to handle changes to declared variables
    def handle_variable_changes(variable):
        name, value = variable.name, variable.value

        if name == "speed":
            timewarp.set_frequency(value)
        if name == "scaleX":
            scale.x = value
        if name == "scaleY":
            scale.y = value

    # a responder which injects the handle_variable_changes()
    # callback into the declared variables (as needed)
    responder = VariableResponder(handle_variable_changes)

    # declare variables
    # these are all of the floating point variety but there are a
    # few different choices (Boolean, Integer, Floating, Option,
    # and ColorSequence)
    # note: only the "speed" variable is assinged the responder
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "speed", 0.001, default_range=(0.0, 0.005), responders=[responder]
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable("offset", offset, responders=[responder])
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "scaleX", scale.x, default_range=(0.0, 0.5), responders=[responder]
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "scaleY", scale.y, default_range=(0.0, 0.5), responders=[responder]
        )
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

        # the timewarp uses its internal speed, as well as the speed
        # of the reference time (in this case timebase.local) to
        # compute its own local time
        z = timewarp.local() + offset

        # use the OpenSimplexNoise utility to fill the scalar field
        osn.fill_scalar_field(field, screen, z, scale.vector, (0, 0))

        # apply the scalar field to the canvas mapping against the
        # layer color palette
        layer.canvas.scalar_field(layer.canvas.screen, field, layer.palette)
