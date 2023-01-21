class VariableDeclaration:
    def __init__(self, type, default, name, description=None, responders=[]):
        self._name = name
        self._type = type
        self._default = self._type(default)
        self._value = self._default
        self._description = str(description)

        # it is very important to use 'list()' to generate a new
        # object here - otherwise there is a leak and subsequent
        # declarations end up duplicating respnders
        self._responders = list(responders)

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def default(self):
        return self._default

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = self._type(val)
        self.notify()

    def add_responder(self, responder):
        self._responders.append(responder)

    def notify(self):
        for responder in self._responders:
            responder.handle(self._name, self._value)

    def get_dict(self):
        return {
            "type": None,
            "name": self._name,
            "description": self._description,
            "default": self._default,
            "value": self._value,
        }

    def serialize(self, f=None):
        import json

        if f is None:
            return json.dumps(self.get_dict())
        else:
            json.dump(self.get_dict(), f)
