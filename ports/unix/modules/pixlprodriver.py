from artnet import ArtDMXPacket
import socket
import transform

MAX_BYTES_PER_UNIVERSE = 512


class PixlProArtnetDriver:
    def __init__(self, display, host, port=6454, start_universe=0, physical_port=0):
        self._packet = ArtDMXPacket(physical_port)

        self._disabled = False

        # configure socket
        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._addr = socket.getaddrinfo(self._host, self._port)[0][-1]

        # configure output
        self._start_universe = start_universe
        self._sequence = 0
        self.advance_sequence()

        # create a buffer for pixels
        self._buffer = bytearray(display.pixels * 3)

    def advance_sequence(self):
        self._sequence += 1
        if self._sequence > 255:
            self._sequence = 1
        self._packet.sequence = self._sequence

    def push(self, interface):
        # the interface is already laid out in the right shape by seasnake
        # now reduce the data down to 3 bytes per pixel
        transform.stride_copy(interface.memory, self._buffer, 4, 3)

        if not self._disabled:
            bytes_remaining = len(self._buffer)
            offset = 0
            universes = (bytes_remaining // MAX_BYTES_PER_UNIVERSE) + 1

            for universe in range(universes):
                length = min(MAX_BYTES_PER_UNIVERSE, bytes_remaining)
                self._packet.universe = universe
                self._packet.data = self._buffer[offset : offset + length]
                self._packet.length = length

                try:
                    self._sock.sendto(self._packet.buffer, self._addr)
                except:
                    print("ERROR sending ArtNet packet")
                    self._disabled = True

                self.advance_sequence()
                offset += length
                bytes_remaining -= length
