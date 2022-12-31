# set up output
import sicgl

WIDTH = 22
HEIGHT = 13
screen = sicgl.Screen((WIDTH, HEIGHT))
memory = sicgl.allocate_memory(screen)
interface = sicgl.Interface(screen, memory)

for h in range(HEIGHT):
    for w in range(WIDTH):
        interface.global_pixel(0xFFFFFFFF, (w, h))

colors = [420, 69, 1111]
s = sicgl.Screen((3, 3), (-2, 1))
sf = sicgl.ScalarField(bytearray(13))
cs = sicgl.ColorSequence(colors)
