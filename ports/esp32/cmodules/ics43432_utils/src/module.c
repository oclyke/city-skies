#include "py/runtime.h"
#include "buffer/float.h"

STATIC mp_obj_t bytes_to_float_buffer(mp_obj_t in_buf, mp_obj_t out_float_buffer) {
  FloatBuffer_obj_t* out_buffer = float_buffer_from_obj(out_float_buffer);

  mp_buffer_info_t in;
  mp_get_buffer_raise(in_buf, &in, MP_BUFFER_READ);
  const uint8_t* pin = (const uint8_t*)in.buf;

  // there are 4 bps in the input buffer
  uint8_t bps = 4;
  size_t buf_samples = in.len / bps;

  size_t total_samples = buf_samples;
  if (total_samples > out_buffer->length) {
    total_samples = out_buffer->length;

    // raise an exception to indicate length mismatch to user
    // (program could continue, but )
    mp_raise_TypeError(NULL);
  }

  // buffer format is determined by micropython i2s driver transformations
  /* (python)
      # # GOLDEN CODE #
      # b0 = buf[bps*idx + 1]
      # b1 = buf[bps*idx + 2]
      # b2 = buf[bps*idx + 3]
      # b3 = 0xff if b2 & 0x80 else 0x00
      # x = (b3 << 24) | (b2 << 16) | (b1 << 8) | (b0 << 0)
      # if x > 0x7fffffff:
      #   x = x - 4294967296
      # print(x)
      # # GOLDEN CODE #
  */
  for (size_t idx = 0; idx < total_samples; idx++) {
    uint8_t b0 = pin[bps * idx + 1];
    uint8_t b1 = pin[bps * idx + 2];
    uint8_t b2 = pin[bps * idx + 3];
    uint8_t b3 = (b2 & 0x80) ? 0xff : 0x00;

    int32_t sample = (((uint32_t)b3) << 24) | (((uint32_t)b2) << 16) |
                     (((uint32_t)b1) << 8) | (((uint32_t)b0) << 0);

    out_buffer->elements[idx] = (float)sample;
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(bytes_to_float_buffer_obj, bytes_to_float_buffer);

STATIC const mp_rom_map_elem_t module_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_ics43432)},
    {MP_OBJ_NEW_QSTR(MP_QSTR_bytes_to_float_buffer), (mp_obj_t)&bytes_to_float_buffer_obj},
};
STATIC MP_DEFINE_CONST_DICT(module_globals, module_globals_table);

const mp_obj_module_t ics43432_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&module_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_ics43432, ics43432_module);
