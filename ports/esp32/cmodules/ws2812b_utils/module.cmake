add_library(ws2812b_utils INTERFACE)

target_sources(ws2812b_utils INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/src/module.c
)

target_include_directories(ws2812b_utils INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/include
)

target_link_libraries(usermod INTERFACE ws2812b_utils)
