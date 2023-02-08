#include <stdio.h>
#include <stdlib.h>

#include "py/binary.h"
#include "py/objarray.h"
#include "py/runtime.h"
#include "pysicgl.h"
#include "pysicgl/color_sequence.h"
#include "pysicgl/field.h"
#include "pysicgl/interface.h"
#include "pysicgl/screen.h"
#include "sicgl/gamma.h"

// module methods
STATIC mp_obj_t allocate_pixel_memory(mp_obj_t obj) {
  // allocate memory
  // the amount of memory allocated is determined according to the type of the
  // argument
  size_t pixels = 0;
  if (mp_obj_is_int(obj)) {
    // allocate the specified number of pixels
    mp_int_t desired = mp_obj_get_int(obj);
    if (desired <= 0) {
      mp_raise_ValueError(NULL);
    }
    pixels = desired;
  } else {
    mp_raise_TypeError(NULL);
  }

  // allocate memory
  // not sure if this could be a memory leak... will the memory be freed when
  // the bytearray is collected?
  size_t bpp = bytes_per_pixel();
  size_t len = pixels * bpp;
  void* mem = m_malloc(len);
  memset(mem, 0, len);
  return mp_obj_new_bytearray_by_ref(len, mem);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(
    allocate_pixel_memory_obj, allocate_pixel_memory);

STATIC mp_obj_t
gamma_correct(mp_obj_t input_interface, mp_obj_t output_interface) {
  Interface_obj_t* input = interface_from_obj(input_interface);
  Interface_obj_t* output = interface_from_obj(output_interface);

  int ret = sicgl_gamma_correct(&input->interface, &output->interface);
  if (0 != ret) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(gamma_correct_obj, gamma_correct);

STATIC mp_obj_t make_color(size_t n_args, const mp_obj_t* args) {
  enum {
    ARG_red,
    ARG_green,
    ARG_blue,
    ARG_alpha,
  };
  color_t color = color_from_channels(
      mp_obj_get_int(args[ARG_red]),
      mp_obj_get_int(args[ARG_green]),
      mp_obj_get_int(args[ARG_blue]),
      mp_obj_get_int(args[ARG_alpha]));
  return mp_obj_new_int(color);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(make_color_obj, 4, 4, make_color);

STATIC mp_obj_t get_color_channels(mp_obj_t color_obj) {
  color_t color = mp_obj_get_int(color_obj);

  // return the maximum value to allow for scaling
  const size_t num_items = 3;
  mp_obj_t items[num_items];

  items[0] = mp_obj_new_int(color_channel_red(color));
  items[1] = mp_obj_new_int(color_channel_green(color));
  items[2] = mp_obj_new_int(color_channel_blue(color));

  return mp_obj_new_tuple(num_items, items);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(get_color_channels_obj, get_color_channels);

// module
STATIC const mp_map_elem_t pysicgl_globals_table[] = {
    {MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_sicgl)},

    // methods
    {MP_OBJ_NEW_QSTR(MP_QSTR_allocate_pixel_memory),
     (mp_obj_t)MP_ROM_PTR(&allocate_pixel_memory_obj)},
    {MP_OBJ_NEW_QSTR(MP_QSTR_gamma_correct),
     (mp_obj_t)MP_ROM_PTR(&gamma_correct_obj)},
    {MP_OBJ_NEW_QSTR(MP_QSTR_make_color),
     (mp_obj_t)MP_ROM_PTR(&make_color_obj)},
    {MP_OBJ_NEW_QSTR(MP_QSTR_get_color_channels),
     (mp_obj_t)MP_ROM_PTR(&get_color_channels_obj)},

    // classes
    {MP_OBJ_NEW_QSTR(MP_QSTR_ColorSequence), (mp_obj_t)&ColorSequence_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_Screen), (mp_obj_t)&Screen_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_Interface), (mp_obj_t)&Interface_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_ScalarField), (mp_obj_t)&ScalarField_type},
};
STATIC MP_DEFINE_CONST_DICT(pysicgl_globals, pysicgl_globals_table);

const mp_obj_module_t pysicgl_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&pysicgl_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_pysicgl, pysicgl_module);
