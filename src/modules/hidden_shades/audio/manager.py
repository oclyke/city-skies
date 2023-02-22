from cache import Cache
from .source import AudioSource


NULL_AUDIO_SOURCE = AudioSource((16000, 1))


class AudioManager:
    def __init__(self, path):
        self._sources = {}
        self._selected = NULL_AUDIO_SOURCE

        self._root_path = path
        self._sources_path = f"{self._root_path}/sources"

        initial_info = {
            "selected": None,
        }
        self._info = Cache(
            f"{self._root_path}/info",
            initial_info,
            # the change handler is intentionally left out during construction
            # to prevent the selected audio source from being accessed before
            # it has been registered.
            # once all audio sources have been registered with the manager call
            # the .initialize() method to respond to info cache values.
            None,
        )

    def _handle_info_change(self, key, value):
        if key == "selected":
            if value == None:
                self._selected = NULL_AUDIO_SOURCE
            else:
                self._selected = self._sources[value]

    def initialize(self):
        """
        this method should be called after all audio sources hae been registered into the audio manager.
        it will load info from the cache and select the proper audio source.
        this cannot be done before the selected source has been registered with the manager.
        in cases where sources may be registered from a number of sources there will have to be some
        external method of synchronization that prevents initialization from ocurring too early (perhaps
        some kind of mutex)
        """
        self._info.set_change_handler(lambda key, value: self._handle_info_change(key, value))
        self._info.notify()

    def add_source(self, source):
        self._sources[source.name] = source

    def select_source(self, name):
        self._info.set("selected", name)

    @property
    def audio_source(self):
        return self._selected
