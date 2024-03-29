#include "py/runtime.h"
#include "pysicgl/interface.h"
#include "sicgl/color.h"

#include <errno.h>

// signifying 'pattern at bit' for ws2812b leds driving bits with SPI @ 2.5 MHz
// (0: [1h, 2l] 1: [2h, 1l])
STATIC inline uint8_t pat_ws2812b(uint8_t b, uint8_t i) {
  const uint8_t p0 = 0b100;
  const uint8_t p1 = 0b110;
  return (b & (0x80 >> i)) ? p1 : p0;
}

STATIC inline void expand_byte_into_bitstream(uint8_t b, uint8_t* output) {
    output[0] = (pat_ws2812b(b, 0) << 5) | (pat_ws2812b(b, 1) << 2) | (pat_ws2812b(b, 2) >> 1);
    output[1] = (pat_ws2812b(b, 2) << 7) | (pat_ws2812b(b, 3) << 4) | (pat_ws2812b(b, 4) << 1) | (pat_ws2812b(b, 5) >> 2);
    output[2] = (pat_ws2812b(b, 5) << 6) | (pat_ws2812b(b, 6) << 3) | (pat_ws2812b(b, 7) << 0);
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

  // each input byte expands into 3 output bytes and
  // each pixel is represented by three bytes
  const size_t expansion_factor = 3 * 3;

  // determine how many pixels to process
  size_t bpp = bytes_per_pixel();
  size_t memory_pixels = memory_info.len / bpp;
  size_t pixels = output_info.len / expansion_factor; 
  if (memory_pixels < pixels) {
    pixels = memory_pixels;
  }

  // expand the input bytes into the output bitstream
  uint8_t* pout = (uint8_t*)output_info.buf;
  for (size_t idx = 0; idx < pixels; idx++) {
    // ws2812b order is GRB
    color_t color = memory[idx];
    expand_byte_into_bitstream(color_channel_green(color), &pout[(expansion_factor * idx) + 0]);
    expand_byte_into_bitstream(color_channel_red(color), &pout[(expansion_factor * idx) + 3]);
    expand_byte_into_bitstream(color_channel_blue(color), &pout[(expansion_factor * idx) + 6]);
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(sicgl_memory_to_spi_bitstream_obj, sicgl_memory_to_spi_bitstream);

STATIC const mp_rom_map_elem_t globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_ws2812b_utils)},
    {MP_OBJ_NEW_QSTR(MP_QSTR_sicgl_memory_to_spi_bitstream), (mp_obj_t)&sicgl_memory_to_spi_bitstream_obj},
};
STATIC MP_DEFINE_CONST_DICT(globals, globals_table);

const mp_obj_module_t ws2812b_utils_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_ws2812b_utils, ws2812b_utils_module);
