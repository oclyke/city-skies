from fft import FftPlan
from resource import Resource


class AudioSource(Resource):
    def __init__(self, name, configuration):
        super().__init__(name)
        sample_frequency, sample_length = configuration
        self._sample_frequency = sample_frequency
        self._sample_length = sample_length
        self._name = name
        self._volume = 0.5

        # attempt to pre-allocate all necessary memory
        self._samples = [0.0] * sample_length
        self._strengths = [0.0] * (sample_length // 2)

        # create an FFT interface
        self._fft_plan = FftPlan(sample_length)
        self._fft_bin_width = self._sample_frequency / self._sample_length

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = float(value)

    def compute_fft(self):
        self._fft_plan.feed(self._samples)
        self._fft_plan.window()
        self._fft_plan.execute()

    @property
    def fft_bin_width(self):
        return self._fft_bin_width

    @property
    def fft_stats(self):
        return self._fft_plan.stats()

    def get_fft_strengths(self, target):
        return self._fft_plan.output(target)

    def reshape_fft_strengths(self, target, config):
        return self._fft_plan.reshape(target, config)


class AudioManager(Resource):
    def __init__(self, name):
        super().__init__(name)
        self._sources = {}
        self._selected = None

    @property
    def sources(self):
        return self._sources

    def register_source(self, source):
        self._sources[source.name] = source


# create a singleton instance of the audio manager
audio_manager = AudioManager("audio")
