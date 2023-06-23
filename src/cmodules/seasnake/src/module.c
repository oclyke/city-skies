#include "py/runtime.h"
#include "sicgl/color.h"

#include <errno.h>
#include <string.h>

STATIC mp_obj_t map_simple(size_t n_args, const mp_obj_t* args) {
  enum {
    ARG_input,
    ARG_output,
    ARG_width,
    ARG_reverse_first,
  };

  mp_buffer_info_t input;
  mp_buffer_info_t output;
  mp_get_buffer_raise(args[ARG_input], &input, MP_BUFFER_READ);
  mp_get_buffer_raise(args[ARG_output], &output, MP_BUFFER_WRITE);

  bool reverse_first = mp_obj_is_true(args[ARG_reverse_first]);
  mp_int_t width = mp_obj_get_int(args[ARG_width]);

  if (width <= 0) {
    mp_raise_ValueError(NULL);
  }

  size_t bpp = bytes_per_pixel();
  size_t pixels = output.len / bpp;
  size_t input_pixels = input.len / bpp;
  if (input_pixels < pixels) {
    pixels = input_pixels;
  }

  // compute maximum full rows to handle.
  // any remaining pixels will not be considered.
  size_t max_rows = pixels / width;

  // make color_t pointers for easier math
  color_t* colors_in = (color_t*)input.buf;
  color_t* colors_out = (color_t*)output.buf;

  // copy the non-reversed rows
  for (size_t rdx = (reverse_first) ? 1 : 0; rdx < max_rows; rdx += 2) {
    memcpy(&colors_out[rdx * width], &colors_in[rdx * width], width * bpp);
  }

  // copy the reversed rows
  for (size_t rdx = (reverse_first) ? 0 : 1; rdx < max_rows; rdx += 2) {
    for (size_t idx = 0; idx < width; idx++) {
      colors_out[rdx * width + idx] = colors_in[rdx * width + width - idx - 1];
    }
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(map_simple_obj, 4, 4, map_simple);

STATIC const mp_rom_map_elem_t globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_seasnake)},
    {MP_OBJ_NEW_QSTR(MP_QSTR_map_simple), (mp_obj_t)&map_simple_obj},
};
STATIC MP_DEFINE_CONST_DICT(globals, globals_table);

const mp_obj_module_t seasnake_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_seasnake, seasnake_module);
