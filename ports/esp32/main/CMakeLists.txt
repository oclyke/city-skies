# Set location of base MicroPython directory.
if(NOT MICROPY_DIR)
    get_filename_component(MICROPY_DIR ${PROJECT_DIR}/../../third-party/micropython ABSOLUTE)
endif()

# override PROJECT_DIR for included MicroPython CMake files
get_filename_component(PROJECT_DIR ${MICROPY_DIR}/ports/esp32 ABSOLUTE)

# rely on existing MicroPython CMake main component
include(${MICROPY_DIR}/ports/esp32/main/CMakeLists.txt)
