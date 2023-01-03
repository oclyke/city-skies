#include <math.h>

#include "plan.h"
#include "py/runtime.h"

#define ERROR_NOT_FLOAT MP_ERROR_TEXT("not a float")

// Define all properties of the module.
// Table entries are key/value pairs of the attribute name (a string)
// and the MicroPython object reference.
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
STATIC const mp_rom_map_elem_t module_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_fft)},
    {MP_OBJ_NEW_QSTR(MP_QSTR_FftPlan), (mp_obj_t)&FftPlan_type},
};
STATIC MP_DEFINE_CONST_DICT(module_globals, module_globals_table);

// Define module object.
const mp_obj_module_t fft_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&module_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_fft, fft_module);
