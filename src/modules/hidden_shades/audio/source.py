from fft import FftPlan, AudioBuffer
from ..variables.manager import VariableManager
from ..variables.types import FloatingVariable


class AudioSourceFFT:
    def __init__(self, config):
        sample_frequency, sample_length = config
        self._sample_frequency = sample_frequency
        self._sample_length = sample_length

        self._plan = FftPlan(sample_length, sample_frequency)

    def compute(self):
        self._plan.window()
        self._plan.execute()

    @property
    def plan(self):
        return self._plan


class AudioSource:
    def __init__(self, name, configuration):
        self._name = name
        sample_frequency, sample_length = configuration
        self._sample_frequency = sample_frequency
        self._sample_length = sample_length

        # create an AudioBuffer that will hold the samples
        # (this is a faster object to use to store floating point values)
        self._buffer = AudioBuffer(sample_length)

        # create an AudioSourceFFT for the source
        self._fft = AudioSourceFFT((sample_frequency, sample_length))

    async def run(self):
        """
        This is a stub of the coroutine which an AudioSource implements
        to handle audio data.
        """

    @property
    def name(self):
        return self._name

    @property
    def fft(self):
        return self._fft


class ManagedAudioSource(AudioSource):
    def __init__(self, path, name, configuration):
        super().__init__(name, configuration)

        self._root_path = path

        # create root path
        self._root_path = f"{self._root_path}/{self._name}"

        # variables which may be dynamically registered for external control
        self._variable_manager = VariableManager(f"{self._root_path}/vars")

        # declare private variables
        self._private_variable_manager = VariableManager(
            f"{self._root_path}/private_vars"
        )
        self._private_variable_manager.declare_variable(
            FloatingVariable(
                0.5,
                "volume",
                default_range=(0.0, 1.0),
            )
        )
        self._private_variable_manager.declare_variable(
            FloatingVariable(
                100.0,
                "fft_low_cutoff_frequency",
                default_range=(100.0, 1000.0),
                allowed_range=(0.0, 20000.0),
            )
        )
        self._private_variable_manager.initialize_variables()

    def apply_volume(self):
        # scale the audio data by the volume
        volume = self.private_variable_manager.variables["volume"].value
        self._buffer.scale(volume)

    def zero_low_fft_bins(self):
        bins_to_zero = (
            self.private_variable_manager.variables["fft_low_cutoff_frequency"].value
            // self.fft.plan.bin_width
        ) + 1
        for idx in range(bins_to_zero):
            self.fft.plan[idx] = 0

    @property
    def variable_manager(self):
        return self._variable_manager

    @property
    def private_variable_manager(self):
        return self._private_variable_manager
