class SpeedManager:
    def __init__(self, path):
        import time
        from cache import Cache
        from variables import VariableResponder
        from variables import DoubleVariable

        # store starting time
        self._time = time.ticks_ms()

        # store paths
        self._root_path = path
        self._vars_path = f"{self._root_path}/vars"

        # variables which may be dynamically registered for external control
        self._variables = {}
        self._variable_responder = VariableResponder(
            lambda name, value: self._store_variable_value(name, value)
        )

        # info recorded in a cache
        # (this must be done after default values are set because it will automatically enable the module if possible)
        initial_info = {
            "speed": 1.0,
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

    def update(self):
        import time
        import math

        now = time.ticks_ms()
        delta_ms = time.ticks_diff(now, self._time)

        # update the time
        self._time = now

        # update the phase according to the speed
        self._phase += self.speed * delta_ms / 1000.0
        self._phase = math.fmod(self._phase, 1.0)

    @property
    def speed(self):
        return self._speed.value

    @speed.setter
    def speed(self, value):
        self._speed.value = value

    @property
    def time(self):
        self.update()
        return self._time

    @property
    def phase(self):
        self.update()
        return self._phase
