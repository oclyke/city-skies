class PaletteManager:
    def __init__(self, path):
        from variables import VariableManager
        from cache import Cache

        # create root path
        self._root_path = path

        # variables which may be dynamically registered for external control
        self._variables = {}
        self._variable_responder = VariableManager(f"{self._root_path}/vars")

        # info recorded in a cache
        # (this must be done after default values are set because it will automatically enable the module if possible)
        initial_info = {
            "palette": [
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
        pass

    @property
    def info(self):
        return self._info.cache

    @property
    def variables(self):
        return self._variables

    @property
    def palette(self):
        return self._info.get("palette")
