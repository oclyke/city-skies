"""
    This pattern draws rain drop kind of pattern. The idea of the pattern is as follows:
    1. we create a drop of different sizes
    2. each drop has a specific color 
    3. drop moving animation happens as a group of drops

    The pattern can run from any of the four direction i.e. left, right, top and bottom.
"""
from pysicgl_utils import Display
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import (
    FloatingVariable,
    IntegerVariable,
    OptionVariable,
)
import random


def random_color():
    r_col = int(50 + random.random() * 205)
    g_col = int(50 + random.random() * 205)
    b_col = int(50 + random.random() * 205)
    color = [0, g_col, r_col, b_col]
    color = "".join("%02x" % i for i in color)
    color = int(color, 16)  # change color to hex values
    return color


def frames(layer):
    def update_drops():
        for dr_id, drop in enumerate(drops):
            if (direction == "top") | (direction == "left"):
                drop = [i + drop_speed for i in drop]
                if drop[0] > num_y:
                    drop_size = min_size + random.random() * size_range
                    drop = []
                    for i in range(drop_size):
                        drop.append(i - drop_size)
                    drop_color[
                        dr_id
                    ] = random_color()  # change the color of corresponding drop
                drops[dr_id] = drop
            else:
                drop = [i - drop_speed for i in drop]
                if drop[-1] < 0:
                    drop_size = random.choice(possible_sizes)
                    drop = []
                    for i in range(drop_size):
                        drop.append(i + num_x)
                    drop_color[
                        dr_id
                    ] = random_color()  # change the color of corresponding drop
                drops[dr_id] = drop

    def display_drops():
        for dr_id, drop in enumerate(drops):
            for idx in range(len(drop)):
                if (direction == "top") | (direction == "bottom"):
                    layer.canvas.interface_pixel(drop_color[dr_id], (dr_id, drop[idx]))
                else:
                    layer.canvas.interface_pixel(drop_color[dr_id], (drop[idx], dr_id))

    # variable change handle
    def handle_variable_changes(variable):
        name, value = variable.name, variable.value
        if name == "direction":
            direction = value
        if name == "drop_speed":
            drop_speed = value

    # registering the variable change handler
    responder = VariableResponder(handle_variable_changes)

    # Declaring variables
    layer.variable_manager.declare_variable(
        OptionVariable(
            "direction",
            "right",
            ("top", "bottom", "left", "right"),
            responders=[responder],
        )
    )

    layer.variable_manager.declare_variable(
        IntegerVariable("drop_speed", 1, default_range=(0, 4), responders=[responder])
    )

    layer.variable_manager.declare_variable(
        FloatingVariable(
            "drop_size_minimum", 1.0, default_range=(1.0, 5.0), responders=[responder]
        )
    )

    # the range over which the drop size can be randomly controlled
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "drop_size_range", 2.0, default_range=(0.0, 5.0), responders=[responder]
        )
    )

    # adding variable
    layer.variable_manager.initialize_variables()

    screen = layer.canvas.screen
    display = Display(screen)
    (num_x, num_y) = display.extent

    drop_speed = layer.variable_manager.variables["drop_speed"].value
    direction = layer.variable_manager.variables["direction"].value
    min_size = layer.variable_manager.variables["drop_size_minimum"].value
    size_range = layer.variable_manager.variables["drop_size_range"].value

    possible_sizes = [1, 2, 3]  # possible drop sizes
    drops = []
    drop_color = []

    if (direction == "left") | (direction == "right"):
        temp = num_y
        num_y = num_x
        num_x = temp

    # Initializes the drops and their colors
    for idx in range(num_x):
        drop_size = min_size + random.random() * size_range
        drop = []
        for i in range(drop_size):
            if (direction == "top") | (direction == "left"):
                drop.append(int(random.random() * num_x) - drop_size)
            else:
                drop.append(int(random.random() * num_x) + num_x)
        drops.append(drop)
        drop_color.append(random_color())

    while True:
        yield None

        # get variables
        drop_speed = layer.variable_manager.variables["drop_speed"].value
        direction = layer.variable_manager.variables["direction"].value

        # update the pattern
        update_drops()

        # Draw pattern
        display_drops()
