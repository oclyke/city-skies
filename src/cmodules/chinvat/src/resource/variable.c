#include "pychinvat/resource/variable.h"

#include <stdio.h>

#include "py/obj.h"
#include "py/runtime.h"
#include "pychinvat/resource/variable/boolean.h"
#include "pychinvat/resource/variable/double.h"
#include "pychinvat/resource/variable/integer.h"
#include "pychinvat/resource/variable/option.h"
#include "resource.pb.h"

// underlying data comes from chinvat protobuf definitions
typedef struct _Variable_obj_t {
  mp_obj_base_t base;
  Resource_Variable def;
} Variable_obj_t;

STATIC void print(
    const mp_print_t* print, mp_obj_t self_in, mp_print_kind_t kind) {
  (void)kind;
  // Variable_obj_t* self = MP_OBJ_TO_PTR(self_in);
  mp_print_str(print, "Variable(");
  mp_print_str(print, ")");
}

STATIC mp_obj_t make_new(
    const mp_obj_type_t* type, size_t n_args, size_t n_kw,
    const mp_obj_t* args) {
  Variable_obj_t* self = m_new_obj(Variable_obj_t);
  self->base.type = &Variable_type;

  // zero the underlying structure
  memset(&self->def, 0x00, sizeof(self->def));

  return MP_OBJ_FROM_PTR(self);
}

// Class methods
STATIC mp_obj_t verify(mp_obj_t self_in) {
  // Variable_obj_t *self = MP_OBJ_TO_PTR(self_in);
  return mp_const_true;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(verify_obj, verify);

// Locals dict
STATIC const mp_rom_map_elem_t locals_table[] = {
    {MP_ROM_QSTR(MP_QSTR_verify), MP_ROM_PTR(&verify_obj)},

    {MP_OBJ_NEW_QSTR(MP_QSTR_Integer), (mp_obj_t)&Integer_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_Double), (mp_obj_t)&Double_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_Option), (mp_obj_t)&Option_type},
};
STATIC MP_DEFINE_CONST_DICT(locals_dict, locals_table);

const mp_obj_type_t Variable_type = {
    {&mp_type_type},
    .name = MP_QSTR_Variable,
    .print = print,
    .make_new = make_new,
    .locals_dict = (mp_obj_dict_t*)&locals_dict,
};