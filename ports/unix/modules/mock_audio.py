import uasyncio as asyncio
import math
import hidden_shades
from hidden_shades.audio.source import ManagedAudioSource


async def mock_audio_source():
    sample_frequency = 16000
    sample_length = 256

    # add this audio source to the audio manager
    source = ManagedAudioSource(hidden_shades.audio_manager, "SineTest", (sample_frequency, sample_length))

    # select this source for the audio manager
    hidden_shades.audio_manager.select_source("SineTest")

    # initialize the audio manager once all audio sources have been registered
    hidden_shades.audio_manager.initialize()

    def sine_wave(freq, sample_freq):
        # the time period between each step is 1/sample_freq seconds long
        # one full cycle should take 1/freq seconds
        count = 0
        while True:
            phase = count / sample_freq
            # weird note: I thought this should be 2 * math.pi but no matter what I do
            # I get a frequency that is double what I expected, so for now let's just
            # use math.pi
            yield math.sin(math.pi * freq * phase)
            count += 1
            if count > sample_freq:
                count = 0

    # make the test signal
    sine_400hz = sine_wave(8000, sample_frequency)

    # output to view the fft strengths
    strengths = [0.0] * 32

    while True:
        # simulate waiting for a real audio source to fill the buffer
        for idx in range(sample_length):
            source._samples[idx] = next(sine_400hz)
        await asyncio.sleep(sample_length / sample_frequency)

        # now that the audio source is filled with data compute the fft
        source.compute_fft()
        stats = source.fft_stats
        _, _, max_idx = stats
        bin_width = source.fft_bin_width
        strongest_freq = max_idx * source.fft_bin_width
        source.get_fft_strengths(strengths)

        # print(strengths)
        # print('')
        # print(stats, bin_width, strongest_freq)
