class Resource:
    def __init__(self):
        self._variables = {}

    @property
    def variables(self):
        return self._variables

    def register_variable(self, variable):
        self._variables[variable.name] = variable
