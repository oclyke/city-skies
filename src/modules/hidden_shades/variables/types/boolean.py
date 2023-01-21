from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_BOOLEAN


class BooleanVariable(VariableDeclaration):
    def __init__(self, default, name, tags=("False", "True"), **kwargs):
        super().__init__(bool, default, name, **kwargs)
        self._tags = tuple(str(tag) for tag in tags)

    def get_dict(self):
        base = super().get_dict()
        additional = {
            "type": TYPECODE_BOOLEAN,
            "tags": self._tags,
        }
        return dict(**base, **additional)
