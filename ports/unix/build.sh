# https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
# (last component of path used to find the script must not be a symlink - there is a multi-line way to do that if needed see above)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# get common locations
source $SCRIPT_DIR/common.sh

# allow easy loading of environment
ENV_FILE=$SCRIPT_DIR/.env.sh
[ -f "$ENV_FILE" ] && echo "sourcing $ENV_FILE" && source $ENV_FILE

make -C $MPY_UNIX_PORT_ROOT submodules
make -C $MPY_UNIX_PORT_ROOT $1
