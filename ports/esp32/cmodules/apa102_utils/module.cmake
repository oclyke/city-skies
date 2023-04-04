add_library(apa102_utils INTERFACE)

target_sources(apa102_utils INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/src/module.c
)

target_include_directories(apa102_utils INTERFACE
  # ${CMAKE_CURRENT_LIST_DIR}/include
)

target_link_libraries(usermod INTERFACE apa102_utils)
