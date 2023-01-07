class AudioSource:
    def __init__(self, manager, name, configuration):
        from variables import VariableResponder
        from cache import Cache
        from fft import FftPlan
        from pathutils import ensure_dirs

        sample_frequency, sample_length = configuration
        self._sample_frequency = sample_frequency
        self._sample_length = sample_length
        self._name = name
        self._manager = manager

        # create root path
        self._root_path = f"{self._manager._sources_path}/{self._name}"
        self._vars_path = f"{self._root_path}/vars"

        # variables which may be dynamically registered for external control
        self._variables = {}
        self._variable_responder = VariableResponder(
            lambda name, value: self._store_variable_value(name, value)
        )

        # attempt to pre-allocate all necessary memory
        self._samples = [0.0] * sample_length
        self._strengths = [0.0] * (sample_length // 2)

        # create an FFT interface
        self._fft_plan = FftPlan(sample_length)
        self._fft_bin_width = self._sample_frequency / self._sample_length

        # ensure that variables will have a directory
        ensure_dirs(self._vars_path)

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

    def _handle_info_change(self, key, value):
        pass

    def _store_variable_value(self, name, value):
        with open(f"{self._vars_path}/{name}", "w") as f:
            f.write(str(value))

    def _load_variable_value(self, name):
        with open(f"{self._vars_path}/{name}", "r") as f:
            return str(f.read())

    def declare_variable(self, cls, *args, **kwargs):
        """
        This method allows automatic association of a declared variable
        to this source so that it may be properly cached.
        """
        # create the variable
        var = cls(*args, **kwargs, responder=self._variable_responder)

        # register it into the layer's list
        self._variables[var.name] = var

        # try loading an existing value for the registered variable
        try:
            var.value = self._load_variable_value(var.name)
        except:
            pass

        # finally store the current value
        self._store_variable_value(var.name, var.value)

        return var

    @property
    def variables(self):
        return self._variables

    @property
    def name(self):
        return self._name

    @property
    def volume(self):
        return self._info.get("volume")

    @volume.setter
    def volume(self, value):
        self._info.set("volume", float(value))

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


class AudioManager:
    def __init__(self, path):
        self._sources = {}
        self._selected = None

        self._root_path = path
        self._sources_path = f"{self._root_path}/sources"

    @property
    def sources(self):
        return self._sources

    def add_source(self, *args, **kwargs):
        source = AudioSource(self, *args, **kwargs)
        self._sources[source.name] = source
        return source
