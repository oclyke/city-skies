# include manifest from the micropython esp32 port
include("$(PORT_DIR)/boards/manifest.py")

# include manifest from city-skies common source
include("../../../src/manifest.py")

# freeze city-skies esp32 port modules
freeze("../modules")
