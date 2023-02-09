import pysicgl
from cache import Cache
from .variables.manager import VariableManager
from .variables.types import FloatingVariable


class GlobalsManager:
    def __init__(self, path):
        # create root path
        self._root_path = path

        # a variable manager to expose variables
        self._variable_manager = VariableManager(f"{self._root_path}/vars")

        # these global variables are accessible in user space
        self._variable_manager.declare_variable(FloatingVariable(1.0, "brightness"))

    @property
    def variables(self):
        return self._variable_manager.variables
