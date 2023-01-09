import time


class ProfilingTimer:
    def set(self):
        self._t = time.ticks_us()

    def mark(self):
        self._delta = time.ticks_diff(time.ticks_us(), self._t)

    @property
    def period_us(self):
        return self._delta

    @property
    def period_ms(self):
        return self._delta / 1000


# @timed
def timed(f, *args, **kwargs):
    t = ProfilingTimer()
    name = str(f).split(" ")[1]

    def inner(*args, **kwargs):
        t.set()
        result = f(*args, **kwargs)
        t.mark()
        print(f"'{name}' took {t.period_us:9.3f}us")
        return result

    return inner
