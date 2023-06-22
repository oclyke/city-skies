# unix port

this is the unix port of city-skies.

# building

building the unix port is fairly simple. it will require getting all the dependencies (available as git submodules) and then running the build script. (more or less).

the best reference is the CI/CD GitHub action workflow file: [.github/workflows/build-unix.yml](../../.github/workflows/build-unix.yml)

the steps are basically:
* clone the repo
* update submodules (but don't do it recursively, micropython and esp-idf are huge)
    * ```git submodule update --init third-party/micropython```
    * ```git submodule update --init --recursicve src/cmodules```
* build mpy-cross
    * ```make -C third-party/micropython/mpy-cross```
* get unix submodules for micropython
    * ```make -C third-party/micropython/ports/unix submodules```
* build the city-skies unix port
    * ```cd ports/unix```
    * ```./build.sh```
* source the common environment variables to locate the executable
    * ```source ./comon.sh```
* run the city-skies unix port
    * ```$EXEC main.py```
* use the [city-skies-visualizer](https://github.com/oclyke/city-skies-visualizer) to view the output
* use the [city-skies-app]()

# filesystem

the filesystem is used to persist settings.

there are two top level directories:
* ephemeral
* persistent

the persistent directory is managed manually - it must contain the shard programs. the ephemeral directory is managed automatically and used to persist settings between runs.

**directory structure**

path | name | description
---|---|---
/runtime | | root
/runtime/persistent | | root of persistent data.
/runtime/persistent/shards | shards | directory where shard modules are stored. use a symbolic link to the example-shards directory to use the example shards.
/runtime/persistent/logs | logs | this is where logs are stored. logs are captured upon exceptions.
/runtime/ephemeral | | root of ephemeral data.
/runtime/ephemeral/artnet | artnet | [NOT USED] directory where artnet settings are stored.
/runtime/ephemeral/audio | audio | root of audio settings.
/runtime/ephemeral/audio/info | audio manager info | settings for the audio manager.
/runtime/ephemeral/audio/sources | audio sources | settings for individual audio sources.
/runtime/ephemeral/audio/sources/\<source\>/private_vars | standard audio source variables | standard variables for audio source (relied upon by system).
/runtime/ephemeral/audio/sources/\<source\>/vars | audio source variables | self-declared variables for audio source.
/runtime/ephemeral/globals/vars | global variables | persists global variables.
/runtime/ephemeral/stacks | stacks | information about stacks.
/runtime/ephemeral/stacks/info | stack manager info | settings for the stack manager.
/runtime/ephemeral/stacks/A | stack A | one of two stacks, enables seamless switching.
/runtime/ephemeral/stacks/B | stack B | one of two stacks, enables seamless switching.
/runtime/ephemeral/stacks/\<stack\>/layers | stack layers | information about layers in a stack.
/runtime/ephemeral/stacks/\<stack\>/layers/\<layer\>/info | layer info | configuration for a layer.
/runtime/ephemeral/stacks/\<stack\>/layers/\<layer\>/vars | layer variables | variables for a layer.
/runtime/ephemeral/stacks/\<stack\>/layers/\<layer\>/private_vars | standard layer variables | standard variables for a layer (relied upon by system).
/runtime/ephemeral/timebase | timebase | information about the timebase.
