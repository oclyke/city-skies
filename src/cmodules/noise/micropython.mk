MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(MOD_DIR)/src/module.c
SRC_USERMOD += $(MOD_DIR)/src/open-simplex-noise.c
SRC_USERMOD += $(MOD_DIR)/third-party/open-simplex-noise-in-c/open-simplex-noise.c

# Add C flags for this module
CFLAGS_USERMOD += -I$(MOD_DIR)/include
CFLAGS_USERMOD += -I$(MOD_DIR)/third-party/open-simplex-noise-in-c
