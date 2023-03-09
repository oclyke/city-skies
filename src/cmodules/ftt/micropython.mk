MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(MOD_DIR)/src/module.c
SRC_USERMOD += $(MOD_DIR)/src/buffer.c
SRC_USERMOD += $(MOD_DIR)/src/plan.c
SRC_USERMOD += $(MOD_DIR)/src/utilities.c
SRC_USERMOD += $(MOD_DIR)/third-party/fakufaku/components/fft/fft.c

# Add C flags for this module
CFLAGS_USERMOD += -I$(MOD_DIR)
CFLAGS_USERMOD += -I$(MOD_DIR)/include
CFLAGS_USERMOD += -I$(MOD_DIR)/third-party/fakufaku/components/fft/include
