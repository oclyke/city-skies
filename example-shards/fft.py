import hidden_shades


def frames(layer):
    print("audio source: ", hidden_shades.audio_manager.audio_source.name)

    # allocate a list to hold the fft results
    strengths = [0.0] * 32

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
