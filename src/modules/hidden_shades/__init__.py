import time
import pysicgl
from semver import SemanticVersion
from .timebase import TimeBase
from .audio.manager import AudioManager
from .palette import PaletteManager

version = SemanticVersion.from_semver("0.0.0")
timebase = TimeBase("runtime/timebase", time.ticks_ms)
audio = AudioManager("runtime/audio")
palette = PaletteManager("runtime/palette")
