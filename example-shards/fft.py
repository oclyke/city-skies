import hidden_shades
from pysicgl_utils import Display


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

        # # reformat the fft bins to make them easier to display
        # audio_source.fft.plan.output(strengths)
        # audio_source.fft.plan.align(strengths)
        reshape_config = (1.0, 0)  # (factor, floor)
        audio_source.fft.plan.reshape(strengths, reshape_config)

        sum, max, max_idx = audio_source.fft.plan.stats()
        bin_width = audio_source.fft.plan.bin_width
        strongest_freq = max_idx * bin_width
        print(f"strongest[{max_idx}]: {strongest_freq:012.2f} hz ({max:012.2f})")

        # clear the background
        layer.canvas.interface_fill(0x00000000)

        # draw vertical bars representing the fft strength at each x location
        for idx in range(numx):
            layer.canvas.interface_line(0x00ff0000, (idx, 0), (idx, strengths[idx] * numy))
