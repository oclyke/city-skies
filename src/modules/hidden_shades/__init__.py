import time
import pysicgl
from semver import SemanticVersion
from .timebase import TimeBase
from .audio.manager import AudioManager
from .palette import PaletteManager
from .globals import GlobalsManager

import config

version = SemanticVersion.from_semver("0.0.0")
timebase = TimeBase(f"{config.EPHEMERAL_DIR}/timebase", time.ticks_ms)
audio = AudioManager(f"{config.EPHEMERAL_DIR}/audio")
palette = PaletteManager(f"{config.EPHEMERAL_DIR}/palette")
globals = GlobalsManager(f"{config.EPHEMERAL_DIR}/globals")
