#include <stdio.h>
#include <errno.h>

#include "py/obj.h"
#include "py/runtime.h"

#include "pysicgl/interface.h"
#include "pysicgl/screen.h"
#include "pysicgl/utilities.h"

// attribute helpers
STATIC mp_obj_t get_memory(mp_obj_t self_in) {
  Interface_obj_t *self = MP_OBJ_TO_PTR(self_in);
  size_t len = self->interface.length * bytes_per_pixel();
  return mp_obj_new_bytearray_by_ref(len, self->interface.memory);
}
STATIC mp_obj_t get_screen(mp_obj_t self_in) {
  Interface_obj_t *self = MP_OBJ_TO_PTR(self_in);
  return new_screen(self->interface.screen);
}

// class methods
STATIC mp_obj_t set_memory(mp_obj_t self_in, mp_obj_t buffer) {
  Interface_obj_t *self = MP_OBJ_TO_PTR(self_in);

  mp_buffer_info_t buffer_info;
  mp_get_buffer_raise(buffer, &buffer_info, MP_BUFFER_READ | MP_BUFFER_WRITE);

  // set the interface memory
  self->interface.memory = buffer_info.buf;
  self->interface.length = buffer_info.len;

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(set_memory_obj, set_memory);

STATIC mp_obj_t set_screen(mp_obj_t self_in, mp_obj_t screen_obj) {
  Interface_obj_t *self = MP_OBJ_TO_PTR(self_in);
  Screen_obj_t* screen = screen_from_obj(screen_obj);
  self->interface.screen = screen->screen;
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(set_screen_obj, set_screen);

// locals dict
STATIC const mp_rom_map_elem_t locals_table[] = {
    {MP_ROM_QSTR(MP_QSTR_set_memory), MP_ROM_PTR(&set_memory_obj)},
    {MP_ROM_QSTR(MP_QSTR_set_screen), MP_ROM_PTR(&set_screen_obj)},
};
STATIC MP_DEFINE_CONST_DICT(locals_dict, locals_table);

// type methods
STATIC void print(
    const mp_print_t* print, mp_obj_t self_in, mp_print_kind_t kind) {
  (void)kind;
  Interface_obj_t* self = MP_OBJ_TO_PTR(self_in);
  mp_print_str(print, "Interface( screen: ");
  mp_obj_print_helper(print, get_screen(self_in), PRINT_REPR);
  mp_print_str(print, ", memory: ");
  mp_obj_print_helper(print, mp_obj_new_int((mp_int_t)self->interface.memory), PRINT_REPR);
  mp_print_str(print, ", length: ");
  mp_obj_print_helper(print, mp_obj_new_int(self->interface.length), PRINT_REPR);
  mp_print_str(print, ")");
}

STATIC mp_obj_t make_new(
    const mp_obj_type_t* type, size_t n_args, size_t n_kw,
    const mp_obj_t* all_args) {
  // parse args
  enum {
    ARG_screen,
    ARG_memory,
  };
  static const mp_arg_t allowed_args[] = {
      {MP_QSTR_screen, MP_ARG_OBJ, {.u_obj = NULL}},
      {MP_QSTR_memory, MP_ARG_OBJ, {.u_obj = NULL}},
  };
  mp_map_t kw_args;
  mp_map_init_fixed_table(&kw_args, n_kw, all_args + n_args);
  mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
  mp_arg_parse_all_kw_array(
      n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

  // set the base type
  Interface_obj_t* self = m_new_obj(Interface_obj_t);
  self->base.type = &Interface_type;

  self->interface.length = 0;
  self->interface.memory = NULL;
  self->interface.screen = NULL;

  mp_obj_t self_obj = MP_OBJ_FROM_PTR(self);

  // configure interface
  mp_obj_t screen = args[ARG_screen].u_obj;
  mp_obj_t memory = args[ARG_memory].u_obj;
  if (NULL != screen) {
    set_screen(self_obj, screen);
  }
  if (NULL != memory) {
    set_memory(self_obj, memory);
  }

  return self_obj;
}

STATIC void attr(mp_obj_t self_in, qstr attribute, mp_obj_t *destination) {
    switch (attribute) {
      case MP_QSTR_memory:
        destination[0] = get_memory(self_in);
        break;
      
      case MP_QSTR_screen:
        destination[0] = get_screen(self_in);
        break;

      default:
        // No attribute found, continue lookup in locals dict.
        // https://github.com/micropython/micropython/pull/7934
        destination[1] = MP_OBJ_SENTINEL;
        break;
    }
}

const mp_obj_type_t Interface_type = {
    {&mp_type_type},
    .name = MP_QSTR_Interface,
    .print = print,
    .make_new = make_new,
    .attr = attr,
    .locals_dict = (mp_obj_dict_t*)&locals_dict,
};
