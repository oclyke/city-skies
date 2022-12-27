unique_key = "a specially loaded module"

# demonstrate that a module can import available modules
import time
import uasyncio as asyncio

print("its me!")
time.sleep(1)
print("still me after sleeping for a sec!")
