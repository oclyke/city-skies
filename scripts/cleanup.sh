SCRIPT_DIR_ABSOLUTE="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";
SCRIPT_DIR_RELATIVE="$(dirname "$0")"

ROOT_DIR_ABSOLUTE=$SCRIPT_DIR_ABSOLUTE/..
ROOT_DIR_RELATIVE=$SCRIPT_DIR_RELATIVE/..

echo "cleaning up previous installations"

# deactivate virtual environement
deactivate 2> /dev/null

# remove virtual environments
find $ROOT_DIR_ABSOLUTE/bin -type d -name "venv*"  -exec rm -rf {} \; | true
rm -rf $ROOT_DIR_ABSOLUTE/bin/venv
