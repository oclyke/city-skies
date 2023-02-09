from cache import Cache
from .source import AudioSource


class AudioManager:
    def __init__(self, path):
        self._sources = {}
        self._selected = None

        self._root_path = path
        self._sources_path = f"{self._root_path}/sources"

        initial_info = {
            "selected": None,
        }
        self._info = Cache(
            f"{self._root_path}/info",
            initial_info,
            None,
        )

    @property
    def sources(self):
        return self._sources

    def add_source(self, *args, **kwargs):
        source = AudioSource(self, *args, **kwargs)
        self._sources[source.name] = source
        return source
