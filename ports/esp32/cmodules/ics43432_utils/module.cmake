add_library(ics43432_utils INTERFACE)

target_sources(ics43432_utils INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/src/module.c
)

target_include_directories(ics43432_utils INTERFACE
  # include the float buffer sources
  ${CMAKE_CURRENT_LIST_DIR}/../../../../src/cmodules/buffer/include
)

target_link_libraries(usermod INTERFACE ics43432_utils)
