import pysicgl
import seasnake


class SimpleSnakeArrangement:
    def __init__(self, screen, reverse_first=False):
        # the screen is used to inform the width of snake rows
        self._screen = screen

        # a simple snake arrangement assumes that the screen memory is
        # fully utilized and that every other screen row is reversed.
        self._memory = pysicgl.allocate_pixel_memory(self._screen.pixels)

        self._reverse_first = reverse_first

    def map(self, memory):
        """
        Map a standard pysicgl interface into the memory according to snake rules.
        """
        seasnake.map_simple(
            memory, self._memory, self._screen.width, self._reverse_first
        )

    @property
    def memory(self):
        return self._memory


class SnakeDriver:
    def __init__(self, screen, output):
        # this arrangement is used to remap the pysicgl interface to
        # match hardware output arrangements
        self._arrangement = SimpleSnakeArrangement(screen, False)

        # an output supports ingest and push methods to respectively
        # prepare and transmit buffer information
        self._output = output

    def ingest(self, interface):
        """ """
        # first, remap the interface according to the hardware output arrangement
        self._arrangement.map(interface.memory)

        # then ingest the mapped memory into the output driver
        self._output.ingest(self._arrangement.memory)

    def push(self):
        self._output.push()
