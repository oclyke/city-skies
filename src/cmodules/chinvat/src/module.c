#include "py/obj.h"
#include "py/runtime.h"
#include "pychinvat/resource.h"
#include "pychinvat/shard.h"
#include "pychinvat/system.h"

STATIC const mp_rom_map_elem_t globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_chinvat)},

    // classes
    {MP_OBJ_NEW_QSTR(MP_QSTR_Resource), (mp_obj_t)&Resource_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_System), (mp_obj_t)&System_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_Shard), (mp_obj_t)&Shard_type},
};
STATIC MP_DEFINE_CONST_DICT(globals_dict, globals_table);

const mp_obj_module_t chinvat_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&globals_dict,
};

MP_REGISTER_MODULE(MP_QSTR_chinvat, chinvat_module);
