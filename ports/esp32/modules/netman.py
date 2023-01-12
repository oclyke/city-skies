class Interface:
    def __init__(self, path, wlan):
        from cache import Cache

        self._path = path
        self._wlan = wlan

        initial_info = {
            "ssid": "",
            "password": "",
        }
        self._info = Cache(self._path, initial_info)

        # a callback that child classes can use to respond to changes in info
        self._on_info_change = None

    def active(self, active=None):
        return self._wlan.active(active)

    def set_ssid(self, value):
        self._info.set("ssid", value)
        if self._on_info_change is not None:
            self._on_info_change()

    def set_password(self, value):
        self._info.set("password", value)
        if self._on_info_change is not None:
            self._on_info_change()

    @property
    def info(self):
        return self._info.cache

    @property
    def wlan(self):
        return self._wlan

    @property
    def ssid(self):
        return self._info.get("ssid")

    @property
    def password(self):
        return self._info.get("password")

    @property
    def ipaddr(self):
        return self._wlan.ifconfig()[0]


class ApInterface(Interface):
    def __init__(self, path):
        import network

        super().__init__(path, network.WLAN(network.AP_IF))
        self._on_info_change = lambda: self.config()
        self.config()

    def config(self):
        self._wlan.config(essid=self.ssid)
        self._wlan.config(password=self.password)


class StaInterface(Interface):
    def __init__(self, path):
        import network

        super().__init__(path, network.WLAN(network.STA_IF))
        self._on_info_change = lambda: self.reconnect()

    def reconnect(self):
        if self._wlan.active():
            self._wlan.disconnect()

        self._wlan.active(True)
        self._wlan.connect(self.ssid, self.password)


class NetworkManager:
    def __init__(self, path):
        from cache import Cache
        import network

        self._path = path

        initial_info = {
            "active": False,
            "mode": "STA",
        }
        self._info = Cache(f"{self._path}/info", initial_info)
        self._station = StaInterface(f"{self._path}/sta")
        self._access_point = ApInterface(f"{self._path}/ap")

        # activate the appropriate interface, if any
        if self.active:
            if self.mode == "AP":
                self._access_point.active(True)
            else:
                self._station.active(True)
                self._station.reconnect()

    def set_mode(self, mode):
        if not mode in ["AP", "STA"]:
            raise ValueError
        self._info.set("mode", mode)
        self._info.set("active", self.wlan.active())

    def set_active(self, active):
        self._info.set("active", active)
        self.wlan.active(self.active)
        if self.mode == "AP":
            self.access_point.config()
        else:
            self.station.reconnect()

    @property
    def station(self):
        return self._station

    @property
    def access_point(self):
        return self._access_point

    @property
    def active(self):
        return self._info.get("active")

    @property
    def mode(self):
        return self._info.get("mode")

    @property
    def wlan(self):
        return self._access_point.wlan if self.mode == "AP" else self._station.wlan

    @property
    def state(self):
        return {
            "info": self._info.cache,
            "station": self._station.info,
            "access_point": self._access_point.info,
        }
