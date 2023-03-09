from semver import SemanticVersion
from udpdriver import UDPDriver
from artnetdriver import ArtnetDriver
from audio_stream_udp import UDPAudioSource
from audio_stream_udp_mic import UDPAudioSourceMic
from audio_mock import MockAudioSource
import config
import pysicgl

# hardware version
hw_version = SemanticVersion.from_semver("0.0.0-unix-dev")

# diplay hardware
drivers = [
    UDPDriver("0.0.0.0", (6969, 6420)),
    ArtnetDriver("192.168.4.177"),
]

# audio sources
audio_source_root_path = f"{config.EPHEMERAL_DIR}/audio/sources"
audio_sources = [
    UDPAudioSourceMic(audio_source_root_path, "MicStreamUDP", ("0.0.0.0", "42311"), (48000, 1024)),
    UDPAudioSource(
        audio_source_root_path, "AudioStreamUDP", ("0.0.0.0", "42310"), (44100, 1024)
    ),
    MockAudioSource(audio_source_root_path, "MockAudio", 400, (16000, 256)),
]
