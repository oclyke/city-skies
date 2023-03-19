import pysicgl
from cache import Cache
from .variables.manager import VariableManager
from .variables.types import FloatingVariable, ColorSequenceVariable

DEFAULT_PALETTE = pysicgl.ColorSequence(
    map_type="continuous_circular",
    colors=[
        0xEFFF0000,
        0xEFFF5F00,
        0xEFFFBF00,
        0xEFDFFF00,
        0xEF7FFF00,
        0xEF1FFF00,
        0xEF00FF3F,
        0xEF00FF9F,
        0xEF00FFFF,
        0xEF009FFF,
        0xEF003FFF,
        0xEF1F00FF,
        0xEF7F00FF,
        0xEFDF00FF,
        0xEFFF00BF,
        0xEFFF005F,
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
