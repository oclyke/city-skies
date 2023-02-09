import bluetooth
import struct
from micropython import const

MAX_NAME_LEN_DEFAULT = const(9)
MAX_ATTR_LEN_DEFAULT = const(512)

# flags
READ = const(0x0002)
WRITE_NO_RESPONSE = const(0x0004)
WRITE = const(0x0008)
NOTIFY = const(0x0010)

# irq flags
CENTRAL_CONNECT = const(1)
CENTRAL_DISCONNECT = const(2)
GATTS_WRITE = const(3)

# advertising fields
TYPE_FLAGS = const(0x01)
TYPE_NAME = const(0x09)
TYPE_UUID16_COMPLETE = const(0x3)
TYPE_UUID32_COMPLETE = const(0x5)
TYPE_UUID128_COMPLETE = const(0x7)
TYPE_UUID16_MORE = const(0x2)
TYPE_UUID32_MORE = const(0x4)
TYPE_UUID128_MORE = const(0x6)
TYPE_APPEARANCE = const(0x19)


# Generate a payload to be passed to gap_advertise(adv_data=...).
def advertising_payload(
    limited_disc=False, br_edr=False, name=None, services=None, appearance=0
):
    payload = bytearray()

    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack("BB", len(value) + 1, adv_type) + value

    _append(
        TYPE_FLAGS,
        struct.pack("B", (0x01 if limited_disc else 0x02) + (0x18 if br_edr else 0x04)),
    )

    if name:
        _append(TYPE_NAME, name)

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(TYPE_UUID128_COMPLETE, b)

    # See org.bluetooth.characteristic.gap.appearance.xml
    if appearance:
        _append(TYPE_APPEARANCE, struct.pack("<h", appearance))

    return payload


# bluetooth peripheral class
class BlePeripheral:
    def __init__(
        self,
        name,
        services,
        max_name_len=MAX_NAME_LEN_DEFAULT,
        max_attr_len=MAX_ATTR_LEN_DEFAULT,
    ):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.config(mtu=max_attr_len)
        self._ble.config(rxbuf=max_attr_len)
        self._ble.irq(self._irq)

        self._name_max_len = max_name_len

        self._adv_uuids = None
        self._connections = set()
        self._service_handles = self._ble.gatts_register_services(services)

        # write handlers are tuples of the attribute handle
        # and a function that is called with the new value
        # (attr_handle, handler)
        self._write_handlers = []

        self.set_name(name)

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)

        elif event == CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            self.advertise()

        elif event == GATTS_WRITE:
            # # update the value of the corresponding value
            # conn_handle, value_handle = data
            # for service_handles in self._service_handles:
            #     for handle in service_handles:
            #         if handle == value_handle:

            # call any write handlers which match this attribute
            conn_handle, attr_handle = data
            for handle, handler in self._write_handlers:
                if handle == attr_handle:
                    handler(self._ble.gatts_read(handle))

    def set_name(self, name):
        self._name = bytearray(name)[0 : self._name_max_len - 1]

    def advertise(self, adv_uuids=None, interval_us=500000):
        if adv_uuids is not None:
            self._adv_uuids = adv_uuids

        self._ble.gap_advertise(
            interval_us,
            adv_data=advertising_payload(
                name=self._name,
                services=self._adv_uuids,
            ),
        )

    def add_write_handler(self, attr_handle, handler):
        """
        Allows the user to register a handler that is called when the value
        of a particular attribute is changed by a central device.
        """
        self._write_handlers.append(tuple((attr_handle, handler)))

    def remove_write_handler(self, attr_handle, handler):
        """
        Allows the user to un-register a handler.
        The atribute handle and the handler must be identically the same as
        those which were originally registered.
        """
        self._write_handlers = list(
            filter(
                (
                    lambda item: item[0] is attr_handle and item[1] is handler,
                    self._write_handlers,
                )
            )
        )

    def get_service_handles(self):
        """
        Returns service handles as registered with the gatt server during initialization.
        Each returned item is a tuple of attribute handles.
        """
        return self._service_handles

    def write(self, attr_handle, value):
        """
        Set the value of an attribute.
        This value is subsequently readable by a connected central device.
        """
        self._ble.gatts_write(attr_handle, value)

    def notify(self, attr_handle):
        """
        Notify the value of an attribute.
        The value of this attribute is immediately sent to all connected central devices.
        The attribute must have the NOTIFY flag.
        """
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, attr_handle)
