# this script is meant to be sourced

SCRIPT_DIR_ABSOLUTE="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";
PROJECT_DIR_RELATIVE="$(dirname "$0")"

ROOT_DIR_ABSOLUTE=$SCRIPT_DIR_ABSOLUTE/..
ROOT_DIR_RELATIVE=$PROJECT_DIR_RELATIVE/..

# allow easy loading of environment
ENV_FILE=$SCRIPT_DIR_ABSOLUTE/bin/.env.sh
[ -f "$ENV_FILE" ] && source $ENV_FILE

# some setup things
[ -z "$PYTHON3" ] && echo "PYTHON3 was not set" && PYTHON3=python3

# run cleanup
. ./scripts/cleanup.sh

# system vars
reminders=
timestamp=$(date +%s)

# # create and activate virtual environment
# reminders+="activate the virtual environment:\\n\\n. venv/bin/activate\\n"
venv="$ROOT_DIR_ABSOLUTE/bin/venv$timestamp"
${PYTHON3} -m venv $venv
ln -s $venv bin/venv
. $venv/bin/activate

# upgrade pip and install python requirements
pip install --upgrade pip

# show reminders
echo $reminders
