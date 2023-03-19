from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_OPTION


class OptionVariable(VariableDeclaration):
    def __init__(self, name, default, options, **kwargs):
        self._options = tuple(str(val) for val in options)
        super().__init__(str, name, default, **kwargs)

    def validate(self, value):
        return value in self._options

    def get_dict(self):
        base = super().get_dict()
        additional = {
            "type": TYPECODE_OPTION,
            "options": self._options,
            "index": self._options[self._value],
        }
        return dict(**base, **additional)
