from fft import FftPlan


class Fft:
    def __init__(self, samples):
        self._samples = samples
        self._plan = FftPlan(len(samples))

    def compute_fft(self):
        self._plan.feed(self._samples)
        self._plan.window()
        self._plan.execute()

    def get_strengths(self, target):
        return self._plan.output(target)

    def reshape_strengths(self, target, config):
        return self._plan.reshape(target, config)


class AudioSource:
    def __init__(self, name, configuration):
        sample_rate, sample_length = configuration
        self._sample_rate = sample_rate
        self._sample_length = sample_length
        self._name = name

        # allow for sources to keep variables
        self._variables = {}

        # attempt to pre-allocate all necessary memory
        self._samples = [0.0] * sample_length
        self._strengths = [0.0] * (sample_length // 2)

        # create an FFT interface
        self._fft = Fft(self._samples)

    @property
    def fft(self):
        return self._fft

    @property
    def variables(self):
        return self._variables

    def register_variable(self, variable):
        self._variables[variable.name] = variable


class AudioManager:
    def __init__(self):
        self._sources = []
        self._selected = None

    @property
    def sources(self):
        return self._sources

    def add_source(self, source):
        self._sources.append(source)


# create a singleton instance of the audio manager
audio = AudioManager()
