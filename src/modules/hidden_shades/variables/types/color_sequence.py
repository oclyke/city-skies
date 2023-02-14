from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_COLOR_SEQUENCE


class ColorSequenceVariable(VariableDeclaration):
    def __init__(self, default, name, **kwargs):
        super().__init__(tuple, default, name, **kwargs)

    def validate(self, value):
        return tuple(int(element) for element in value)

    def get_dict(self):
        base = super().get_dict()
        additional = {
            "type": TYPECODE_COLOR_SEQUENCE,
        }
        return dict(**base, **additional)
