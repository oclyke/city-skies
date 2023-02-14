class VariableDeclaration:
    def __init__(self, type, default, name, description=None, responders=None):
        self._name = name
        self._type = type
        self._default = self.validate(default)
        self._value = self._default
        self._description = str(description)

        # using a new empty list is important to avoid a leak which
        # causes responders from any instance of a VariableDeclaration
        # to all be called for any change to any instance... this note
        # exists mostly to serve as a clue in case this behaviour is
        # observed again
        self._responders = []
        if responders is not None:
            for responder in responders:
                self.add_responder(responder)

    def validate(self, value):
        return self._type(value)

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
        self._value = self.validate(val)
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
