set(USER_C_MODULES ${USER_C_MODULES}
  # city-skies c modules
  ${CMAKE_CURRENT_LIST_DIR}/../../../src/cmodules/sicgl/module.cmake
  ${CMAKE_CURRENT_LIST_DIR}/../../../src/cmodules/noise/module.cmake
  ${CMAKE_CURRENT_LIST_DIR}/../../../src/cmodules/ftt/module.cmake
  ${CMAKE_CURRENT_LIST_DIR}/../../../src/cmodules/buffer/module.cmake
  ${CMAKE_CURRENT_LIST_DIR}/../../../src/cmodules/reshape/module.cmake

  # esp32 c modules
  ${CMAKE_CURRENT_LIST_DIR}/../cmodules/ws2812b_utils/module.cmake
  ${CMAKE_CURRENT_LIST_DIR}/../cmodules/apa102_utils/module.cmake
  ${CMAKE_CURRENT_LIST_DIR}/../cmodules/ics43432_utils/module.cmake
  ${CMAKE_CURRENT_LIST_DIR}/../cmodules/seasnake/module.cmake
)
