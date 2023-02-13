#include "pysicgl/interface.h"

#include <errno.h>
#include <stdio.h>

#include "py/obj.h"
#include "py/runtime.h"
#include "pysicgl/drawing/blit.h"
#include "pysicgl/drawing/compose.h"
#include "pysicgl/drawing/field.h"
#include "pysicgl/drawing/global.h"
#include "pysicgl/drawing/interface.h"
#include "pysicgl/drawing/screen.h"
#include "pysicgl/screen.h"
#include "pysicgl/utilities.h"

// attribute helpers
STATIC mp_obj_t get_memory(mp_obj_t self_in) {
  Interface_obj_t* self = MP_OBJ_TO_PTR(self_in);
  size_t len = self->interface.length * bytes_per_pixel();
  return mp_obj_new_bytearray_by_ref(len, self->interface.memory);
}
STATIC mp_obj_t get_screen(mp_obj_t self_in) {
  Interface_obj_t* self = MP_OBJ_TO_PTR(self_in);
  if (NULL == self->interface.screen) {
    return mp_const_none;
  } else {
    return mp_obj_new_screen_reference(self->interface.screen);
  }
}

// class methods
STATIC mp_obj_t set_memory(mp_obj_t self_in, mp_obj_t buffer) {
  Interface_obj_t* self = MP_OBJ_TO_PTR(self_in);

  mp_buffer_info_t buffer_info;
  mp_get_buffer_raise(buffer, &buffer_info, MP_BUFFER_READ | MP_BUFFER_WRITE);

  // set the interface memory
  self->interface.memory = buffer_info.buf;
  self->interface.length = buffer_info.len / bytes_per_pixel();

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(set_memory_obj, set_memory);

STATIC mp_obj_t set_screen(mp_obj_t self_in, mp_obj_t screen_obj) {
  Interface_obj_t* self = MP_OBJ_TO_PTR(self_in);
  Screen_obj_t* screen = screen_from_obj(screen_obj);
  self->interface.screen = screen->screen;
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(set_screen_obj, set_screen);

// drawing methods
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    interface_scale_obj, 2, 2, interface_scale);

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    interface_fill_obj, 2, 2, interface_fill);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    interface_pixel_obj, 3, 3, interface_pixel);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    interface_line_obj, 4, 4, interface_line);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    interface_rectangle_obj, 4, 4, interface_rectangle);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    interface_rectangle_filled_obj, 4, 4, interface_rectangle_filled);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    interface_circle_obj, 4, 4, interface_circle);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    interface_ellipse_obj, 4, 4, interface_ellipse);

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    global_pixel_obj, 3, 3, global_pixel);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(global_line_obj, 4, 4, global_line);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    global_rectangle_obj, 4, 4, global_rectangle);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    global_rectangle_filled_obj, 4, 4, global_rectangle_filled);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    global_circle_obj, 4, 4, global_circle);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    global_ellipse_obj, 4, 4, global_ellipse);

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(screen_fill_obj, 2, 2, screen_fill);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    screen_pixel_obj, 4, 4, screen_pixel);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(screen_line_obj, 5, 5, screen_line);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    screen_rectangle_obj, 5, 5, screen_rectangle);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    screen_rectangle_filled_obj, 5, 5, screen_rectangle_filled);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    screen_circle_obj, 5, 5, screen_circle);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    screen_ellipse_obj, 5, 5, screen_ellipse);

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(compose_obj, 4, 4, compose);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(blit_obj, 3, 3, blit);
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    scalar_field_obj, 4, 5, scalar_field);

// locals dict
STATIC const mp_rom_map_elem_t locals_table[] = {
    {MP_ROM_QSTR(MP_QSTR_set_memory), MP_ROM_PTR(&set_memory_obj)},
    {MP_ROM_QSTR(MP_QSTR_set_screen), MP_ROM_PTR(&set_screen_obj)},

    // drawing
    {MP_ROM_QSTR(MP_QSTR_interface_scale), MP_ROM_PTR(&interface_scale_obj)},

    {MP_ROM_QSTR(MP_QSTR_interface_fill), MP_ROM_PTR(&interface_fill_obj)},
    {MP_ROM_QSTR(MP_QSTR_interface_pixel), MP_ROM_PTR(&interface_pixel_obj)},
    {MP_ROM_QSTR(MP_QSTR_interface_line), MP_ROM_PTR(&interface_line_obj)},
    {MP_ROM_QSTR(MP_QSTR_interface_rectangle),
     MP_ROM_PTR(&interface_rectangle_obj)},
    {MP_ROM_QSTR(MP_QSTR_interface_rectangle_filled),
     MP_ROM_PTR(&interface_rectangle_filled_obj)},
    {MP_ROM_QSTR(MP_QSTR_interface_circle), MP_ROM_PTR(&interface_circle_obj)},
    {MP_ROM_QSTR(MP_QSTR_interface_ellipse),
     MP_ROM_PTR(&interface_ellipse_obj)},

    {MP_ROM_QSTR(MP_QSTR_global_pixel), MP_ROM_PTR(&global_pixel_obj)},
    {MP_ROM_QSTR(MP_QSTR_global_line), MP_ROM_PTR(&global_line_obj)},
    {MP_ROM_QSTR(MP_QSTR_global_rectangle), MP_ROM_PTR(&global_rectangle_obj)},
    {MP_ROM_QSTR(MP_QSTR_global_rectangle_filled),
     MP_ROM_PTR(&global_rectangle_filled_obj)},
    {MP_ROM_QSTR(MP_QSTR_global_circle), MP_ROM_PTR(&global_circle_obj)},
    {MP_ROM_QSTR(MP_QSTR_global_ellipse), MP_ROM_PTR(&global_ellipse_obj)},

    {MP_ROM_QSTR(MP_QSTR_screen_fill), MP_ROM_PTR(&screen_fill_obj)},
    {MP_ROM_QSTR(MP_QSTR_screen_pixel), MP_ROM_PTR(&screen_pixel_obj)},
    {MP_ROM_QSTR(MP_QSTR_screen_line), MP_ROM_PTR(&screen_line_obj)},
    {MP_ROM_QSTR(MP_QSTR_screen_rectangle), MP_ROM_PTR(&screen_rectangle_obj)},
    {MP_ROM_QSTR(MP_QSTR_screen_rectangle_filled),
     MP_ROM_PTR(&screen_rectangle_filled_obj)},
    {MP_ROM_QSTR(MP_QSTR_screen_circle), MP_ROM_PTR(&screen_circle_obj)},
    {MP_ROM_QSTR(MP_QSTR_screen_ellipse), MP_ROM_PTR(&screen_ellipse_obj)},

    {MP_ROM_QSTR(MP_QSTR_compose), MP_ROM_PTR(&compose_obj)},
    {MP_ROM_QSTR(MP_QSTR_blit), MP_ROM_PTR(&blit_obj)},
    {MP_ROM_QSTR(MP_QSTR_scalar_field), MP_ROM_PTR(&scalar_field_obj)},

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
  mp_obj_print_helper(
      print, mp_obj_new_int((mp_int_t)self->interface.memory), PRINT_REPR);
  mp_print_str(print, ", length: ");
  mp_obj_print_helper(
      print, mp_obj_new_int(self->interface.length), PRINT_REPR);
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
      {MP_QSTR_screen, MP_ARG_OBJ | MP_ARG_REQUIRED, {.u_obj = NULL}},
      {MP_QSTR_memory, MP_ARG_OBJ | MP_ARG_REQUIRED, {.u_obj = NULL}},
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
  set_screen(self_obj, args[ARG_screen].u_obj);
  set_memory(self_obj, args[ARG_memory].u_obj);

  return self_obj;
}

STATIC void attr(mp_obj_t self_in, qstr attribute, mp_obj_t* destination) {
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
    {&mp_type_type}, .name = MP_QSTR_Interface,
    .print = print,  .make_new = make_new,
    .attr = attr,    .locals_dict = (mp_obj_dict_t*)&locals_dict,
};
