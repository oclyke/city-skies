#include "pychinvat/system/identity.h"

#include <stdio.h>

#include "py/obj.h"
#include "py/runtime.h"
#include "system.pb.h"

// underlying data comes from chinvat protobuf definitions
typedef struct _System_SystemInfo_IdentityInfo_obj_t {
  mp_obj_base_t base;
  System_SystemInfo_IdentityInfo def;
} System_SystemInfo_IdentityInfo_obj_t;

STATIC void print(
    const mp_print_t* print, mp_obj_t self_in, mp_print_kind_t kind) {
  (void)kind;
  // System_SystemInfo_IdentityInfo_obj_t* self = MP_OBJ_TO_PTR(self_in);
  mp_print_str(print, "System_SystemInfo_IdentityInfo(");
  mp_print_str(print, ")");
}

STATIC mp_obj_t make_new(
    const mp_obj_type_t* type, size_t n_args, size_t n_kw,
    const mp_obj_t* args) {
  System_SystemInfo_IdentityInfo_obj_t* self =
      m_new_obj(System_SystemInfo_IdentityInfo_obj_t);
  self->base.type = &System_SystemInfo_IdentityInfo_type;

  // zero the underlying structure
  memset(&self->def, 0x00, sizeof(self->def));

  return MP_OBJ_FROM_PTR(self);
}

// Class methods
STATIC mp_obj_t verify(mp_obj_t self_in) {
  // System_SystemInfo_IdentityInfo_obj_t *self = MP_OBJ_TO_PTR(self_in);
  return mp_const_true;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(verify_obj, verify);

// Locals dict
STATIC const mp_rom_map_elem_t locals_table[] = {
    {MP_ROM_QSTR(MP_QSTR_verify), MP_ROM_PTR(&verify_obj)},
};
STATIC MP_DEFINE_CONST_DICT(locals_dict, locals_table);

const mp_obj_type_t System_SystemInfo_IdentityInfo_type = {
    {&mp_type_type},
    .name = MP_QSTR_System_SystemInfo_IdentityInfo,
    .print = print,
    .make_new = make_new,
    .locals_dict = (mp_obj_dict_t*)&locals_dict,
};
