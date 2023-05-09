"""
    This file draw the randomly moving 5 concentric circles
"""
from pysicgl_utils import Display
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import (
    ColorSequenceVariable,
    FloatingVariable,
    IntegerVariable,
)
import random
import math


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
    (numx, numy) = display.extent
    var_info = [0] * 4
    mov_angle = random.random()
    directions = ["p", "n"]
    circle_info = []

    def move_circles(var_info):
        cd = 0
        circle_speed, total_circles, stepx, stepy = var_info
        for idx, c_in in enumerate(circle_info):
            cx, cy, c_c, dirx, diry = c_in
            rad = dias[0] / 2
            if (cy + rad) >= numy:
                if (cx - rad) <= 0:
                    dirx = "p"
                    diry = "n"
                elif (cx + rad) >= numx:
                    dirx = "n"
                    diry = "n"
                else:
                    diry = "n"
                cd = 1
            elif (cy - rad) <= 0:
                if (cx - rad) <= 0:
                    dirx = "p"
                    diry = "p"
                elif (cx + rad) >= numx:
                    dirx = "n"
                    diry = "p"
                else:
                    diry = "p"
                cd = 1
            elif (cx + rad) >= numx:
                dirx = "n"
                cd = 1
            elif (cx - rad) <= 0:
                dirx = "p"
                cd = 1

            # ---change direction
            if cd == 1:
                mov_angle = random.random()
                stepx = circle_speed * math.cos(mov_angle)
                stepy = circle_speed * math.sin(mov_angle)
                var_info[2] = stepx
                var_info[3] = stepy

            # ---change cx & cy------
            if dirx == "p":
                cx += stepx
            else:
                cx -= stepx

            if diry == "p":
                cy += stepy
            else:
                cy -= stepy
            circle_info[idx] = [cx, cy, c_c, dirx, diry]

    # draw circle patterns
    def draw_pattern():
        for c_in in circle_info:
            cx, cy, c_c, dirx, diry = c_in
            for dia in dias:
                layer.canvas.interface_circle(c_c, (cx, cy), dia)

    # variable change handle
    def handle_variable_changes(variable):
        name, value = variable.name, variable.value
        if name == "circle_speed":
            var_info[0] = value
            var_info[2] = var_info[0] * math.cos(mov_angle)
            var_info[3] = var_info[0] * math.sin(mov_angle)
        if name == "total_circles":
            var_info[1] = value
            circle_info.clear()
            for _ in range(var_info[1]):
                (cx, cy) = (int(random.random() * numx), int(random.random() * numy))
                c_c = random_color()
                dirx = random.choice(directions)
                diry = random.choice(directions)
                circle_info.append([cx, cy, c_c, dirx, diry])

    # Registering the variable change responder
    responder = VariableResponder(handle_variable_changes)

    # declaring variables
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "circle_speed", 1, default_range=(0, 5), responders=[responder]
        )
    )

    layer.variable_manager.declare_variable(
        IntegerVariable(
            "total_circles", 3, default_range=(3, 6), responders=[responder]
        )
    )

    # Initializing variables
    layer.variable_manager.initialize_variables()

    # declare_variables(layer)
    total_circles = int(
        layer.variable_manager.variables["total_circles"].value
    )  # total concentric
    dias = [1, 7, 15, 21, 28]
    circle_speed = layer.variable_manager.variables["circle_speed"].value

    stepx = circle_speed * math.cos(mov_angle)
    stepy = circle_speed * math.sin(mov_angle)

    while True:
        yield None

        # adding variable
        move_circles(var_info)

        # draw pattern
        draw_pattern()
