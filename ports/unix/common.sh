# https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
# (last component of path used to find the script must not be a symlink - there is a multi-line way to do that if needed see above)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR=$SCRIPT_DIR/../..

# roots
MPY_ROOT=$ROOT_DIR/third-party/micropython
MPY_UNIX_PORT_ROOT=$MPY_ROOT/ports/unix

# default values
export VARIANT=city-skies
export VARIANT_DIR=$SCRIPT_DIR/variants/$VARIANT

# where the executable gets put by the micropython build system :/
export EXEC=$MPY_UNIX_PORT_ROOT/build-$VARIANT/build-$VARIANT/micropython-dev
