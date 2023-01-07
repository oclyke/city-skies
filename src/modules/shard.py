import os


class ShardManager:
    def __init__(self, path):
        self._path = path

        # ensure that the desired path exists
        try:
            os.listdir(self._path)
        except:
            os.mkdir(self._path)

    @property
    def shards(self):
        available = os.listdir(f"{self._path}")
        return available

    def store_shard(self, uuid, source):
        # shards are uniquely identified by their uuid
        with open(f"{self._path}/{uuid}.py", "w") as f:
            f.write(source)

    def get_shard_module(self, uuid):
        module = __import__(f"{self._path}/{uuid}")
        return module
