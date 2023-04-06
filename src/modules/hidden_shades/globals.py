import pysicgl
from cache import Cache
from .variables.manager import VariableManager
from .variables.types import FloatingVariable, ColorSequenceVariable

DEFAULT_PALETTE = pysicgl.ColorSequence(
    map_type="continuous_circular",
    colors=[
        0x7FFF0000,
        0x7FFF5F00,
        0x7FFFBF00,
        0x7FDFFF00,
        0x7F7FFF00,
        0x7F1FFF00,
        0x7F00FF3F,
        0x7F00FF9F,
        0x7F00FFFF,
        0x7F009FFF,
        0x7F003FFF,
        0x7F1F00FF,
        0x7F7F00FF,
        0x7FDF00FF,
        0x7FFF00BF,
        0x7FFF005F,
    ],
)


class GlobalsManager:
    def __init__(self, path):
        # create root path
        self._root_path = path

        # a variable manager to expose variables
        self._variable_manager = VariableManager(f"{self._root_path}/vars")

        # these global variables are accessible in user space
        self._variable_manager.declare_variable(FloatingVariable("brightness", 1.0))
        self._variable_manager.declare_variable(
            ColorSequenceVariable("palette", DEFAULT_PALETTE)
        )
        self._variable_manager.initialize_variables()

    @property
    def variable_manager(self):
        return self._variable_manager
