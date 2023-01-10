class FreqCounter:
    def __init__(self, timebase, frequency):
        self._timebase = timebase
        self._freq = frequency
        self._basis = 0
        self._total = 0
        self._prev = 0

    def reset(self):
        self._basis = self._timebase.ticks_ms()
        self._total = 0
        self._prev = 0

    def update(self, speed=1):
        import time
        import math

        delta = time.ticks_diff(self._timebase.ticks_ms(), self._basis)
        transitions = math.floor(speed * self._freq * (delta / 1000.0))
        self._prev = self._total
        self._total = transitions

    def transitions(self):
        return self._total

    def accumulated(self):
        return self._total - self._prev
