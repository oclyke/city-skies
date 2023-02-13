import io
import os
import sys
import time
import pathutils


class LogManager:
    @staticmethod
    def logname_generator(base):
        id = 0
        path = f"{base}+{id}"
        try:
            os.stat(path)
            id += 1
        except:
            yield path

    def __init__(self, path):
        self._path = path

    def log_exception(self, e):
        base = f"{self._path}/exceptions/{time.ticks_ms()}"
        gen = LogManager.logname_generator(base)
        path = next(gen)
        pathutils.ensure_parent_dirs(path)

        errbuf = io.StringIO()
        sys.print_exception(e, errbuf)
        errbuf = errbuf.getvalue()

        print(errbuf)

        print("logging to path: ", path)

        with open(path, "w") as f:
            f.write(errbuf)
