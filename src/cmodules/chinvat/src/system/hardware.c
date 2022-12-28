#include "pychinvat/system/hardware.h"

#include <stdio.h>

#include "py/obj.h"
#include "py/runtime.h"
#include "system.pb.h"

// underlying data comes from chinvat protobuf definitions
typedef struct _System_HardwareInfo_obj_t {
  mp_obj_base_t base;
  System_HardwareInfo def;
} System_HardwareInfo_obj_t;

STATIC void print(
    const mp_print_t* print, mp_obj_t self_in, mp_print_kind_t kind) {
  (void)kind;
  // System_HardwareInfo_obj_t* self = MP_OBJ_TO_PTR(self_in);
  mp_print_str(print, "System_HardwareInfo(");
  mp_print_str(print, ")");
}

STATIC mp_obj_t make_new(
    const mp_obj_type_t* type, size_t n_args, size_t n_kw,
    const mp_obj_t* args) {
  System_HardwareInfo_obj_t* self = m_new_obj(System_HardwareInfo_obj_t);
  self->base.type = &System_HardwareInfo_type;
  self->def.has_id = false;
  self->def.has_version = false;
  self->def.name.arg = NULL;
  self->def.name.funcs.decode = NULL;
  return MP_OBJ_FROM_PTR(self);
}

// Class methods
STATIC mp_obj_t verify(mp_obj_t self_in) {
  // System_HardwareInfo_obj_t *self = MP_OBJ_TO_PTR(self_in);
  return mp_const_true;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(verify_obj, verify);

// Locals dict
STATIC const mp_rom_map_elem_t locals_table[] = {
    {MP_ROM_QSTR(MP_QSTR_verify), MP_ROM_PTR(&verify_obj)},
};
STATIC MP_DEFINE_CONST_DICT(locals_dict, locals_table);

const mp_obj_type_t System_HardwareInfo_type = {
    {&mp_type_type},
    .name = MP_QSTR_System_HardwareInfo,
    .print = print,
    .make_new = make_new,
    .locals_dict = (mp_obj_dict_t*)&locals_dict,
};
