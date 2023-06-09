from microdot_asyncio import Microdot
from semver import SemanticVersion

from .shards import shards_app
from .stacks import stacks_app, init_stacks_app
from .stack_manager import stack_manager_app, init_stack_manager_app
from .globals import globals_app
from .audio import audio_app

api_version = SemanticVersion.from_semver("0.0.0")

api_app = Microdot()

def init_api_app(stack_manager, canvas, layer_post_init_hook):
        
    # a sorta ugly way to pass local data into the stacks app...
    init_stacks_app(stack_manager, canvas, layer_post_init_hook)
    init_stack_manager_app(stack_manager)

    api_app.mount(shards_app, url_prefix="/shards")
    api_app.mount(stacks_app, url_prefix="/stacks")
    api_app.mount(stack_manager_app, url_prefix="/stack_manager")
    api_app.mount(globals_app, url_prefix="/global")
    api_app.mount(audio_app, url_prefix="/audio")
