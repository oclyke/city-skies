add_library(buffer INTERFACE)

target_sources(buffer INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/src/module.c
  ${CMAKE_CURRENT_LIST_DIR}/src/utilities.c
  ${CMAKE_CURRENT_LIST_DIR}/src/buffer/float.c
)

target_include_directories(buffer INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/include
)

target_link_libraries(usermod INTERFACE buffer)
