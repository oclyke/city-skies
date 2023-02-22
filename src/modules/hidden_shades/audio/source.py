from cache import Cache
from fft import FftPlan
from ..variables.manager import VariableManager

class AudioSource:
    def __init__(self, configuration):
        sample_frequency, sample_length = configuration
        self._sample_frequency = sample_frequency
        self._sample_length = sample_length

        # attempt to pre-allocate all necessary memory
        self._samples = [0.0] * sample_length
        self._strengths = [0.0] * (sample_length // 2)

        # create an FFT interface
        self._fft_plan = FftPlan(sample_length)
        self._fft_bin_width = self._sample_frequency / self._sample_length

    def compute_fft(self):
        self._fft_plan.feed(self._samples)
        self._fft_plan.window()
        self._fft_plan.execute()

    def get_fft_strengths(self, target):
        return self._fft_plan.output(target)
    
    def align_fft_strengths(self, target):
        return self._fft_plan.align(target)

    def reshape_fft_strengths(self, target, config):
        return self._fft_plan.reshape(target, config)

    @property
    def variables(self):
        return self._variables

    @property
    def fft_bin_width(self):
        return self._fft_bin_width

    @property
    def fft_stats(self):
        return self._fft_plan.stats()

class ManagedAudioSource(AudioSource):
    def __init__(self, manager, name, configuration):
        super().__init__(configuration)

        self._name = name
        self._manager = manager

        # create root path
        self._root_path = f"{self._manager._sources_path}/{self._name}"

        # variables which may be dynamically registered for external control
        self._variables = {}
        self._variable_responder = VariableManager(f"{self._root_path}/vars")

        # info recorded in a cache
        # (this must be done after default values are set because it will automatically enable the module if possible)
        initial_info = {
            "volume": 0.5,
        }
        self._info = Cache(
            f"{self._root_path}/info",
            initial_info,
            lambda key, value: self._handle_info_change(key, value),
        )

        # add this source to the manager
        manager.add_source(self)

    def _handle_info_change(self, key, value):
        pass

    @property
    def name(self):
        return self._name
