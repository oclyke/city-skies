# include manifest from the micropython unix port
include("$(PORT_DIR)/variants/manifest.py")

# include uasyncio
include("$(MPY_DIR)/extmod/uasyncio/manifest.py")

# include manifest from city-skies common source
include("../../../../src/manifest.py")
