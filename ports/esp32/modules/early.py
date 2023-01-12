import expression
import palette
import board
import sicgl

# memory for the composited output
memory = sicgl.allocate_memory(board.display)
canvas_interface = sicgl.Interface(board.display, memory)

# memory into which to place the gamma corrected output
gamma_memory = sicgl.allocate_memory(board.display)
gamma_interface = sicgl.Interface(board.display, gamma_memory)

# memory for intermediate layer action
layer_memory = sicgl.allocate_memory(board.display)
layer_interface = sicgl.Interface(board.display, layer_memory)

# palette and expression manager
palette_manager = palette.PaletteManager(".cfg/palette")
expression_manager = expression.ExpressionManager(
    ".cfg/expressions", palette_manager, layer_interface
)
