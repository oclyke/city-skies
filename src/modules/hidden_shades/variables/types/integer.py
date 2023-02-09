from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_INTEGER


class IntegerVariable(VariableDeclaration):
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
        self.notify()

    def get_dict(self):
        base = super().get_dict()
        additional = {
            "type": TYPECODE_INTEGER,
            "default_range": self._default_range,
            "allowed_range": self._allowed_range,
        }
        return dict(**base, **additional)
