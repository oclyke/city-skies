// Set base feature level.
#define MICROPY_CONFIG_ROM_LEVEL (MICROPY_CONFIG_ROM_LEVEL_EXTRA_FEATURES)

// Enable extra Unix features.
#include "../../../../third-party/micropython/ports/unix/variants/mpconfigvariant_common.h"

// #define MICROPY_PY_THREAD                 (0)

// // Disable some features that come enabled by default with the feature level.
// #define MICROPY_PY_BUILTINS_EXECFILE            (0)
// #define MICROPY_PY_SYS_STDIO_BUFFER             (0)
// #define MICROPY_PY_USELECT                      (0)

// // Enable some additional features.
// #define MICROPY_REPL_EMACS_WORDS_MOVE           (1)
// #define MICROPY_REPL_EMACS_EXTRA_WORDS_MOVE     (1)
// #define MICROPY_PY_SYS_SETTRACE                 (1)
// #define MICROPY_PY_URANDOM_SEED_INIT_FUNC       (mp_urandom_seed_init())
