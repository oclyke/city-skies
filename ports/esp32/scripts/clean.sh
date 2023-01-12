SCRIPT_DIR_ABSOLUTE="$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-$0}"; )" &> /dev/null && pwd 2> /dev/null; )";

BUILD_DIR_ABSOLUTE=$SCRIPT_DIR_ABSOLUTE/../build

rm -rf ${BUILD_DIR_ABSOLUTE}/genhdr
rm -rf ${BUILD_DIR_ABSOLUTE}/frozen_mpy
