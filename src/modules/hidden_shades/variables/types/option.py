from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_OPTION


class OptionVariable(VariableDeclaration):
    def __init__(self, default, name, options, **kwargs):
        super().__init__(int, default, name, **kwargs)
        self._options = tuple(str(val) for val in options)

    @VariableDeclaration.value.setter
    def value(self, value):
        v = self._type(value)
        if not v in range(len(self._options)):
            raise ValueError
        self._value = v
        self.notify()

    def get_dict(self):
        base = super().get_dict()
        additional = {
            "type": TYPECODE_OPTION,
            "options": self._options,
        }
        return dict(**base, **additional)