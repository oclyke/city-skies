MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(MOD_DIR)/src/module.c
SRC_USERMOD += $(MOD_DIR)/src/utilities.c
SRC_USERMOD += $(MOD_DIR)/src/screen.c

SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/color_sequence.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/interpolation.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/iter.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/screen.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/translate.c

# Add C flags for this module
CFLAGS_USERMOD += -I$(MOD_DIR)
CFLAGS_USERMOD += -I$(MOD_DIR)/include
CFLAGS_USERMOD += -I$(MOD_DIR)/third-party/sicgl/include

CFLAGS_USERMOD += -Wno-error=double-promotion
CFLAGS_USERMOD += -Wno-error=float-conversion
CFLAGS_USERMOD += -Wno-error=sign-compare
