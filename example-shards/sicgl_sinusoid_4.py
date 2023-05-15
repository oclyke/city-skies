"""
    This file drwas collapsing concentric circles
"""
from hidden_shades import timebase
from hidden_shades.timewarp import TimeWarp
from pysicgl_utils import Display
from hidden_shades.frequency import FreqCounter
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import (
    ColorSequenceVariable,
    FloatingVariable,
    IntegerVariable,
)
import random
import math
import time


def random_color():
    r_col = int(50 + random.random() * 205)
    g_col = int(50 + random.random() * 205)
    b_col = int(50 + random.random() * 205)
    color = [0, g_col, r_col, b_col]
    color = "".join("%02x" % i for i in color)
    color = int(color, 16)  # change color to hex values
    return color

def frames(layer):
    screen = layer.canvas.screen
    display = Display(screen)
    (num_x, num_y) = display.extent
    x_val = range(6, num_x - 6)
    y_val = range(4, num_y - 4)
    circle_info = []

    # update circles
    def update_circles(con_circles, dias):
        for id, cr in enumerate(con_circles):
            con_circles[id] -= 1
            if con_circles[id] == 0:
                con_circles[id] = len(dias) - 1
    
    # draw circle patterns
    def draw_pattern():
        for cr in con_circles:
            for c_in in circle_info:
                cx, cy, c_c = c_in
                layer.canvas.interface_circle(c_c, (cx, cy), dias[cr])

    # variable change handle
    def handle_variable_changes(variable):
        name, value = variable.name, variable.value
        if name == "total_circles":
            total_circles = value
            circle_info.clear()
            for i in range(total_circles):
                (cx, cy) = (random.choice(x_val), random.choice(y_val))
                circle_info.append([cx, cy, random_color()])

    # Registering the variable change responder
    responder = VariableResponder(handle_variable_changes)

    # declaring variables
    layer.variable_manager.declare_variable(
        FloatingVariable("collapse_speed", 0.1, default_range=(0, 4), responders=[responder])
    )
    layer.variable_manager.declare_variable(
        IntegerVariable(
            "total_circles", 1, default_range=(1, 4), responders=[responder]
        )
    )

    # Initializing variables
    layer.variable_manager.initialize_variables()

    total_circles = layer.variable_manager.variables["total_circles"].value
    dias = range(1, 40, 2)
    con_circles = [5, 10, 15, len(dias) - 1]  # number of concentric circles

    timewarp = TimeWarp(timebase.local)
    # timewarp.set_frequency(variable.value)
    timewarp.set_frequency(100)

    # advance_counter = FreqCounter(1.0)
    advance_counter = FreqCounter(1)
    # reset the advance counter
    advance_counter.reset(timebase.local())

    while True:
        yield None

        # run the animation
        update_circles(con_circles, dias)

        # draw pattern
        draw_pattern()
