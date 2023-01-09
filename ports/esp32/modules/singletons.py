from identity import IdentityInfo
from audio import AudioManager
from speed import SpeedManager
from shard import ShardManager
from expression import ExpressionManager
from board import display
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
identity = IdentityInfo(".cfg/identity")
audio_manager = AudioManager(".cfg/audio")
speed_manager = SpeedManager(".cfg/speed")
shard_manager = ShardManager(".cfg/shards")
expression_manager = ExpressionManager(".cfg/expressions", layer_interface)
