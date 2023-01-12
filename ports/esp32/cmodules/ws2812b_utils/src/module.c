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

STATIC mp_obj_t sicgl_interface_to_spi_bitstream(mp_obj_t interface_obj, mp_obj_t output) {
  mp_buffer_info_t out;
  mp_get_buffer_raise(output, &out, MP_BUFFER_WRITE);
  Interface_obj_t* interface = interface_from_obj(interface_obj);

  color_t* memory = interface->interface.memory;
  if (NULL == memory) {
    mp_raise_OSError(-ENOMEM);
  }

  // each input byte expands into 3 output bytes and
  // each pixel is represented by three bytes
  const size_t expansion_factor = 3 * 3;

  // determine how many pixels to process
  size_t interface_pixels = interface->interface.length;
  size_t pixels = out.len / expansion_factor; 
  if (interface_pixels < pixels) {
    pixels = interface_pixels;
  }

  // expand the input bytes into the output bitstream
  uint8_t* pout = (uint8_t*)out.buf;
  for (size_t idx = 0; idx < pixels; idx++) {
    // ws2812b order is GRB
    color_t color = memory[idx];
    expand_byte_into_bitstream(color_channel_green(color), &pout[(expansion_factor * idx) + 0]);
    expand_byte_into_bitstream(color_channel_red(color), &pout[(expansion_factor * idx) + 3]);
    expand_byte_into_bitstream(color_channel_blue(color), &pout[(expansion_factor * idx) + 6]);
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(sicgl_interface_to_spi_bitstream_obj, sicgl_interface_to_spi_bitstream);

// STATIC mp_obj_t transform_ws2812b(mp_obj_t in_buf, mp_obj_t out_buf) {
//   mp_buffer_info_t in;
//   mp_buffer_info_t out;
//   mp_get_buffer_raise(in_buf, &in, MP_BUFFER_READ);
//   mp_get_buffer_raise(out_buf, &out, MP_BUFFER_WRITE);

//   const uint8_t bpb = 3;  // only works for bpb == 3

//   if (out.len != bpb * in.len) {
//     mp_raise_msg(&mp_type_ValueError, MP_ERROR_TEXT("out.len != bpp*in.len"));
//     return mp_const_none;
//   }
//   if (bpb != 3) {
//     mp_raise_msg(&mp_type_ValueError, MP_ERROR_TEXT("bpp != 3"));
//     return mp_const_none;
//   }

//   uint8_t* pin = (uint8_t*)in.buf;
//   uint8_t* pout = (uint8_t*)out.buf;

//   // re-order channels (per WS2812B datasheet, the expexted order is GRB but the
//   // input to this function is RGB)
//   const uint8_t bpp = 3;  // bytes per pixel of the input... this used to be a
//                           // nice function that could accept any length input
//                           // array but now it must be a multiple of bpp
//   if (in.len % bpp) {
//     mp_raise_TypeError(MP_ERROR_TEXT("input len must be a multiple of bpp!"));
//   }
//   for (size_t idx = 0; idx < in.len / bpp; idx++) {
//     uint8_t tmp = pin[bpp * idx + 0];         // store index 0
//     pin[bpp * idx + 0] = pin[bpp * idx + 1];  // move index 1 into index 0
//     pin[bpp * idx + 1] = tmp;  // store tmp (index 0) into index 1
//   }

//   for (size_t idx = 0; idx < in.len; idx++) {
//     uint8_t b = pin[idx];
//     pout[bpb * idx + 0] = (pat_ws2812b(b, 0) << 5) | (pat_ws2812b(b, 1) << 2) |
//                           (pat_ws2812b(b, 2) >> 1);
//     pout[bpb * idx + 1] = (pat_ws2812b(b, 2) << 7) | (pat_ws2812b(b, 3) << 4) |
//                           (pat_ws2812b(b, 4) << 1) | (pat_ws2812b(b, 5) >> 2);
//     pout[bpb * idx + 2] = (pat_ws2812b(b, 5) << 6) | (pat_ws2812b(b, 6) << 3) |
//                           (pat_ws2812b(b, 7) << 0);
//   }

//   return mp_const_none;
// }
// MP_DEFINE_CONST_FUN_OBJ_2(transform_ws2812b_obj, transform_ws2812b);

STATIC const mp_rom_map_elem_t globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_ws2812b_utils)},
    {MP_OBJ_NEW_QSTR(MP_QSTR_sicgl_interface_to_spi_bitstream), (mp_obj_t)&sicgl_interface_to_spi_bitstream_obj},

    
    // {MP_OBJ_NEW_QSTR(MP_QSTR_xform_rgb), (mp_obj_t)&transform_ws2812b_obj},
};
STATIC MP_DEFINE_CONST_DICT(globals, globals_table);

const mp_obj_module_t ws2812b_utils_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_ws2812b_utils, ws2812b_utils_module);
