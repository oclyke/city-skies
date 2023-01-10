#include "sicgl/compose.h"

#include <errno.h>

#include "pysicgl/drawing/blit.h"
#include "pysicgl/interface.h"
#include "pysicgl/screen.h"
#include "pysicgl/utilities.h"

static inline color_t clamp_u8(color_t channel) {
  if (channel > 255) {
    return 255;
  } else if (channel < 0) {
    return 0;
  } else {
    return channel;
  }
}

static void compositor_set(color_t* source, color_t* dest, size_t width) {
    memcpy(dest, source, width * bytes_per_pixel());
}

static void compositor_add_clamped(color_t* source, color_t* dest, size_t width) {
  for (size_t idx = 0; idx < width; idx++) {
    dest[idx] = color_from_channels(
        clamp_u8(color_channel_red(dest[idx]) + color_channel_red(source[idx])),
        clamp_u8(color_channel_green(dest[idx]) + color_channel_green(source[idx])),
        clamp_u8(color_channel_blue(dest[idx]) + color_channel_blue(source[idx])));
  }
}

static void compositor_subtract_clamped(color_t* source, color_t* dest, size_t width) {
  for (size_t idx = 0; idx < width; idx++) {
  dest[idx] = color_from_channels(
      clamp_u8(color_channel_red(dest[idx]) - color_channel_red(source[idx])),
      clamp_u8(color_channel_green(dest[idx]) - color_channel_green(source[idx])),
      clamp_u8(color_channel_blue(dest[idx]) - color_channel_blue(source[idx])));
  }
}

static void compositor_multiply_clamped(color_t* source, color_t* dest, size_t width) {
  for (size_t idx = 0; idx < width; idx++) {
  dest[idx] = color_from_channels(
      clamp_u8(color_channel_red(dest[idx]) * color_channel_red(source[idx])),
      clamp_u8(color_channel_green(dest[idx]) * color_channel_green(source[idx])),
      clamp_u8(color_channel_blue(dest[idx]) * color_channel_blue(source[idx])));
  }
}

static void compositor_AND(color_t* source, color_t* dest, size_t width) {
  for (size_t idx = 0; idx < width; idx++) {
  dest[idx] = color_from_channels(
      color_channel_red(dest[idx]) & color_channel_red(source[idx]),
      color_channel_green(dest[idx]) & color_channel_green(source[idx]),
      color_channel_blue(dest[idx]) & color_channel_blue(source[idx]));
  }
}

static void compositor_OR(color_t* source, color_t* dest, size_t width) {
  for (size_t idx = 0; idx < width; idx++) {
  dest[idx] = color_from_channels(
      color_channel_red(dest[idx]) | color_channel_red(source[idx]),
      color_channel_green(dest[idx]) | color_channel_green(source[idx]),
      color_channel_blue(dest[idx]) | color_channel_blue(source[idx]));
  }
}

static void compositor_XOR(color_t* source, color_t* dest, size_t width) {
  for (size_t idx = 0; idx < width; idx++) {
  dest[idx] = color_from_channels(
      color_channel_red(dest[idx]) ^ color_channel_red(source[idx]),
      color_channel_green(dest[idx]) ^ color_channel_green(source[idx]),
      color_channel_blue(dest[idx]) ^ color_channel_blue(source[idx]));
  }
}

mp_obj_t compose(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_screen,
    ARG_sprite,
    ARG_mode,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  Screen_obj_t* screen = screen_from_obj(args[ARG_screen]);
  mp_buffer_info_t sprite_info;
  mp_get_buffer_raise(args[ARG_sprite], &sprite_info, MP_BUFFER_READ);
  mp_int_t mode = mp_obj_get_int(args[ARG_mode]);

  compositor_fn compositor = NULL;
  switch (mode) {
    case 0:
      compositor = compositor_set;
      break;

    case 1:
      compositor = compositor_add_clamped;
      break;

    case 2:
      compositor = compositor_subtract_clamped;
      break;

    case 3:
      compositor = compositor_multiply_clamped;
      break;

    case 4:
      compositor = compositor_AND;
      break;

    case 5:
      compositor = compositor_OR;
      break;

    case 6:
      compositor = compositor_XOR;
      break;

    default:
      mp_raise_ValueError(NULL);
      break;
  }

  int ret = sicgl_compose(
      &self->interface, screen->screen, sprite_info.buf, compositor);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}
