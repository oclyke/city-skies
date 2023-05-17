from pysicgl_utils import Display
import pysicgl


def frames(layer):
    screen = layer.canvas.screen
    display = Display(screen)
    (numx, numy) = display.extent
    (maxx, maxy) = display.shape

    while True:
        yield None

        layer.canvas.interface_circle(
            pysicgl.ALPHA_TRANSPARENCY_HALF | 0x00AFAFAF,
            (int(numx / 2), int(numy / 2)),
            int(numx / 2),
        )
