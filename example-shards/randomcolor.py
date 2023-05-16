# shows how to use a random color from the color palette
import random


def frames(layer):
    while True:
        yield None

        random_number = random.random()
        random_palette_color = layer.palette.interpolate(random_number)
        layer.canvas.interface_fill(random_palette_color)
