add_library(sicgl INTERFACE)

target_sources(sicgl INTERFACE
  # python bindings
  ${CMAKE_CURRENT_LIST_DIR}/src/module.c
  # ${CMAKE_CURRENT_LIST_DIR}/src/sicgl/sicgl.c
  # ${CMAKE_CURRENT_LIST_DIR}/src/sicgl/interface.c
  # ${CMAKE_CURRENT_LIST_DIR}/src/sicgl/screen.c
  # ${CMAKE_CURRENT_LIST_DIR}/src/sicgl/utilities.c

  # sicgl library sources
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/color_sequence.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/interpolation.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/iter.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/screen.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/translate.c

  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/specific/blit.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/specific/direct.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/specific/display.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/specific/field.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/specific/global.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/specific/screen.c  
)

target_include_directories(sicgl INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/include
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/include
)

target_compile_options(sicgl INTERFACE
  -Wno-unused-label
  -Wno-error=unused-label
)

target_link_libraries(usermod INTERFACE sicgl)