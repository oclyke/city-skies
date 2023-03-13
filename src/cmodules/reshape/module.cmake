add_library(reshape INTERFACE)

target_sources(reshape INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/src/module.c
)

target_include_directories(reshape INTERFACE
)

target_link_libraries(usermod INTERFACE reshape)
