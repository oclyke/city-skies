import hidden_shades
from pysicgl_utils import Display
from fft import bin_stats
import reshape


def frames(layer):
    print("audio source: ", hidden_shades.audio_manager.audio_source.name)

    screen = layer.canvas.screen
    display = Display(screen)
    (numx, numy) = display.extent
    (maxx, maxy) = display.shape

    # allocate a list to hold the fft results
    strengths = [0.0] * numx

    while True:
        yield None

        audio_source = hidden_shades.audio_manager.audio_source

        # # choose an fft output to view
        # bins = audio_source.fft.output
        bins = audio_source.fft.reshaped

        # align the bins to the strenths (interpolate)
        bins.align(strengths)

        # clear the background
        layer.canvas.interface_fill(0x00000000)

        # draw vertical bars representing the fft strength at each x location
        for idx in range(numx):
            layer.canvas.interface_line(
                0x00FF0000, (idx, 0), (idx, strengths[idx] * numy)
            )
