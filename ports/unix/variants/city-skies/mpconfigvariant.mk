PROG ?= $(BUILD)/micropython-dev

FROZEN_MANIFEST ?= $(VARIANT_DIR)/manifest.py

# specify c modules
CITY_SKIES_ROOT = $(VARIANT_DIR)/../../../..
USER_C_MODULES = $(CITY_SKIES_ROOT)/src/cmodules
