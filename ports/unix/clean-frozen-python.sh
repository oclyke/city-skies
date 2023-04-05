# get common locations
source ./common.sh

BUILD=$MPY_UNIX_PORT_ROOT/build-$VARIANT

echo "cleaning frozen python files from build at:\n$BUILD"

rm -rf $BUILD/frozen_mpy
rm -rf $BUILD/genhdr
