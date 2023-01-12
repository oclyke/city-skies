#include "cnoise/open-simplex.h"
#include "py/runtime.h"

STATIC const mp_rom_map_elem_t globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_cnoise)},

    // types
    {MP_OBJ_NEW_QSTR(MP_QSTR_OpenSimplexNoise),
     (mp_obj_t)&open_simplex_noise_obj_type},
};
STATIC MP_DEFINE_CONST_DICT(module_globals, globals_table);

const mp_obj_module_t noise_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&module_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_noise, noise_module);
