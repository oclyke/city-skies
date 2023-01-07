class SpeedManager:
    def __init__(self, path):
        import time
        from cache import Cache
        from variables import VariableManager

        # store starting time
        self._time = time.ticks_ms()

        # store paths
        self._root_path = path
        self._vars_path = f"{self._root_path}/vars"

        # variables which may be dynamically registered for external control
        self._variable_responder = VariableManager(f"{self._root_path}/vars")

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
    def info(self):
        return self._info.cache

    @property
    def variables(self):
        return self._variable_manager.variables

    @property
    def time(self):
        self.update()
        return self._time

    @property
    def phase(self):
        self.update()
        return self._phase
