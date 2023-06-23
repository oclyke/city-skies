add_library(transform INTERFACE)

target_sources(transform INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/src/module.c
)

target_include_directories(transform INTERFACE
  # ${CMAKE_CURRENT_LIST_DIR}/include
)

target_link_libraries(usermod INTERFACE transform)
