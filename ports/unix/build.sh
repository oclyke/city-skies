# get common locations
source ./common.sh

# allow easy loading of environment
ENV_FILE=$SCRIPT_DIR/.env.sh
[ -f "$ENV_FILE" ] && echo "sourcing $ENV_FILE" && source $ENV_FILE

make -C $MPY_UNIX_PORT_ROOT submodules
make -C $MPY_UNIX_PORT_ROOT $1
