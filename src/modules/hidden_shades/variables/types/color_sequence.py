from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_COLOR_SEQUENCE


class ColorSequenceVariable(VariableDeclaration):
    def __init__(self, default, name, **kwargs):
        super().__init__(tuple, default, name, **kwargs)

    @VariableDeclaration.value.setter
    def value(self, value):
        self._value = tuple(int(element) for element in value)
        self.notify()

    def get_dict(self):
        base = super().get_dict()
        additional = {
            "type": TYPECODE_COLOR_SEQUENCE,
        }
        return dict(**base, **additional)
