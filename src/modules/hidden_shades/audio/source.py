from fft import FftPlan, bin_stats
from reshape import reshape
from buffer import FloatBuffer
from ..variables.manager import VariableManager
from ..variables.types import FloatingVariable
from ..variables.responder import VariableResponder


class AudioSourceFFT:
    def __init__(self, sample_frequency, input_buffer):
        self._input_buffer = input_buffer
        sample_length = len(self._input_buffer)

        # create an output buffer
        self._output_buffer = FloatBuffer(sample_length // 2)
        self._plan = FftPlan(
            (self._input_buffer, self._output_buffer), sample_frequency
        )

    def compute(self):
        self._plan.window()
        self._plan.execute()

    @property
    def plan(self):
        return self._plan

    @property
    def output(self):
        return self._output_buffer


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

        # create an output meant to hold nonlinear-corrected fft results
        # this buffer will have equal length to the output buffer despite that the number of bins required may be substantially more or substantially fewer depending on the chosen fft reshape factor.
        self._reshaped_fft_output_buffer = FloatBuffer(len(self._fft._output_buffer))
        self._reshaped_fft_output = self._reshaped_fft_output_buffer.reference()

        self._floor = None
        self._factor = None

        # create root path
        self._root_path = f"{path}/{self._name}"

        # variables which may be dynamically registered for external control
        self._variable_manager = VariableManager(f"{self._root_path}/vars")

        # declare private variables
        self._private_variable_responder = VariableResponder(
            lambda variable: self._handle_private_variable_change(variable)
        )
        self._private_variable_manager = VariableManager(
            f"{self._root_path}/private_vars"
        )
        self._private_variable_manager.declare_variable(
            FloatingVariable(
                0.5,
                "volume",
                default_range=(0.0, 1.0),
                responders=[self._private_variable_responder],
            )
        )
        self._private_variable_manager.declare_variable(
            FloatingVariable(
                1.5,
                "fft_reshape_factor",
                default_range=(1.5, 2.0),
                allowed_range=(0.5, 3.0),
                responders=[self._private_variable_responder],
            )
        )
        self._private_variable_manager.declare_variable(
            FloatingVariable(
                500.0,
                "fft_reshape_floor",
                default_range=(0.0, 1000.0),
                responders=[self._private_variable_responder],
            )
        )
        self._private_variable_manager.initialize_variables()

    def _handle_private_variable_change(self, variable):
        if variable.name == "fft_reshape_factor":
            # create a reference to the reshaped fft output buffer which is sized according to the number of bins actually required
            reshape_factor = self.private_variable_manager.variables[
                "fft_reshape_factor"
            ].value
            bins_required = reshape((reshape_factor, 0), self._fft._output_buffer, None)
            bins_available = len(self._reshaped_fft_output_buffer)
            if bins_required > bins_available:
                bins_required = bins_available
            self._reshaped_fft_output = self._reshaped_fft_output_buffer.reference(
                window=(0, bins_required)
            )

    def apply_volume(self):
        # scale the audio data by the volume
        volume = self.private_variable_manager.variables["volume"].value
        self._buffer.scale(volume)

    def fft_postprocess(self):
        reshape_factor = self.private_variable_manager.variables[
            "fft_reshape_factor"
        ].value
        reshape_floor = self.private_variable_manager.variables[
            "fft_reshape_floor"
        ].value
        reshape_config = (reshape_factor, reshape_floor)
        reshape(reshape_config, self._fft._output_buffer, self._reshaped_fft_output)

    @property
    def variable_manager(self):
        return self._variable_manager

    @property
    def private_variable_manager(self):
        return self._private_variable_manager

    @property
    def reshaped_fft_output(self):
        return self._reshaped_fft_output
