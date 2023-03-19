MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(MOD_DIR)/src/module.c

SRC_USERMOD += $(MOD_DIR)/src/utilities.c
SRC_USERMOD += $(MOD_DIR)/src/screen.c
SRC_USERMOD += $(MOD_DIR)/src/field.c
SRC_USERMOD += $(MOD_DIR)/src/interface.c
SRC_USERMOD += $(MOD_DIR)/src/color_sequence.c
SRC_USERMOD += $(MOD_DIR)/src/drawing/blend.c
SRC_USERMOD += $(MOD_DIR)/src/drawing/compose.c
SRC_USERMOD += $(MOD_DIR)/src/drawing/global.c
SRC_USERMOD += $(MOD_DIR)/src/drawing/screen.c
SRC_USERMOD += $(MOD_DIR)/src/drawing/interface.c
SRC_USERMOD += $(MOD_DIR)/src/drawing/blit.c
SRC_USERMOD += $(MOD_DIR)/src/drawing/field.c

# sicgl sources
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/blend.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/blenders.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/blit.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/color_sequence.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/compose.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/compositors/alpha.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/compositors/bitwise.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/compositors/channelwise.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/compositors/direct.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/compositors/simple_alpha.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/field.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/gamma.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/iter.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/screen.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/translate.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/unity_color.c

SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/domain/global.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/domain/interface.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/domain/screen.c

SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/private/interpolation.c
SRC_USERMOD += $(MOD_DIR)/third-party/sicgl/src/private/direct.c

# Add C flags for this module
CFLAGS_USERMOD += -I$(MOD_DIR)
CFLAGS_USERMOD += -I$(MOD_DIR)/include
CFLAGS_USERMOD += -I$(MOD_DIR)/third-party/sicgl/include

CFLAGS_USERMOD += -Wno-error=unused-function
CFLAGS_USERMOD += -Wno-error=unused-label
CFLAGS_USERMOD += -Wno-error=double-promotion
CFLAGS_USERMOD += -Wno-error=float-conversion
CFLAGS_USERMOD += -Wno-error=sign-compare

CFLAGS_USERMOD += -DSICGL_DEBUG_PRINTF
