import bluetooth
from ble import (
    READ,
    WRITE,
    NOTIFY,
)

# advertising UUID
ADV_UUID_CITY_SKIES = bluetooth.UUID("3003c6ee-7765-478d-9d8d-29ddb98bd1fd")

# identity service
CHR_IDCFG_UNIQUE = (
    bluetooth.UUID("55c89d04-463b-4bba-8a21-ec145717c87c"),
    READ,
)
CHR_IDCFG_TAG = (
    bluetooth.UUID("d6a040e0-0c33-457e-abc8-1bda1f810485"),
    READ | WRITE | NOTIFY,
)
SVC_IDCFG = (
    bluetooth.UUID("8ab700eb-bcd3-4bfd-aa98-4823e8e70993"),
    (CHR_IDCFG_UNIQUE, CHR_IDCFG_TAG),
)

# network configuration service
CHR_NETCFG_STATE = (
    bluetooth.UUID("dc6e8ace-d2d0-4eb8-801c-4ce30046ee07"),
    READ | NOTIFY,
)
CHR_NETCFG_MODE = (
    bluetooth.UUID("39979325-326d-4d84-9ae0-2a04282cfa68"),
    READ | WRITE | NOTIFY,
)
CHR_NETCFG_ACTIVE = (
    bluetooth.UUID("d5175f24-cea4-4c08-98cd-f50b1ac3ab8d"),
    READ | WRITE | NOTIFY,
)

CHR_NETCFG_STA_SSID = (
    bluetooth.UUID("77e3d4a0-a31a-4fa1-b84b-84ce23f6600f"),
    READ | WRITE | NOTIFY,
)
CHR_NETCFG_STA_PASSWORD = (
    bluetooth.UUID("dbab9851-71f0-43ae-9af0-368d83d66434"),
    WRITE,
)
CHR_NETCFG_STA_IPADDR = (
    bluetooth.UUID("ebe3b007-6cab-4791-a3d9-24757b50a031"),
    READ | NOTIFY,
)

CHR_NETCFG_AP_SSID = (
    bluetooth.UUID("9362c588-cc81-47a0-989e-86529e7e1d8d"),
    READ | WRITE | NOTIFY,
)
CHR_NETCFG_AP_PASSWORD = (
    bluetooth.UUID("6ca4cc65-fbe8-479d-95fb-5f81a69ae221"),
    WRITE,
)
CHR_NETCFG_AP_IPADDR = (
    bluetooth.UUID("db5b2ad6-2afb-43c3-ba83-37e61a73e91f"),
    READ | NOTIFY,
)

SVC_NETCFG = (
    bluetooth.UUID("f286b5ca-6d19-4d84-96b1-a18a53056607"),
    (
        CHR_NETCFG_STATE,
        CHR_NETCFG_MODE,
        CHR_NETCFG_ACTIVE,
        CHR_NETCFG_STA_SSID,
        CHR_NETCFG_STA_PASSWORD,
        CHR_NETCFG_STA_IPADDR,
        CHR_NETCFG_AP_SSID,
        CHR_NETCFG_AP_PASSWORD,
        CHR_NETCFG_AP_IPADDR,
    ),
)
