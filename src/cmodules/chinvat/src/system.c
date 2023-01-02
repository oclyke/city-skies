#include "pychinvat/system.h"

#include <stdio.h>

#include "py/obj.h"
#include "py/runtime.h"
#include "pychinvat/system/firmware.h"
#include "pychinvat/system/hardware.h"
#include "pychinvat/system/network.h"
#include "pychinvat/system/system_info.h"
#include "pychinvat/system/system_info/identity.h"
#include "pychinvat/system/uuidv4.h"
#include "pychinvat/system/version.h"
#include "resource.pb.h"

// underlying data comes from chinvat protobuf definitions
typedef struct _System_obj_t {
  mp_obj_base_t base;
} System_obj_t;

STATIC void print(
    const mp_print_t* print, mp_obj_t self_in, mp_print_kind_t kind) {
  (void)kind;
  // System_obj_t* self = MP_OBJ_TO_PTR(self_in);
  mp_print_str(print, "System(");
  mp_print_str(print, ")");
}

STATIC mp_obj_t make_new(
    const mp_obj_type_t* type, size_t n_args, size_t n_kw,
    const mp_obj_t* args) {
  System_obj_t* self = m_new_obj(System_obj_t);
  self->base.type = &System_type;

  return MP_OBJ_FROM_PTR(self);
}

// Locals dict
STATIC const mp_rom_map_elem_t locals_table[] = {
    {MP_OBJ_NEW_QSTR(MP_QSTR_UUIDv4), (mp_obj_t)&UUIDv4_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_Version), (mp_obj_t)&Version_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_HardwareInfo), (mp_obj_t)&HardwareInfo_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_FirmwareInfo), (mp_obj_t)&FirmwareInfo_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_NetworkInfo), (mp_obj_t)&NetworkInfo_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_System_SystemInfo), (mp_obj_t)&SystemInfo_type},
};
STATIC MP_DEFINE_CONST_DICT(locals_dict, locals_table);

const mp_obj_type_t System_type = {
    {&mp_type_type},
    .name = MP_QSTR_System,
    .print = print,
    .make_new = make_new,
    .locals_dict = (mp_obj_dict_t*)&locals_dict,
};
