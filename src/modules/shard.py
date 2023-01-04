import os
import json


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

    def store_shard(self, name, info, source):
        dirname = f"{self._path}/{name}"
        try:
            os.rmdir(dirname)
        except OSError:
            pass
        os.mkdir(dirname)

        # store info
        with open(f"{dirname}/info.json", "w") as f:
            json.dump(info, f)

        # store source
        with open(f"{dirname}/shard.py", "w") as f:
            f.write(source)

    def get_shard_module(self, name):
        module = __import__(f"{self._path}/{name}/shard")
        return module

    def get_shard_info(self, name):
        with open(f"{self._path}/{name}/info.json", "r") as f:
            info = json.load(f)
        return info
