add_library(incident_fft INTERFACE)

target_sources(incident_fft INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/src/module.c
  ${CMAKE_CURRENT_LIST_DIR}/src/plan.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/fakufaku/components/fft/fft.c
)

target_include_directories(incident_fft INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/src
  ${CMAKE_CURRENT_LIST_DIR}/src/include
  ${CMAKE_CURRENT_LIST_DIR}/third-party/fakufaku/components/fft/include
)

target_link_libraries(usermod INTERFACE incident_fft)
