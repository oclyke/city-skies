# wavestream

notes about building:
* cmake needs to "find" the libsndfile package, but the usual file that would do this seems to be a built output from libsndfile - so for everything to really work you probably need to build libsndfile first (in the libsndfile root: mkdir build; cd build; cmake ..; cmake --build .)

