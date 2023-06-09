from microdot_asyncio import Microdot

stack_manager_app = Microdot()

def init_stack_manager_app(stack_manager):
    # change the active stack
    @stack_manager_app.get("/info")
    async def get_manager_info(request):
        return stack_manager.info

    # change the active stack
    @stack_manager_app.put("/switch")
    async def switch_stacks(request):
        stack_manager.switch()
