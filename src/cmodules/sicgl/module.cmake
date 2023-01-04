add_library(sicgl INTERFACE)

target_sources(sicgl INTERFACE
  # python bindings
  ${CMAKE_CURRENT_LIST_DIR}/src/module.c
  ${CMAKE_CURRENT_LIST_DIR}/src/utilities.c
  ${CMAKE_CURRENT_LIST_DIR}/src/screen.c
  ${CMAKE_CURRENT_LIST_DIR}/src/field.c
  ${CMAKE_CURRENT_LIST_DIR}/src/interface.c
  ${CMAKE_CURRENT_LIST_DIR}/src/color_sequence.c
  ${CMAKE_CURRENT_LIST_DIR}/src/drawing/compose.c
  ${CMAKE_CURRENT_LIST_DIR}/src/drawing/global.c
  ${CMAKE_CURRENT_LIST_DIR}/src/drawing/screen.c
  ${CMAKE_CURRENT_LIST_DIR}/src/drawing/interface.c
  ${CMAKE_CURRENT_LIST_DIR}/src/drawing/blit.c
  ${CMAKE_CURRENT_LIST_DIR}/src/drawing/field.c

  # sicgl library sources
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/blit.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/color_sequence.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/compose.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/field.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/gamma.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/iter.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/screen.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/translate.c

  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/domain/global.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/domain/interface.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/domain/screen.c
  
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/private/interpolation.c
  ${CMAKE_CURRENT_LIST_DIR}/third-party/sicgl/src/private/direct.c 
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
