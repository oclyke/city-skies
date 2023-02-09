class VariableResponder:
    def __init__(self, handler):
        self._handler = handler

    def handle(self, name, value):
        self._handler(name, value)
