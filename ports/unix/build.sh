# https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
# (last component of path used to find the script must not be a symlink - there is a multi-line way to do that if needed see above)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR=$SCRIPT_DIR/../..

# the first argument is passed along directly to make as the target
TARGET=$1

# roots
MPY_ROOT=$ROOT_DIR/third-party/micropython
MPY_UNIX_PORT_ROOT=$MPY_ROOT/ports/unix

# default values
export VARIANT=dev
export VARIANT_DIR=$SCRIPT_DIR/variants/$VARIANT
export BUILD=$SCRIPT_DIR/dist/$VARIANT

rm -rf $BUILD/frozen_mpy
rm -rf $BUILD/genhdr
make -C $MPY_UNIX_PORT_ROOT submodules
make -C $MPY_UNIX_PORT_ROOT $TARGET
