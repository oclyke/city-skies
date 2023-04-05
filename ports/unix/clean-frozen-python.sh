# https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
# (last component of path used to find the script must not be a symlink - there is a multi-line way to do that if needed see above)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# get common locations
source $SCRIPT_DIR/common.sh

BUILD=$MPY_UNIX_PORT_ROOT/build-$VARIANT

echo "cleaning frozen python files from build at:\n$BUILD"

rm -rf $BUILD/frozen_mpy
rm -rf $BUILD/genhdr
