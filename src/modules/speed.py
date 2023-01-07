import time
import math
from resource import Resource


class SpeedManager(Resource):
    def __init__(self, name):
        super().__init__(name)
        from variables import DoubleVariable

        self._speed = DoubleVariable(
            1.0, "PrimarySpeed", (0.05, 5.0), description="Control the primary speed."
        )
        self.register_variable(self._speed)

        self._time = time.ticks_ms()
        self._phase = 0

    def update(self):
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
