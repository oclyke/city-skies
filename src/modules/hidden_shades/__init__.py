import time
import pysicgl
from semver import SemanticVersion
from .timebase import TimeBase
from .audio.manager import AudioManager
from .globals import GlobalsManager
from .artnet import ArtnetProvider

import config

version = SemanticVersion.from_semver("0.0.0")
timebase = TimeBase(f"{config.EPHEMERAL_DIR}/timebase", time.ticks_ms)
audio_manager = AudioManager(f"{config.EPHEMERAL_DIR}/audio")
globals = GlobalsManager(f"{config.EPHEMERAL_DIR}/globals")
artnet_provider = ArtnetProvider(f"{config.EPHEMERAL_DIR}/artnet")
