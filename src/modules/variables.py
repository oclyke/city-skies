class VariableResponder:
    def __init__(self, handler):
        self._handler = handler

    def handle(self, name, value):
        self._handler(name, value)


class VariableDeclaration:
    def __init__(self, type, default, name, description=None, responder=None):
        self._name = name
        self._type = type
        self._default = self._type(default)
        self._value = self._default
        self._description = str(description)
        self._responder = responder

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
        if self._responder is not None:
            self._responder.handle(self._name, self._value)

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


class BooleanVariable(VariableDeclaration):
    TYPECODE = 1

    def __init__(self, default, name, tags=("False", "True"), **kwargs):
        super().__init__(bool, default, name, **kwargs)
        self._tags = tuple(str(tag) for tag in tags)

    def get_dict(self):
        base = super().get_dict()
        additional = {
            "type": BooleanVariable.TYPECODE,
            "tags": self._tags,
        }
        return dict(**base, **additional)


class IntegerVariable(VariableDeclaration):
    TYPECODE = 2

    def __init__(
        self, default, name, default_range=(0, 100), allowed_range=None, **kwargs
    ):
        super().__init__(int, default, name, **kwargs)
        self._default_range = tuple(int(val) for val in default_range)
        self._allowed_range = (
            tuple(int(val) for val in allowed_range)
            if allowed_range is not None
            else None
        )

    @VariableDeclaration.value.setter
    def value(self, value):
        v = self._type(value)
        if self._allowed_range is not None:
            if not v in range(*self._allowed_range):
                raise ValueError
        self._value = v

    def get_dict(self):
        base = super().get_dict()
        additional = {
            "type": IntegerVariable.TYPECODE,
            "default_range": self._default_range,
            "allowed_range": self._allowed_range,
        }
        return dict(**base, **additional)


class DoubleVariable(VariableDeclaration):
    TYPECODE = 3

    def __init__(
        self, default, name, default_range=(0, 1), allowed_range=None, **kwargs
    ):
        super().__init__(float, default, name, **kwargs)
        self._default_range = tuple(float(val) for val in default_range)
        self._allowed_range = (
            tuple(float(val) for val in allowed_range)
            if allowed_range is not None
            else None
        )

    @VariableDeclaration.value.setter
    def value(self, value):
        v = self._type(value)
        if self._allowed_range is not None:
            if not v in range(*self._allowed_range):
                raise ValueError
        self._value = v

    def get_dict(self):
        base = super().get_dict()
        additional = {
            "type": DoubleVariable.TYPECODE,
            "default_range": self._default_range,
            "allowed_range": self._allowed_range,
        }
        return dict(**base, **additional)


class OptionVariable(VariableDeclaration):
    TYPECODE = 4

    def __init__(self, default, name, options, **kwargs):
        super().__init__(int, default, name, **kwargs)
        self._options = tuple(str(val) for val in options)

    @VariableDeclaration.value.setter
    def value(self, value):
        v = self._type(value)
        if not v in range(len(self._options)):
            raise ValueError
        self._value = v

    def get_dict(self):
        base = super().get_dict()
        additional = {
            "type": OptionVariable.TYPECODE,
            "options": self._options,
        }
        return dict(**base, **additional)
