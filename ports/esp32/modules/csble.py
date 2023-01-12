import ble
import ble_services


class CSBLE(ble.BlePeripheral):
    def __init__(self):
        super().__init__("litt", (ble_services.SVC_IDCFG, ble_services.SVC_NETCFG))
        idcfg_handles, netcfg_handles = self.get_service_handles()

        (self._idcfg_unique_handle, self._idcfg_tag_handle) = idcfg_handles
        self._idcfg_handles = {
            "unique": self._idcfg_unique_handle,
            "tag": self._idcfg_tag_handle,
        }

        (
            self._netcfg_state_handle,
            self._netcfg_mode_handle,
            self._netcfg_active_handle,
            self._netcfg_sta_ssid_handle,
            self._netcfg_sta_password_handle,
            self._netcfg_sta_ipaddr_handle,
            self._netcfg_ap_ssid_handle,
            self._netcfg_ap_password_handle,
            self._netcfg_ap_ipaddr_handle,
        ) = netcfg_handles

        self._netcfg_handles = {
            "mode": self._netcfg_mode_handle,
            "active": self._netcfg_active_handle,
            "sta_ssid": self._netcfg_sta_ssid_handle,
            "sta_pass": self._netcfg_sta_password_handle,
            "sta_ipaddr": self._netcfg_sta_ipaddr_handle,
            "ap_ssid": self._netcfg_ap_ssid_handle,
            "ap_pass": self._netcfg_ap_password_handle,
            "ap_ipaddr": self._netcfg_ap_ipaddr_handle,
        }

    @property
    def idcfg_handles(self):
        return self._idcfg_handles

    @property
    def netcfg_handles(self):
        return self._netcfg_handles
