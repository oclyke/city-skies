from pathutils import ensure_dirs
from .responder import VariableResponder


class VariableManager(VariableResponder):
    def __init__(self, path):
        super().__init__(lambda name, value: self._handle_variable_change(name, value))
        self._path = path
        self._variables = {}

        # ensure filesystem storage exists
        ensure_dirs(self._path)

    def _handle_variable_change(self, name, value):
        self._store_variable_value(name, value)

    def _store_variable_value(self, name, value):
        with open(f"{self._path}/{name}", "w") as f:
            f.write(str(value))

    def _load_variable_value(self, name):
        with open(f"{self._path}/{name}", "r") as f:
            return str(f.read())

    def declare_variable(self, variable):
        """
        This method allows automatic association of a declared variable
        to this object so that it may be properly cached.
        """
        self._variables[variable.name] = variable  # register it into the list
        variable.add_responder(self)  # register self as a responder

        # try loading an existing value for the registered variable
        try:
            variable.value = self._load_variable_value(variable.name)
        except:
            pass

        # finally store the current value
        self._store_variable_value(variable.name, variable.value)
        variable.notify()

        return variable

    @property
    def variables(self):
        return self._variables
