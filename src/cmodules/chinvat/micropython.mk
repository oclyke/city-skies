MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(MOD_DIR)/src/module.c

SRC_USERMOD += $(MOD_DIR)/src/system.c
SRC_USERMOD += $(MOD_DIR)/src/system/uuidv4.c
SRC_USERMOD += $(MOD_DIR)/src/system/version.c
SRC_USERMOD += $(MOD_DIR)/src/system/hardware.c
SRC_USERMOD += $(MOD_DIR)/src/system/firmware.c
SRC_USERMOD += $(MOD_DIR)/src/system/network.c
SRC_USERMOD += $(MOD_DIR)/src/system/system_info/identity.c
SRC_USERMOD += $(MOD_DIR)/src/system/system_info.c

SRC_USERMOD += $(MOD_DIR)/src/shard.c
SRC_USERMOD += $(MOD_DIR)/src/shard/atom.c

SRC_USERMOD += $(MOD_DIR)/src/resource.c
SRC_USERMOD += $(MOD_DIR)/src/resource/variable.c
SRC_USERMOD += $(MOD_DIR)/src/resource/variable/boolean.c
SRC_USERMOD += $(MOD_DIR)/src/resource/variable/double.c
SRC_USERMOD += $(MOD_DIR)/src/resource/variable/integer.c
SRC_USERMOD += $(MOD_DIR)/src/resource/variable/option.c

SRC_USERMOD += $(MOD_DIR)/third-party/chinvat/third-party/nanopb/pb_common.c
SRC_USERMOD += $(MOD_DIR)/third-party/chinvat/third-party/nanopb/pb_encode.c
SRC_USERMOD += $(MOD_DIR)/third-party/chinvat/third-party/nanopb/pb_decode.c

SRC_USERMOD += $(MOD_DIR)/third-party/chinvat/src/generated/resource.pb.c
SRC_USERMOD += $(MOD_DIR)/third-party/chinvat/src/generated/shard.pb.c
SRC_USERMOD += $(MOD_DIR)/third-party/chinvat/src/generated/system.pb.c

# Add C flags for this module
CFLAGS_USERMOD += -I$(MOD_DIR)
CFLAGS_USERMOD += -I$(MOD_DIR)/include
CFLAGS_USERMOD += -I$(MOD_DIR)/third-party/chinvat/third-party/nanopb
CFLAGS_USERMOD += -I$(MOD_DIR)/third-party/chinvat/src/generated
