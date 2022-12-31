#include "pysicgl/field.h"

#include <stdio.h>

#include "py/obj.h"
#include "py/runtime.h"
#include "pysicgl/utilities.h"

// class methods
STATIC mp_obj_t set_scalars(mp_obj_t self_in, mp_obj_t buffer) {
  ScalarField_obj_t* self = MP_OBJ_TO_PTR(self_in);

  mp_buffer_info_t buffer_info;
  mp_get_buffer_raise(buffer, &buffer_info, MP_BUFFER_READ | MP_BUFFER_WRITE);

  // set the scalars memory
  self->scalars = buffer_info.buf;
  self->length = buffer_info.len;

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(set_scalars_obj, set_scalars);

// locals dict
STATIC const mp_rom_map_elem_t locals_table[] = {
    {MP_ROM_QSTR(MP_QSTR_set_scalars), MP_ROM_PTR(&set_scalars_obj)},
};
STATIC MP_DEFINE_CONST_DICT(locals_dict, locals_table);

// type methods
STATIC void print(
    const mp_print_t* print, mp_obj_t self_in, mp_print_kind_t kind) {
  (void)kind;
  ScalarField_obj_t* self = MP_OBJ_TO_PTR(self_in);
  mp_print_str(print, "ScalarField( length: ");
  mp_obj_print_helper(print, mp_obj_new_int(self->length), PRINT_REPR);
  mp_print_str(print, ", memory: ");
  mp_obj_print_helper(
      print, mp_obj_new_int((mp_int_t)self->scalars), PRINT_REPR);
  mp_print_str(print, ")");
}

STATIC mp_obj_t make_new(
    const mp_obj_type_t* type, size_t n_args, size_t n_kw,
    const mp_obj_t* all_args) {
  // parse args
  enum {
    ARG_scalars,
  };
  static const mp_arg_t allowed_args[] = {
      {MP_QSTR_scalars, MP_ARG_OBJ, {.u_obj = NULL}},
  };
  mp_map_t kw_args;
  mp_map_init_fixed_table(&kw_args, n_kw, all_args + n_args);
  mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
  mp_arg_parse_all_kw_array(
      n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

  // create instance object
  ScalarField_obj_t* self = m_new_obj(ScalarField_obj_t);
  self->base.type = &ScalarField_type;
  self->scalars = NULL;
  self->length = 0;
  mp_obj_t self_obj = MP_OBJ_FROM_PTR(self);

  // set initial values
  if (NULL != args[ARG_scalars].u_obj) {
    set_scalars(self_obj, args[ARG_scalars].u_obj);
  }

  return self_obj;
}

const mp_obj_type_t ScalarField_type = {
    {&mp_type_type},
    .name = MP_QSTR_ScalarField,
    .print = print,
    .make_new = make_new,
    .locals_dict = (mp_obj_dict_t*)&locals_dict,
};
