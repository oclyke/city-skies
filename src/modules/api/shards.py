from microdot_asyncio import Microdot
import os
import config

shards_app = Microdot()


@shards_app.get("")
async def get_shards(request):
    return list(os.listdir(f"{config.PERSISTENT_DIR}/shards"))


# curl -H "Content-Type: text/plain" -X PUT http://localhost:1337/shards/<uuid> -d $'def frames(l):\n\twhile True:\n\t\tyield None\n\t\tprint("hello world")\n\n'
@shards_app.put("/<uuid>")
async def put_shard(request, uuid):
    # shards are immutable once published, therefore if the specified UUID
    # exists on the filesystem it does not need to be written again
    path = f"{config.PERSISTENT_DIR}/shards/{uuid}"
    try:
        os.stat(path)
    except:
        with open(path, "w") as f:
            f.write(request.body)
