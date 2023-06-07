from ..declaration import VariableDeclaration
from .typecodes import TYPECODE_COLOR_SEQUENCE
import pysicgl
import json


class ColorSequenceVariable(VariableDeclaration):
    def __init__(self, name, default, **kwargs):
        super().__init__(TYPECODE_COLOR_SEQUENCE, pysicgl.ColorSequence, name, default, **kwargs)

    def serialize(self, value):
        return json.dumps({"colors": value.colors, "map_type": value.map_type})

    def deserialize(self, ser_value):
        data = json.loads(ser_value)
        return pysicgl.ColorSequence(colors=data["colors"], map_type=data["map_type"])
