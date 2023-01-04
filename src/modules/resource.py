class ResourceLocator:
    def __init__(self, name):
        self.set_name(name)

    def set_name(self, name):
        # name conditioning
        pairs = str(name).strip().split(" ", 1)
        try:
            self._name, _ = pairs
        except ValueError:
            self._name = pairs[0]

    @property
    def name(self):
        return self._name


class Resource(ResourceLocator):
    def __init__(self, name):
        super().__init__(name)
        self._variables = {}

    @property
    def variables(self):
        return self._variables

    def register_variable(self, variable):
        self._variables[variable.name] = variable
