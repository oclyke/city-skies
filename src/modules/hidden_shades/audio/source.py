from fft import FftPlan, bin_stats
from reshape import reshape
from buffer import FloatBuffer
from ..variables.manager import VariableManager
from ..variables.types import FloatingVariable


class AudioSourceFFT:
    def __init__(self, sample_frequency, input_buffer):
        self._input_buffer = input_buffer
        sample_length = len(self._input_buffer)

        # create an output buffer
        self._output_buffer = FloatBuffer(sample_length // 2)
        self._plan = FftPlan(
            (self._input_buffer, self._output_buffer), sample_frequency
        )

        # create an output meant to hold nonlinear-corrected fft results
        self._reshape_factor = 1.3
        bins_required = reshape(self._reshape_factor, self._output_buffer, None)
        self._reshaped_output_buffer = FloatBuffer(bins_required)

    def compute(self):
        self._plan.window()
        self._plan.execute()
        reshape(self._reshape_factor, self._output_buffer, self._reshaped_output_buffer)

    @property
    def plan(self):
        return self._plan

    @property
    def output(self):
        return self._output_buffer

    @property
    def reshaped(self):
        return self._reshaped_output_buffer


class AudioSource:
    def __init__(self, name, configuration):
        self._name = name
        sample_frequency, sample_length = configuration
        self._sample_frequency = sample_frequency
        self._sample_length = sample_length

        # create an FloatBuffer that will hold the samples
        # (this is a faster object to use to store floating point values)
        self._buffer = FloatBuffer(sample_length)

        # create an AudioSourceFFT for the source
        self._fft = AudioSourceFFT(sample_frequency, self._buffer)

    async def run(self):
        """
        This is a stub of the coroutine which an AudioSource implements
        to handle audio data.

        Responsibilities of this routine are as follows:
        - fill the buffer with audio samples

        This coroutine may manipulate the data as needed.
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
        self._private_variable_manager.initialize_variables()

    def apply_volume(self):
        # scale the audio data by the volume
        volume = self.private_variable_manager.variables["volume"].value
        self._buffer.scale(volume)

    @property
    def variable_manager(self):
        return self._variable_manager

    @property
    def private_variable_manager(self):
        return self._private_variable_manager
