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

def declare_variables(layer):
    layer.variable_manager.declare_variable(
        FloatingVariable("speed",2,default_range=(2, 4),)
    )

    layer.variable_manager.declare_variable(
        FloatingVariable("total_circles",3,default_range=(3,6),)
    )

def move(cx, cy, dirx, diry, rad, speed, num_x, num_y, stepx, stepy):
    cd = 0

    if (cy + rad) >= num_y:
        if (cx - rad) <= 0:
            dirx = "p"
            diry = "n"
        elif (cx + rad) >= num_x:
            dirx = "n"
            diry = "n"
        else:
            diry = "n"
        cd = 1
    elif (cy - rad) <= 0:
        if (cx - rad) <= 0:
            dirx = "p"
            diry = "p"
        elif (cx + rad) >= num_x:
            dirx = "n"
            diry = "p"
        else:
            diry = "p"
        cd = 1
    elif (cx + rad) >= num_x:
        dirx = "n"
        cd = 1
    elif (cx - rad) <= 0:
        dirx = "p"
        cd = 1

    # ---change direction
    if cd == 1:
        mov_angle = random.random()
        stepx = speed * math.cos(mov_angle)
        stepy = speed * math.sin(mov_angle)

    # ---change cx & cy------
    if dirx == "p":
        cx += stepx
    else:
        cx -= stepx

    if diry == "p":
        cy += stepy
    else:
        cy -= stepy

    return (int(cx), int(cy), dirx, diry)


def frames(layer):
    declare_variables(layer)
    total_circles = int(layer.variable_manager.variables["total_circles"].value) # total concentric
    dias = [1, 7, 15, 21, 28]
    speed = int(layer.variable_manager.variables["speed"].value)
    screen = layer.canvas.screen
    display = Display(screen)
    (numx, numy) = display.extent

    mov_angle = random.random()
    stepx = speed * math.cos(mov_angle)
    stepy = speed * math.sin(mov_angle)
    directions = ["p", "n"]
    circle_info = []

    for _ in range(total_circles):
        (cx, cy) = (int(random.random() * numx), int(random.random() * numy))
        c_c = random_color()
        c_c = ''.join('%02x'%i for i in c_c)
        c_c = int(c_c, 16) # change color to hex values
        dirx = random.choice(directions)
        diry = random.choice(directions)
        circle_info.append([cx, cy, c_c, dirx, diry])

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
                cx, cy, dirx, diry, dias[0] / 2, speed, numx, numy, stepx, stepy
            )
            circle_info[idx] = [cx, cy, c_c, dirx, diry]

        # draw pattern
        for c_in in circle_info:
            cx, cy, c_c, dirx, diry = c_in
            for dia in dias:
                layer.canvas.interface_circle(c_c, (cx, cy), dia)
