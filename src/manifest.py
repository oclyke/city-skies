# freeze("../../modules")
# freeze("modules")
# freeze("packages/pystorage/src")

# microdot web server
freeze(
    "packages/microdot/src",
    [
        "microdot.py",
        "microdot_websocket.py",
        "microdot_asyncio.py",
        "microdot_asyncio_websocket.py",
    ],
)
