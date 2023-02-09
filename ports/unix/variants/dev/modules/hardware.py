from semver import SemanticVersion
from udpdriver import UDPDriver
from artnetdriver import ArtnetDriver
import pysicgl

# hardware version
hw_version = SemanticVersion.from_semver("0.0.0-unix-dev")

# diplay hardware
drivers = [
    UDPDriver("0.0.0.0", (6969, 6420)),
    ArtnetDriver("192.168.4.177"),
]
