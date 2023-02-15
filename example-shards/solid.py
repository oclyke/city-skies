# a simple layer for a solid color


def frames(layer):
    while True:
        yield None

        layer.canvas.interface_fill(layer.palette[0])
