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
        FloatingVariable("direction",1,default_range=(0, 4),)
    )

    layer.variable_manager.declare_variable(
        FloatingVariable("speed",1,default_range=(0, 4),)
    )


def drop_update(drops,num_x,num_y,speed,drop_color,possible_sizes,dir):
  for dr_id, drop in enumerate(drops):
    if (dir == 0) | (dir == 2):
      drop = [i+speed for i in drop]
      if drop[0] > num_y:
        drop_size = random.choice(possible_sizes)
        drop = []
        for i in range(drop_size):
          drop.append(i - drop_size)
        drop_color[dr_id] = random_color() #change the color of corresponding drop
      drops[dr_id] = drop
    else:
      drop = [i-speed for i in drop]
      if drop[-1] < 0:
        drop_size = random.choice(possible_sizes)
        drop = []
        for i in range(drop_size):
          drop.append(i+num_x)
        drop_color[dr_id] = random_color() #change the color of corresponding drop
      drops[dr_id] = drop


def display_drops(layer,dr_id,drop,dir,drop_color):
    for idx in range(len(drop)):
      if (dir == 0) | (dir == 1):
          layer.canvas.interface_pixel(convert_color(drop_color[dr_id]),(dr_id,drop[idx]))
      else:
          layer.canvas.interface_pixel(convert_color(drop_color[dr_id]),(drop[idx],dr_id))


def frames(layer):
    declare_variables(layer)

    screen = layer.canvas.screen
    display = Display(screen)
    (num_x, num_y) = display.extent

    speed = int(layer.variable_manager.variables["speed"].value)
    dir = int(layer.variable_manager.variables["direction"].value)
    print('direction: ', dir)
    possible_sizes = [1,2,3] # possible drop sizes
    drops =[]
    drop_color = []
    
    if (dir == 2) | (dir == 3):
        temp = num_y
        num_y = num_x
        num_x = temp

    for idx in range(num_x):
        drop_size = random.choice(possible_sizes)
        drop = []
        for i in range(drop_size):
            if (dir == 0) | (dir == 2):
                drop.append(i - drop_size)
            else:
                drop.append(i+num_x)
        drops.append(drop)
        drop_color.append(random_color())

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
        drop_update(drops,num_x,num_y,speed,drop_color,possible_sizes,dir)

        # draw pattern
        for dr_id,drop in enumerate(drops):
            display_drops(layer,dr_id,drop,dir,drop_color)
