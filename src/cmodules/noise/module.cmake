add_library(cnoise INTERFACE)

target_sources(cnoise INTERFACE
  # the cnoise module
  ${CMAKE_CURRENT_LIST_DIR}/src/module.c

  # types
  ${CMAKE_CURRENT_LIST_DIR}/src/open-simplex-noise.c

  # open simplex noise in c (git submodule)
  # https://github.com/smcameron/open-simplex-noise-in-c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/open-simplex-noise-in-c/open-simplex-noise.c
)

target_include_directories(cnoise INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/include
  ${CMAKE_CURRENT_LIST_DIR}/third-party/open-simplex-noise-in-c
)

target_link_libraries(usermod INTERFACE cnoise)
