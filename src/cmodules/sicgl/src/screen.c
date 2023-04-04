#include "pysicgl/screen.h"

#include <stdio.h>

#include "py/obj.h"
#include "py/runtime.h"
#include "pysicgl/utilities.h"

// attribute helpers
STATIC mp_obj_t get_width(mp_obj_t self_in) {
  Screen_obj_t* self = MP_OBJ_TO_PTR(self_in);
  return mp_obj_new_int(self->screen->width);
}

STATIC mp_obj_t get_height(mp_obj_t self_in) {
  Screen_obj_t* self = MP_OBJ_TO_PTR(self_in);
  return mp_obj_new_int(self->screen->height);
}

STATIC mp_obj_t get_pixels(mp_obj_t self_in) {
  Screen_obj_t* self = MP_OBJ_TO_PTR(self_in);
  return mp_obj_new_int(self->screen->width * self->screen->height);
}

// class methods
STATIC mp_obj_t normalize(mp_obj_t self_in) {
  Screen_obj_t* self = MP_OBJ_TO_PTR(self_in);
  int ret = screen_normalize(self->screen);
  if (0 != ret) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(normalize_obj, normalize);

STATIC mp_obj_t set_corners(mp_obj_t self_in, mp_obj_t c0, mp_obj_t c1) {
  Screen_obj_t* self = MP_OBJ_TO_PTR(self_in);
  ext_t u0, v0, u1, v1;
  int ret = unpack_ext_t_tuple2(c0, &u0, &v0);
  if (0 != ret) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }
  ret = unpack_ext_t_tuple2(c1, &u1, &v1);
  if (0 != ret) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }
  ret = screen_set_corners(self->screen, u0, v0, u1, v1);
  if (0 != ret) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }
  normalize(self);
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(set_corners_obj, set_corners);

STATIC mp_obj_t set_extent(mp_obj_t self_in, mp_obj_t extent) {
  Screen_obj_t* self = MP_OBJ_TO_PTR(self_in);
  ext_t width, height;
  int ret = unpack_ext_t_tuple2(extent, &width, &height);
  if (0 != ret) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }
  ret = screen_set_extent(self->screen, width, height);
  if (0 != ret) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }
  normalize(self);
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(set_extent_obj, set_extent);

STATIC mp_obj_t set_location(mp_obj_t self_in, mp_obj_t location) {
  Screen_obj_t* self = MP_OBJ_TO_PTR(self_in);
  ext_t lu, lv;
  int ret = unpack_ext_t_tuple2(location, &lu, &lv);
  if (0 != ret) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }
  ret = screen_set_location(self->screen, lu, lv);
  if (0 != ret) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }
  normalize(self);
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(set_location_obj, set_location);

STATIC mp_obj_t intersect(mp_obj_t self_in, mp_obj_t s0, mp_obj_t s1) {
  screen_t* target = screen_from_obj(self_in)->screen;
  screen_t* screen0 = screen_from_obj(s0)->screen;
  screen_t* screen1 = screen_from_obj(s1)->screen;
  int ret = screen_intersect(target, screen0, screen1);
  if (0 != ret) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(intersect_obj, intersect);

// locals dict
STATIC const mp_rom_map_elem_t locals_table[] = {
    {MP_ROM_QSTR(MP_QSTR_set_corners), MP_ROM_PTR(&set_corners_obj)},
    {MP_ROM_QSTR(MP_QSTR_set_extent), MP_ROM_PTR(&set_extent_obj)},
    {MP_ROM_QSTR(MP_QSTR_set_location), MP_ROM_PTR(&set_location_obj)},

    {MP_ROM_QSTR(MP_QSTR_normalize), MP_ROM_PTR(&normalize_obj)},
    {MP_ROM_QSTR(MP_QSTR_intersect), MP_ROM_PTR(&intersect_obj)},
};
STATIC MP_DEFINE_CONST_DICT(locals_dict, locals_table);

// type methods
STATIC void print(
    const mp_print_t* print, mp_obj_t self_in, mp_print_kind_t kind) {
  (void)kind;
  Screen_obj_t* self = MP_OBJ_TO_PTR(self_in);
  mp_print_str(print, "Screen( extent(");
  mp_obj_print_helper(print, mp_obj_new_int(self->screen->width), PRINT_REPR);
  mp_print_str(print, ", ");
  mp_obj_print_helper(print, mp_obj_new_int(self->screen->height), PRINT_REPR);
  mp_print_str(print, "), location(");
  mp_obj_print_helper(print, mp_obj_new_int(self->screen->lu), PRINT_REPR);
  mp_print_str(print, ", ");
  mp_obj_print_helper(print, mp_obj_new_int(self->screen->lv), PRINT_REPR);
  mp_print_str(print, "), corners((");
  mp_obj_print_helper(print, mp_obj_new_int(self->screen->u0), PRINT_REPR);
  mp_print_str(print, ", ");
  mp_obj_print_helper(print, mp_obj_new_int(self->screen->v0), PRINT_REPR);
  mp_print_str(print, "), (");
  mp_obj_print_helper(print, mp_obj_new_int(self->screen->u1), PRINT_REPR);
  mp_print_str(print, ", ");
  mp_obj_print_helper(print, mp_obj_new_int(self->screen->v1), PRINT_REPR);
  mp_print_str(print, "))");
}

/**
 * @brief Create a new Screen_obj_t.
 * May either act as an instance or a reference.
 *
 * @param reference if this argument is provided the screen will act as a
 * reference
 * @return mp_obj_t
 */
mp_obj_t mp_obj_new_screen_reference(screen_t* reference) {
  Screen_obj_t* self = m_new_obj(Screen_obj_t);
  self->base.type = &Screen_type;
  self->screen = &self->_screen;
  self->_is_reference = false;
  if (NULL != reference) {
    self->screen = reference;
    self->_is_reference = true;
  }
  return MP_OBJ_FROM_PTR(self);
}

mp_obj_t mp_obj_new_screen(void) { return mp_obj_new_screen_reference(NULL); }

STATIC mp_obj_t make_new(
    const mp_obj_type_t* type, size_t n_args, size_t n_kw,
    const mp_obj_t* all_args) {
  // parse args
  enum {
    ARG_extent,
    ARG_location,
  };
  static const mp_arg_t allowed_args[] = {
      {MP_QSTR_extent, MP_ARG_REQUIRED | MP_ARG_OBJ, {.u_obj = NULL}},
      {MP_QSTR_location, MP_ARG_OBJ, {.u_obj = NULL}},
  };
  mp_map_t kw_args;
  mp_map_init_fixed_table(&kw_args, n_kw, all_args + n_args);
  mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
  mp_arg_parse_all_kw_array(
      n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

  // create instance object
  mp_obj_t self = mp_obj_new_screen();

  // set initial values
  set_extent(self, args[ARG_extent].u_obj);
  if (NULL != args[ARG_location].u_obj) {
    set_location(self, args[ARG_location].u_obj);
  }

  return self;
}

STATIC void attr(mp_obj_t self_in, qstr attribute, mp_obj_t* destination) {
  switch (attribute) {
    case MP_QSTR_width:
      destination[0] = get_width(self_in);
      break;

    case MP_QSTR_height:
      destination[0] = get_height(self_in);
      break;

    case MP_QSTR_pixels:
      destination[0] = get_pixels(self_in);
      break;

    default:
      // No attribute found, continue lookup in locals dict.
      // https://github.com/micropython/micropython/pull/7934
      destination[1] = MP_OBJ_SENTINEL;
      break;
  }
}

MP_DEFINE_CONST_OBJ_TYPE(
  Screen_type,
  MP_QSTR_Screen,
  MP_TYPE_FLAG_NONE,
  make_new, make_new,
  print, print,
  attr, attr,
  locals_dict, &locals_dict
);
