import io
import os
import sys
import time


def logname_generator(base):
    id = 0
    path = f"{base}+{id}"
    try:
        os.stat(path)
        id += 1
    except:
        yield path


def log_exception(e):
    base = f"runtime/logs/{time.ticks_ms()}"
    gen = logname_generator(base)
    path = next(gen)

    errbuf = io.StringIO()
    sys.print_exception(e, errbuf)
    errbuf = errbuf.getvalue()

    print("logging to path: ", path)

    with open(path, "w") as f:
        f.write(errbuf)
