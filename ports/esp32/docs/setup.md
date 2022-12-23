# setup a build environment

setting up a build environment for the esp32 boards requires the following aspects:
* the esp-idf
* micropython
* mpy-cross compiler
* the precious-time sources

the esp-idf subodule version is locked to a recent version compatible with the
version of micropython.

## submodules

there are many submodules available for precious-time contributed from several
sources:
* the precious-time sources
* the esp-idf
* micropython

it is NOT RECCOMENDED to clone precious-time with github desktop - it will default
to recursively downloading *all* submodules including **many** that are only
necessary to support various target architectures in micropython.

generally the subodules that are required can be gotten by:
``` sh
git submodule update --init # non-recursive, gets submodules for precious-time including esp-idf, micropython, and cmodules
git submodule update --init micropython # non-recursive, gets submodules required for the core of micropython
git submodule update --init --recursive esp-idf # recursively gets all esp-idf submodules

# for esp32
cd micropython/ports/esp32 && make submodules # prepares required submodules for esp32 port
```

## mpy-cross

the mpy-cross cross compiler is required to transform python files into "frozen" bytecode.

``` sh
make -C micropython/mpy-cross
```

## esp-idf tools

the esp-idf requires a one-time install (per version installed) and an export of tools to the command line environment.

``` sh
# once per esp-idf version
./esp-idf/install.sh

# once per session
. ./esp-idf/export.sh
```
