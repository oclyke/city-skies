# configured values
class IdentityInfo:
    def __init__(self, path):
        self._path = path
        self._tag = None

    @property
    def tag(self):
        if self._tag is None:
            try:
                with open(f"{self._path}/tag", "r") as f:
                    self._tag = str(f.read())
            except:
                self._tag = ""
        return self._tag

    @tag.setter
    def tag(self, value):
        with open(f"{self._path}/tag", "w") as f:
            f.write(str(value))
