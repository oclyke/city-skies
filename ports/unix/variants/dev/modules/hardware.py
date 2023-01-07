from semver import SemanticVersion
import sicgl

# hardware version
hw_version = SemanticVersion.from_semver("0.0.0-unix-dev")

# diplay hardware
WIDTH = 22
HEIGHT = 13
display = sicgl.Screen((WIDTH, HEIGHT))
