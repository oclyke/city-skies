MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(MOD_DIR)/src/module.c
SRC_USERMOD += $(MOD_DIR)/src/utilities.c
SRC_USERMOD += $(MOD_DIR)/src/buffer/float.c

# Add C flags for this module
CFLAGS_USERMOD += -I$(MOD_DIR)
CFLAGS_USERMOD += -I$(MOD_DIR)/include
