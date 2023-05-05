"""
    This file draws 3 circles with 3 concentric circles moving randomly.
"""
from pysicgl_utils import Display
from hidden_shades.variables.responder import VariableResponder
from hidden_shades.variables.types import IntegerVariable, FloatingVariable
import random
import math


def convert_color(color):
    color = "".join("%02x" % i for i in color)
    color = int(color, 16)  # change color to hex values
    return color


def frames(layer):
    # check speed
    def check_speed(var_info):
        circle_speed, prev_speed, stepx, stepy = var_info

        var_info[0] = layer.variable_manager.variables["circle_speed"].value
        if circle_speed != prev_speed:
            stepx = circle_speed * math.cos(mov_angle)
            stepy = circle_speed * math.sin(mov_angle)
            prev_speed = circle_speed
        var_info[1] = prev_speed
        var_info[2] = stepx
        var_info[3] = stepy

    # moving the circles
    def move_circles(var_info):
        circle_speed, prev_speed, stepx, stepy = var_info
        for idx, c_in in enumerate(circle_info):
            cx, cy, c_c, dirx, diry = c_in
            rad = dias[0]
            cd = 0
            box = 2
            if (cy + rad) >= num_y - box:
                if (cx - rad) <= box:
                    dirx = "p"
                    diry = "n"
                elif (cx + rad) >= num_x - box:
                    dirx = "n"
                    diry = "n"
                else:
                    diry = "n"
                cd = 1
            elif (cy - rad) <= box:
                if (cx - rad) <= box:
                    dirx = "p"
                    diry = "p"
                elif (cx + rad) >= num_x - box:
                    dirx = "n"
                    diry = "p"
                else:
                    diry = "p"
                cd = 1
            elif (cx + rad) >= num_x - box:
                dirx = "n"
                cd = 1
            elif (cx - rad) <= box:
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
            c_c_1 = [int(i * 0.5) for i in c_c]
            for dia in dias:
                layer.canvas.interface_circle(convert_color(c_c), (cx, cy), dia)
                layer.canvas.interface_circle(convert_color(c_c_1), (cx, cy), dia + 2)

    # variable change handle
    def handle_variable_changes(variable):
        name, value = variable.name, variable.value
        if name == "circle_speed":
            circle_speed = value

    # registering the variable change handler
    responder = VariableResponder(handle_variable_changes)

    # Declaring variables
    layer.variable_manager.declare_variable(
        FloatingVariable(
            "circle_speed", 0.65, default_range=(0, 5), responders=[responder]
        )
    )

    # Initializing variables
    layer.variable_manager.initialize_variables()

    screen = layer.canvas.screen
    display = Display(screen)
    (num_x, num_y) = display.extent

    dias = [3, 13, 21]
    circle_speed = layer.variable_manager.variables["circle_speed"].value
    prev_speed = circle_speed
    mov_angle = random.random()
    stepx = circle_speed * math.cos(mov_angle)
    stepy = circle_speed * math.sin(mov_angle)
    directions = ["p", "n"]
    circle_info = []
    c_c = [[0, 0, 0, 255], [0, 255, 0, 0], [0, 0, 255, 0]]  # circles color

    for id in range(3):
        (cx, cy) = (int(random.random() * num_x), int(random.random() * num_y))
        dirx = random.choice(directions)
        diry = random.choice(directions)
        circle_info.append([cx, cy, c_c[id], dirx, diry])

    var_info = [circle_speed, prev_speed, stepx, stepy]
    while True:
        yield None

        # check Speed
        check_speed(var_info)

        # Moving the circles
        move_circles(var_info)

        # draw pattern
        draw_pattern()
