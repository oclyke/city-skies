class UDPDriver:
    def __init__(self, screen, host="0.0.0.0", ports=(6969, 6420)):
        import socket

        self._screen = screen
        self._config = self._screen.width.to_bytes(
            2, "little"
        ) + self._screen.height.to_bytes(2, "little")

        self._host = host
        self._port_control, self._port_data = ports
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._addr_control = socket.getaddrinfo(self._host, self._port_control)[0][-1]
        self._addr_data = socket.getaddrinfo(self._host, self._port_data)[0][-1]

    def push(self, interface):
        # self._sock.sendto(self._config, self._addr_control)
        self._sock.sendto(interface.memory, self._addr_data)
