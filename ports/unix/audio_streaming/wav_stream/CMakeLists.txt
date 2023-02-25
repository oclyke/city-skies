# https://cliutils.gitlab.io/modern-cmake
cmake_minimum_required(VERSION 3.21...3.24)
project(
  wav_stream
  VERSION 0.0
  LANGUAGES C
)

set(CMAKE_C_STANDARD 17)

# handle command line options
if(DEFINED DEBUG)
message("debug was set")
message("but nothing was done because of it")
endif()

# find the SndFile Cmake package
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/third-party/libsndfile/cmake)
message("CMAKE_MODULE_PATH = " ${CMAKE_MODULE_PATH})
find_package(SndFile REQUIRED)


# set some useful variables
set(TARGET_NAME "wavstream")

# # create useful variables
# set(SICGL_LIB_DEPS -lm)
# set(SICGL_ROOT_DIR ${CMAKE_SOURCE_DIR})
# set(SICGL_LIBRARIES sicgl ${SICGL_LIB_DEPS})

set(WAV_STREAM_SOURCES
  ${CMAKE_CURRENT_LIST_DIR}/stream_wav.c
)


add_executable(${TARGET_NAME})
target_sources(${TARGET_NAME} PRIVATE
  ${WAV_STREAM_SOURCES}
)
target_include_directories(${TARGET_NAME} PRIVATE
  ${CMAKE_CURRENT_LIST_DIR}
	${CMAKE_CURRENT_LIST_DIR}/include
)
target_link_libraries(${TARGET_NAME} PRIVATE
  SndFile::sndfile
)


add_executable(client ${CMAKE_CURRENT_LIST_DIR}/client.c)
add_executable(server ${CMAKE_CURRENT_LIST_DIR}/server.c)
