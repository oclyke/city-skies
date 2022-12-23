# include common configuration
include(${CMAKE_CURRENT_LIST_DIR}/../common.cmake)

# configure board
set(SDKCONFIG_DEFAULTS
    ${MICROPY_PORT_DIR}/boards/sdkconfig.base
    ${MICROPY_PORT_DIR}/boards/sdkconfig.ble
    boards/sdkconfig.partitions.4MiB
)
if(NOT MICROPY_FROZEN_MANIFEST)
    set(MICROPY_FROZEN_MANIFEST ${CMAKE_CURRENT_LIST_DIR}/manifest.py)
endif()

# # include board-specific cmodules
# set(USER_C_MODULES ${USER_C_MODULES}
#     # ${CMAKE_CURRENT_LIST_DIR}/cmodules/board-cmodule/module.cmake
# )
