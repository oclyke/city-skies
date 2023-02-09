import pysicgl
from cache import Cache


class PaletteManager:
    def __init__(self, path):
        # create root path
        self._root_path = path

        # info recorded in a cache
        # (this must be done after default values are set because it will automatically enable the module if possible)
        initial_info = {
            "primary": [
                0xFF0000,
                0xFF5F00,
                0xFFBF00,
                0xDFFF00,
                0x7FFF00,
                0x1FFF00,
                0xFF3F,
                0xFF9F,
                0xFFFF,
                0x9FFF,
                0x3FFF,
                0x1F00FF,
                0x7F00FF,
                0xDF00FF,
                0xFF00BF,
                0xFF005F,
            ],
        }
        self._info = Cache(
            f"{self._root_path}/info",
            initial_info,
            lambda key, value: self._handle_info_change(key, value),
        )

    def _handle_info_change(self, key, value):
        if key == "primary":
            self._primary = pysicgl.ColorSequence(value)

    @property
    def primary(self):
        return self._primary
