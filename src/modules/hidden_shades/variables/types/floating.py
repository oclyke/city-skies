from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_FLOATING


class FloatingVariable(VariableDeclaration):
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
        self.notify()

    def get_dict(self):
        base = super().get_dict()
        additional = {
            "type": TYPECODE_FLOATING,
            "default_range": self._default_range,
            "allowed_range": self._allowed_range,
        }
        return dict(**base, **additional)
