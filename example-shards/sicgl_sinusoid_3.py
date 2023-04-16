import pysicgl
from hidden_shades import timebase
from pysicgl_utils import Display
from hidden_shades.frequency import FreqCounter
from hidden_shades.variables.types import ColorSequenceVariable, FloatingVariable
import random
import math

def random_color():
  r_col = int(50+random.random()*205)
  g_col = int(50+random.random()*205)
  b_col = int(50+random.random()*205)
  return [0,g_col,r_col,b_col]

def convert_color(color):
    color = ''.join('%02x'%i for i in color)
    color = int(color, 16) # change color to hex values
    return color

def declare_variables(layer):

    layer.variable_manager.declare_variable(
        FloatingVariable("speed",0.1,default_range=(0, 4),)
    )

def move(cx, cy, dirx, diry, rad, speed, num_x, num_y, stepx, stepy):
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
        stepx = speed * math.cos(mov_angle)
        stepy = speed * math.sin(mov_angle)

    # ---change cx & cy------
    if dirx == "p":
        cx += 0.5 + stepx
    else:
        cx -= 0.5 + stepx

    if diry == "p":
        cy += 0.5 + stepy
    else:
        cy -= 0.5 + stepy

    return (cx, cy, dirx, diry)


def frames(layer):
    declare_variables(layer)

    screen = layer.canvas.screen
    display = Display(screen)
    (num_x, num_y) = display.extent

    dias = [3, 13, 21]
    speed = int(layer.variable_manager.variables["speed"].value)
    mov_angle = random.random()
    stepx = speed * math.cos(mov_angle)
    stepy = speed * math.sin(mov_angle)
    directions = ["p", "n"]
    circle_info = []
    c_c = [[0, 0, 0, 255], [0, 255, 0, 0], [0, 0, 255, 0]]  # circles color
    
    for id in range(3):
        (cx, cy) = (int(random.random() * num_x), int(random.random() * num_y))
        dirx = random.choice(directions)
        diry = random.choice(directions)
        circle_info.append([cx, cy, c_c[id], dirx, diry])

    # adding variable
    layer.variable_manager.initialize_variables()
    # the advance counter is used to control the number of animation steps performed during each frame
    # the speed of the animation will be controlled the timewarp
    advance_counter = FreqCounter(1.0)

    # reset the advance counter
    advance_counter.reset(timebase.local())
    while True:
        yield None

        # Clear background
        layer.canvas.interface_fill(0x00000000)

        # run the animation       
        for idx, c_in in enumerate(circle_info):
            cx, cy, c_c, dirx, diry = c_in
            cx, cy, dirx, diry = move(
                cx, cy, dirx, diry, dias[0] / 2, speed, num_x, num_y, stepx, stepy
            )
            circle_info[idx] = [cx, cy, c_c, dirx, diry]

        # draw pattern
        for c_in in circle_info:
            cx, cy, c_c, dirx, diry = c_in
            c_c_1 = [int(i * 0.5) for i in c_c]
            for dia in dias:
                layer.canvas.interface_circle(convert_color(c_c), (cx, cy), dia)
                layer.canvas.interface_circle(convert_color(c_c_1), (cx, cy), dia + 2)
