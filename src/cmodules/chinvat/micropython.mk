MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(MOD_DIR)/src/module.c

SRC_USERMOD += $(MOD_DIR)/src/system/uuidv4.c
SRC_USERMOD += $(MOD_DIR)/src/system/version.c
SRC_USERMOD += $(MOD_DIR)/src/system/hardware.c
SRC_USERMOD += $(MOD_DIR)/src/system/firmware.c
SRC_USERMOD += $(MOD_DIR)/src/system/network.c
SRC_USERMOD += $(MOD_DIR)/src/system/identity.c
SRC_USERMOD += $(MOD_DIR)/src/system/system.c

SRC_USERMOD += $(MOD_DIR)/src/shard/atom.c
SRC_USERMOD += $(MOD_DIR)/src/shard/variable.c
SRC_USERMOD += $(MOD_DIR)/src/shard/variable/boolean.c
SRC_USERMOD += $(MOD_DIR)/src/shard/variable/double.c
SRC_USERMOD += $(MOD_DIR)/src/shard/variable/integer.c
SRC_USERMOD += $(MOD_DIR)/src/shard/variable/option.c

SRC_USERMOD += $(MOD_DIR)/third-party/chinvat/third-party/nanopb/pb_common.c
SRC_USERMOD += $(MOD_DIR)/third-party/chinvat/third-party/nanopb/pb_encode.c
SRC_USERMOD += $(MOD_DIR)/third-party/chinvat/third-party/nanopb/pb_decode.c

SRC_USERMOD += $(MOD_DIR)/third-party/chinvat/src/generated/shard.pb.c
SRC_USERMOD += $(MOD_DIR)/third-party/chinvat/src/generated/system.pb.c

# Add C flags for this module
CFLAGS_USERMOD += -I$(MOD_DIR)
CFLAGS_USERMOD += -I$(MOD_DIR)/include
CFLAGS_USERMOD += -I$(MOD_DIR)/third-party/chinvat/third-party/nanopb
CFLAGS_USERMOD += -I$(MOD_DIR)/third-party/chinvat/src/generated
