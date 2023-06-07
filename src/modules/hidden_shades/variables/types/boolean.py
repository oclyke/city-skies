from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_BOOLEAN


class BooleanVariable(VariableDeclaration):
    def __init__(self, name, default, tags=("False", "True"), **kwargs):
        super().__init__(TYPECODE_BOOLEAN, bool, name, default, **kwargs)
        self._tags = tuple(str(tag) for tag in tags)

    def get_data(self):
        return {
            "tags": self._tags,
        }
