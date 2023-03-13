add_library(fft INTERFACE)

target_sources(fft INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/src/module.c
  ${CMAKE_CURRENT_LIST_DIR}/src/plan.c
  ${CMAKE_CURRENT_LIST_DIR}/src/utilities.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/fakufaku/components/fft/fft.c
)

target_include_directories(fft INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/include
  ${CMAKE_CURRENT_LIST_DIR}/third-party/fakufaku/components/fft/include
  ${CMAKE_CURRENT_LIST_DIR}/../buffer/include
)

target_link_libraries(usermod INTERFACE fft)
