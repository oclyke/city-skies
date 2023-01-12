from identity import IdentityInfo
from audio import AudioManager
from speed import SpeedManager
from shard import ShardManager
from palette import PaletteManager
from expression import ExpressionManager
from netman import NetworkManager
from csble import CSBLE
from board import display
import sicgl

# create the BLE peripheral
ble = CSBLE()

# memory for the composited output
memory = sicgl.allocate_memory(display)
canvas_interface = sicgl.Interface(display, memory)

# memory into which to place the gamma corrected output
gamma_memory = sicgl.allocate_memory(display)
gamma_interface = sicgl.Interface(display, gamma_memory)

# memory for intermediate layer action
layer_memory = sicgl.allocate_memory(display)
layer_interface = sicgl.Interface(display, layer_memory)

# data managers
identity = IdentityInfo(".cfg/identity")
palette_manager = PaletteManager(".cfg/palette")
audio_manager = AudioManager(".cfg/audio")
speed_manager = SpeedManager(".cfg/speed")
shard_manager = ShardManager(".cfg/shards")
network_manager = NetworkManager(".cfg/network")
expression_manager = ExpressionManager(
    ".cfg/expressions", palette_manager, layer_interface
)
