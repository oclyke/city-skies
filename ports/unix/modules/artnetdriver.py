MAX_BYTES_PER_UNIVERSE = 512

class ArtnetDriver:
    def __init__(self, host, port=6454, start_universe=0, physical_port=0):
        import socket

        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._start_universe = start_universe

        self._addr = socket.getaddrinfo(self._host, self._port)[0][-1]

        self._packet = bytearray(18 + 512)
        self._packet[0:8] = bytearray('Art-Net\0')
        self._packet[8:10] = (0x5000).to_bytes(2, 'little')
        self._packet[10:12] = bytearray([0, 14])
        self._packet[13] = physical_port

        self._sequence = 0
        self.advance_sequence()


    def advance_sequence(self):
        self._sequence += 1
        if self._sequence > 255:
            self._sequence = 1
        
        self._packet[12] = self._sequence

    def push(self, interface):
        bytes_remaining = len(interface.memory)
        offset = 0
        universes = (bytes_remaining // MAX_BYTES_PER_UNIVERSE) + 1

        for universe in range(universes):
            length = min(MAX_BYTES_PER_UNIVERSE, bytes_remaining)

            self._packet[14:] = (universe & 0x7ffff).to_bytes(2, 'little')
            self._packet[16:] = length.to_bytes(2, 'big')
            self._packet[18:] = interface.memory[offset:offset+length]


            self._sock.sendto(self._packet, self._addr)
            self.advance_sequence()
            offset += length
            bytes_remaining -= length
