from identity import IdentityInfo
from audio import AudioManager
from speed import SpeedManager
from shard import ShardManager
from palette import PaletteManager
from expression import ExpressionManager
from hardware import display
import sicgl

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
identity = IdentityInfo("runtime/identity")
palette_manager = PaletteManager("runtime/palette")
audio_manager = AudioManager("runtime/audio")
speed_manager = SpeedManager("runtime/speed")
shard_manager = ShardManager("runtime/shards")
expression_manager = ExpressionManager(
    "runtime/expressions", palette_manager, layer_interface
)
