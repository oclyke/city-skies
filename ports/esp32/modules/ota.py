from micropython import const
import uhashlib as hashlib
import ubinascii as binascii
from esp32 import Partition

BLOCKLEN_DEFAULT = const(4096)  # data bytes in a flash block


class OTA:
    def __init__(self, blocklen=BLOCKLEN_DEFAULT):
        self._blocklen = blocklen
        self._block = 0  # current flash block to write to
        self._sha = hashlib.sha256()
        self._buf = bytearray(self._blocklen)
        self._watermark = 0  # number of bytes currently in the buffer
        self._processed = 0  # number of bytes handled in total
        self._wp = False  # flag to indicate write protection (used to avoid discontinuous memory writing)

    def _available(self):  # number of bytes needed to fill the buffer
        return self._blocklen - self._watermark

    def _write_buf(self):
        assert not self._wp  # ensure not write protected
        if self._available():
            self._wp = True  # do not allow writes after partial blocks
            for idx in range(
                self._available()
            ):  # fill any unused space with erased flash value 0xff
                self._buf[self._watermark + idx] = 0xFF
        self._writeblocks(
            self._block, self._buf
        )  # hook for implementations to handle this data
        self._block += 1  # increment block by one for next write
        self._processed += self._watermark  # increment processed by watermark level
        self._watermark = 0  # reset watermark because all buffer data was consumed

    def ingest(self, data):
        handled = 0
        remaining = len(data)
        self._sha.update(data)
        while remaining:
            if self._available() <= remaining:
                cpylen = self._available()
                self._buf[self._watermark : self._blocklen] = data[
                    handled : handled + cpylen
                ]
                self._watermark += cpylen
                self._write_buf()

            else:
                cpylen = remaining
                self._buf[self._watermark : self._watermark + cpylen] = data[
                    handled : handled + cpylen
                ]
                self._watermark += cpylen

            handled += cpylen
            remaining -= cpylen

    def finish(self, check_sha):
        if self._watermark:
            self._write_buf()  # write any remaining data

        del self._buf  # free up some memory
        calc_sha = binascii.hexlify(self._sha.digest())

        if calc_sha != check_sha:
            raise Exception("checksums do not match - abort")

        self._finish()  # hook for implementations to call finishing code


class ESP32OTA(OTA):
    def __init__(self):
        super().__init__()
        self._part = Partition(Partition.RUNNING).get_next_update()

    def _writeblocks(self, block, buffer):
        self._part.writeblocks(block, buffer)  # write entire buffer to the partition

    def _finish(self):
        self._part.set_boot()  # set the next boot partition


class OtaManager:
    def __init__(self):
        from cache import Cache

        initial_info = {
            "available": {
                "semver": None,
                "info": None,
            },
            "next": {
                "semver": None,
                "verified": False,
            },
        }
        self._info = Cache(f"{self._path}/info", initial_info)
