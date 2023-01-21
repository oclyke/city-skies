import json
from pathutils import ensure_parent_dirs


class Cache:
    """
    Cache storage backed by filesystem.
    Nested dictionaries not allowed.
    """

    def __init__(self, path, initial_values={}, on_change=None):
        self._path = path
        self._on_change = on_change
        self._cache = initial_values

        # try to load existing file
        # if failed then make sure dirs exist for initial storage
        try:
            self.load()
        except OSError:
            ensure_parent_dirs(path)
            self.notify()

        # store initial values
        self.store()

    def notify(self, key=None):
        """
        Notify the registered change handler, if any, of the value of one or all keys in the cache.
        """
        if self._on_change is not None:
            if key is not None:
                self._on_change(key, self._cache[key])
            else:
                for key in self._cache.keys():
                    self._on_change(key, self._cache[key])

    def load(self):
        with open(self._path, "r") as f:
            self._cache = json.load(f)
        self.notify()

    def store(self):
        with open(self._path, "w") as f:
            json.dump(self._cache, f)

    def get(self, name):
        return self._cache[name]

    def set(self, key, value):
        self._cache[key] = value
        self.store()
        self.notify(key)

    @property
    def cache(self):
        return self._cache
