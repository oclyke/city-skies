#include "py/runtime.h"
#include "pysicgl/interface.h"
#include "sicgl/color.h"

#include <errno.h>

STATIC inline void expand_color_into_bitstream(color_t color, uint8_t* output) {
    output[0] = 0xff;
    output[1] = color_channel_blue(color);
    output[2] = color_channel_green(color);
    output[3] = color_channel_red(color);
}

/**
 * @brief Converts sicgl memory (color_t buffer) containing 'pixels' pixels into an output
 * bitstream compatible with driving WS2812B LEDs at 2.5 MHz.
 * 
 * @param memory_obj 
 * @param output_obj 
 * @return STATIC 
 */
STATIC mp_obj_t sicgl_memory_to_spi_bitstream(mp_obj_t memory_obj, mp_obj_t output_obj) {
  mp_buffer_info_t memory_info;
  mp_buffer_info_t output_info;
  mp_get_buffer_raise(memory_obj, &memory_info, MP_BUFFER_READ);
  mp_get_buffer_raise(output_obj, &output_info, MP_BUFFER_WRITE);

  color_t* memory = (color_t*)memory_info.buf;
  if (NULL == memory) {
    mp_raise_OSError(-ENOMEM);
  }

  // apa102 leds use 4 bytes per pixel
  const size_t apa102_bpp = 4;

  // determine how many pixels to process
  size_t bpp = bytes_per_pixel();
  size_t memory_pixels = memory_info.len / bpp;
  size_t pixels = output_info.len / apa102_bpp; 
  if (memory_pixels < pixels) {
    pixels = memory_pixels;
  }

  // expand the input bytes into the output bitstream
  uint8_t* pout = (uint8_t*)output_info.buf;
  for (size_t idx = 0; idx < pixels; idx++) {
    expand_color_into_bitstream(memory[idx], &pout[idx * apa102_bpp]);
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(sicgl_memory_to_spi_bitstream_obj, sicgl_memory_to_spi_bitstream);

STATIC const mp_rom_map_elem_t globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_apa102_utils)},
    {MP_OBJ_NEW_QSTR(MP_QSTR_sicgl_memory_to_spi_bitstream), (mp_obj_t)&sicgl_memory_to_spi_bitstream_obj},
};
STATIC MP_DEFINE_CONST_DICT(globals, globals_table);

const mp_obj_module_t apa102_utils_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_apa102_utils, apa102_utils_module);
