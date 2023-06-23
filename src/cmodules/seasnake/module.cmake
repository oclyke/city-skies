add_library(seasnake INTERFACE)

target_sources(seasnake INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/src/module.c
)

target_include_directories(seasnake INTERFACE
  # ${CMAKE_CURRENT_LIST_DIR}/include
)

target_link_libraries(usermod INTERFACE seasnake)
