import pysicgl
import fieldgen
from pysicgl_utils import Display
from hidden_shades import timebase
from hidden_shades.timewarp import TimeWarp
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import FloatingVariable

def frames(layer):
    screen = layer.canvas.screen
    display = Display(screen)

    # unpack info about the screen
    (numx, numy) = display.extent
    (maxx, maxy) = display.shape

    # create a field to cover all pixels in the screen
    field = pysicgl.ScalarField(screen.pixels)

    # create a timewarp
    timewarp = TimeWarp(timebase.local)


    def handle_variable_changes(variable):
        name = variable.name

        if name == "speed":
            timewarp.set_frequency(variable.value)

    # a responder which injects the handle_variable_changes()
    # callback into the declared variables (as needed)
    responder = VariableResponder(handle_variable_changes)

    # declare variables
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "speed", 0.0001, default_range=(0, 0.05), responders=[responder]
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "scale", 0.8, default_range=(0.1, 5.0)
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "frequency", 40.0, default_range=(0, 50.0)
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "centerX", -0.4, default_range=(-0.5, 0.5)
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "centerY", 0.4, default_range=(-0.5, 0.5)
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "offset", 0.2, default_range=(0, 1.0)
        )
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "decay", 20.0, default_range=(0.0, 30.0)
        )
    )
    layer.variable_manager.initialize_variables()

    while True:
        yield None

        # get variables
        center = (0.5 + layer.variable_manager.variables["centerX"].value,
                  0.5 + layer.variable_manager.variables["centerY"].value)
        scale = layer.variable_manager.variables["scale"].value
        frequency = layer.variable_manager.variables["frequency"].value
        offset = layer.variable_manager.variables["offset"].value
        decay = layer.variable_manager.variables["decay"].value

        # generate the scalar field
        fieldgen.sinusoids(screen, field, center, scale, frequency, offset, decay)

        # show the scalar field
        layer.canvas.scalar_field(layer.canvas.screen, field, layer.palette, timewarp.local())
