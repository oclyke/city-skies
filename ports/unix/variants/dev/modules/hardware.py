from semver import SemanticVersion
from udpdriver import UDPDriver
import sicgl

# hardware version
hw_version = SemanticVersion.from_semver("0.0.0-unix-dev")

# diplay hardware
WIDTH = 23
HEIGHT = 13
display = sicgl.Screen((WIDTH, HEIGHT))
driver = UDPDriver(display, "0.0.0.0", (6969, 6420))
