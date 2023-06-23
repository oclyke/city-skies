#include <errno.h>

#include "py/runtime.h"

STATIC mp_obj_t stride_copy(size_t n_args, const mp_obj_t* args) {
  enum {
    ARG_input,
    ARG_output,
    ARG_strideIn,
    ARG_strideOut,
  };

  mp_buffer_info_t input_info;
  mp_buffer_info_t output_info;
  mp_get_buffer_raise(args[ARG_input], &input_info, MP_BUFFER_READ);
  mp_get_buffer_raise(args[ARG_output], &output_info, MP_BUFFER_WRITE);

  uint8_t* input = (uint8_t*)input_info.buf;
  if (NULL == input) {
    mp_raise_OSError(-ENOMEM);
  }
  uint8_t* output = (uint8_t*)output_info.buf;
  if (NULL == output) {
    mp_raise_OSError(-ENOMEM);
  }

  // get the stride amounts
  size_t strideIn = mp_obj_get_int(args[ARG_strideIn]);
  size_t strideOut = mp_obj_get_int(args[ARG_strideOut]);

  size_t inChunks = input_info.len / strideIn;
  size_t outChunks = output_info.len / strideOut;

  // determine how many chunks to process
  size_t chunks = outChunks;
  if (inChunks < outChunks) {
    chunks = inChunks;
  }

  // expand chunks into one another
  for (size_t idx = 0; idx < chunks; idx++) {
    uint8_t* in = &input[strideIn * idx];
    uint8_t* out = &output[strideOut * idx];
    for (size_t jdx = 0; jdx < strideOut; jdx++) {
      out[jdx] = in[jdx];
    }
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(stride_copy_obj, 4, 4, stride_copy);

STATIC const mp_rom_map_elem_t globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_transform)},
    {MP_OBJ_NEW_QSTR(MP_QSTR_stride_copy), (mp_obj_t)&stride_copy_obj},
};
STATIC MP_DEFINE_CONST_DICT(globals, globals_table);

const mp_obj_module_t transform_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_transform, transform_module);
