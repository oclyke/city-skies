import pysicgl
from pysicgl_utils import Display
from hidden_shades import timebase, palette
from hidden_shades.timewarp import TimeWarp
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import FloatingVariable, OptionVariable


def frames(layer):
    screen = layer.canvas.screen
    display = Display(screen)
    field = pysicgl.ScalarField(screen.pixels)
    timewarp = TimeWarp(timebase.local)

    field = pysicgl.ScalarField(screen.pixels)

    def compute_scalar_field():
        """
        this function is called to recompute the scalar field.
        it must be re-run when a dependency variable changes.
        there is no automatic mechanism to track these dependencies, so it must
        be added to a reponder callback for any of the dependencies.
        """
        variables = layer.variable_manager.variables

        scale = variables["scale"].value
        side_var = variables["side"]

        # determine signs depending on the direction option
        if side_var.matches("left"):
            sx, sy = (1, 0)
        if side_var.matches("right"):
            sx, sy = (-1, 0)
        if side_var.matches("top"):
            sx, sy = (0, 1)
        if side_var.matches("bottom"):
            sx, sy = (0, -1)

        # use the scale and direction signs to compute a scalar field
        for info in display.pixel_info():
            idx, coordinates, position = info
            x, y = position

            field[idx] = scale * (sx * x + sy * y)

    # a callback function to handle changes to declared variables
    def handle_variable_changes(name, value):
        if name == "speed":
            timewarp.set_frequency(value)
        if name == "scale":
            compute_scalar_field()
        if name == "side":
            compute_scalar_field()

    # a responder which injects the handle_variable_changes()
    # callback into the declared variables (as needed)
    responder = VariableResponder(handle_variable_changes)

    # declare variables
    layer.variable_manager.declare_variable(
        FloatingVariable(0.001, "speed", default_range=(0, 0.05), responders=[responder])
    )
    layer.variable_manager.declare_variable(
        FloatingVariable(1.0, "scale", responders=[responder])
    )
    layer.variable_manager.declare_variable(
        OptionVariable(
            0,
            "side",
            ("left", "right", "top", "bottom"),
            responders=[responder],
        )
    )
    layer.variable_manager.initialize_variables()

    # compute the initial scalar field (once variables are all declared)
    compute_scalar_field()

    while True:
        yield None

        # apply the scalar field to the canvas mapping against the selected palette
        offset = timewarp.local()
        layer.canvas.scalar_field(layer.canvas.screen, field, palette.primary, offset)
