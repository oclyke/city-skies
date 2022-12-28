#include "py/obj.h"
#include "py/runtime.h"

#include "pychinvat/system/firmware.h"
#include "pychinvat/system/hardware.h"
#include "pychinvat/system/uuidv4.h"
#include "pychinvat/system/version.h"
#include "pychinvat/system/network.h"
#include "pychinvat/system/identity.h"
#include "pychinvat/system/system.h"

#include "pychinvat/shard/atom.h"
#include "pychinvat/shard/variable.h"
#include "pychinvat/shard/variable/boolean.h"
#include "pychinvat/shard/variable/double.h"
#include "pychinvat/shard/variable/integer.h"
#include "pychinvat/shard/variable/option.h"

STATIC const mp_rom_map_elem_t globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_chinvat)},

    // classes
    {MP_OBJ_NEW_QSTR(MP_QSTR_System_UUIDv4), (mp_obj_t)&System_UUIDv4_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_System_Version), (mp_obj_t)&System_Version_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_System_HardwareInfo),
     (mp_obj_t)&System_HardwareInfo_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_System_FirmwareInfo),
     (mp_obj_t)&System_FirmwareInfo_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_System_NetworkInfo),
     (mp_obj_t)&System_NetworkInfo_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_System_SystemInfo_IdentityInfo),
     (mp_obj_t)&System_SystemInfo_IdentityInfo_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_System_SystemInfo),
     (mp_obj_t)&System_SystemInfo_type},

    {MP_OBJ_NEW_QSTR(MP_QSTR_Shard_Atom), (mp_obj_t)&Shard_Atom_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_Shard_Variable), (mp_obj_t)&Shard_Variable_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_Shard_Variable_Integer), (mp_obj_t)&Shard_Variable_Integer_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_Shard_Variable_Double), (mp_obj_t)&Shard_Variable_Double_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_Shard_Variable_Option), (mp_obj_t)&Shard_Variable_Option_type},
};
STATIC MP_DEFINE_CONST_DICT(globals_dict, globals_table);

const mp_obj_module_t chinvat_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&globals_dict,
};

MP_REGISTER_MODULE(MP_QSTR_chinvat, chinvat_module);
