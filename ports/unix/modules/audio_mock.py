import uasyncio as asyncio
import math
import hidden_shades
from hidden_shades.audio.source import ManagedAudioSource


class MockAudioSource(ManagedAudioSource):
    def __init__(self, path, name, freq, fft_config):
        super().__init__(path, name, fft_config)

        self._sample_frequency, self._sample_length = fft_config
        self._freq = freq

    async def run(self):
        def sine_wave(freq, sample_freq):
            # the time period between each step is 1/sample_freq seconds long
            # one full cycle should take 1/freq seconds
            count = 0
            while True:
                phase = count / sample_freq
                yield math.sin(2 * math.pi * freq * phase)
                count += 1
                if count > sample_freq:
                    count = 0

        # make the test signal
        sine_generator = sine_wave(self._freq, self._sample_frequency)

        # output to view the fft strengths
        strengths = [0.0] * 32

        while True:
            # simulate waiting for a real audio source to fill the buffer
            for idx in range(self._sample_length):
                self._buffer[idx] = next(sine_generator)
            await asyncio.sleep(self._sample_length / self._sample_frequency)

            # scale the audio data by the volume
            self.apply_volume()

            # feed the audio data to the fft
            self.fft.plan.feed(self._buffer)

            # now that the audio source is filled with data compute the fft
            self.fft.compute()

            # zero out low frequency fft bins
            self.zero_low_fft_bins()