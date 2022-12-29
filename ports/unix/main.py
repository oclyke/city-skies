import uasyncio as asyncio
from microdot_asyncio import Microdot, send_file, Request, Response

# set up output
import sicgl
WIDTH = 22
HEIGHT = 13
screen = sicgl.Screen((WIDTH, HEIGHT))
memory = sicgl.allocate_memory(screen)
interface = sicgl.Interface(screen, memory)

# set up server
PORT = 1337
app = Microdot()
Request.max_content_length = 128 * 1024  # 128 KB

# an endpoint to which the user can send module names
# curl -d 'demo_dynamic_module' -H "Content-Type: text/plain" -X POST http://localhost:1337/upload
@app.post("/upload")
async def upload(request):
    # decode the payload assuming utf-8
    name = request.body.decode()
    print("importing: ", name)

    # import that module
    module = __import__(name)


async def blink():
    import time

    while True:
        print("blink: ", time.ticks_ms(), "ms")
        await asyncio.sleep(10)


async def main():
    # create async tasks
    asyncio.create_task(app.start_server(debug=True, port=PORT))
    asyncio.create_task(blink())

    # the main task should not return so that asyncio continues to handle tasks
    while True:
        await asyncio.sleep(1)


# run asyncio scheduler
asyncio.run(main())
