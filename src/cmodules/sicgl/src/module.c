#include "pysicgl.h"
#include "py/runtime.h"

// module
STATIC const mp_map_elem_t sicgl_globals_table[] = {
    {MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_sicgl)},

    // classes
    {MP_OBJ_NEW_QSTR(MP_QSTR_Screen), (mp_obj_t)&Screen_type},
};

STATIC MP_DEFINE_CONST_DICT(sicgl_globals, sicgl_globals_table);

const mp_obj_module_t sicgl_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&sicgl_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_sicgl, sicgl_module);
