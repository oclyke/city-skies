class SpeedManager:
    def __init__(self, path):
        import time
        from cache import Cache
        from variables import VariableManager

        # store starting time
        self._last_time = time.ticks_ms()

        # store variables pertaining to managed time
        self._managed_ticks_ms = 0
        self._managed_phase = 0

        # store paths
        self._root_path = path
        self._vars_path = f"{self._root_path}/vars"

        # variables which may be dynamically registered for external control
        self._variable_responder = VariableManager(f"{self._root_path}/vars")

        # info recorded in a cache
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

        # update the time
        now = time.ticks_ms()
        delta_ms = time.ticks_diff(now, self._last_time)
        self._last_time += delta_ms

        # update the managed time
        advance_ms = self._info.get("speed") * delta_ms
        self._managed_ticks_ms += advance_ms

        # update the phase according to the speed
        self._managed_phase += advance_ms / 1000.0
        self._managed_phase = math.fmod(self._managed_phase, 1.0)

    def ticks_ms(self):
        self.update()
        return self._managed_ticks_ms

    def phase(self):
        self.update()
        return self._managed_phase

    @property
    def info(self):
        return self._info.cache

    @property
    def variables(self):
        return self._variable_manager.variables
