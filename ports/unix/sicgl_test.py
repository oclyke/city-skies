# set up output
import sicgl
WIDTH = 22
HEIGHT = 13
screen = sicgl.Screen((WIDTH, HEIGHT))
memory = sicgl.allocate_memory(screen)
interface = sicgl.Interface(screen, memory)

for h in range(HEIGHT):
  for w in range(WIDTH):
    interface.global_pixel(0xffffffff, (w, h))

s = sicgl.Screen((3, 3), (-2, 1))

