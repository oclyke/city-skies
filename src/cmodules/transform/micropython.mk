MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(MOD_DIR)/src/module.c

# Add C flags for this module
CFLAGS_USERMOD += -I$(MOD_DIR)
