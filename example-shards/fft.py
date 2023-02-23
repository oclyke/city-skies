import hidden_shades

def frames(layer):
    print("audio source: ", hidden_shades.audio_manager.audio_source)


    # allocate a list to hold the fft results
    strengths = [0.0] * 32

    while True:
        yield None

        audio_source = hidden_shades.audio_manager.audio_source

        # # do some processing on the fft bins to make them easier to display
        # audio_source.get_fft_strengths(strengths)
        # audio_source.align_fft_strengths(strengths)
        reshape_config = (1.0, 0) # (factor, floor)
        audio_source.reshape_fft_strengths(strengths, reshape_config)

        # print(audio_source)

        print((audio_source.fft_stats, strengths))
        print('')

        layer.canvas.interface_fill(layer.palette[0])
