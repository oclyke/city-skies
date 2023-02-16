#include "sicgl/compose.h"

#include <errno.h>

#include "py/obj.h"
#include "py/runtime.h"
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

static void compositor_set(
    color_t* source, color_t* dest, size_t width, void* args) {
  memcpy(dest, source, width * bytes_per_pixel());
}

static void compositor_add_clamped(
    color_t* source, color_t* dest, size_t width, void* args) {
  for (size_t idx = 0; idx < width; idx++) {
    dest[idx] = color_from_channels(
        clamp_u8(color_channel_red(dest[idx]) + color_channel_red(source[idx])),
        clamp_u8(
            color_channel_green(dest[idx]) + color_channel_green(source[idx])),
        clamp_u8(
            color_channel_blue(dest[idx]) + color_channel_blue(source[idx])),
        clamp_u8(
            color_channel_alpha(dest[idx]) + color_channel_alpha(source[idx])));
  }
}

static void compositor_subtract_clamped(
    color_t* source, color_t* dest, size_t width, void* args) {
  for (size_t idx = 0; idx < width; idx++) {
    dest[idx] = color_from_channels(
        clamp_u8(color_channel_red(dest[idx]) - color_channel_red(source[idx])),
        clamp_u8(
            color_channel_green(dest[idx]) - color_channel_green(source[idx])),
        clamp_u8(
            color_channel_blue(dest[idx]) - color_channel_blue(source[idx])),
        clamp_u8(
            color_channel_alpha(dest[idx]) - color_channel_alpha(source[idx])));
  }
}

static void compositor_multiply_clamped(
    color_t* source, color_t* dest, size_t width, void* args) {
  for (size_t idx = 0; idx < width; idx++) {
    dest[idx] = color_from_channels(
        clamp_u8(color_channel_red(dest[idx]) * color_channel_red(source[idx])),
        clamp_u8(
            color_channel_green(dest[idx]) * color_channel_green(source[idx])),
        clamp_u8(
            color_channel_blue(dest[idx]) * color_channel_blue(source[idx])),
        clamp_u8(
            color_channel_alpha(dest[idx]) * color_channel_alpha(source[idx])));
  }
}

static void compositor_AND(
    color_t* source, color_t* dest, size_t width, void* args) {
  for (size_t idx = 0; idx < width; idx++) {
    dest[idx] = color_from_channels(
        color_channel_red(dest[idx]) & color_channel_red(source[idx]),
        color_channel_green(dest[idx]) & color_channel_green(source[idx]),
        color_channel_blue(dest[idx]) & color_channel_blue(source[idx]),
        color_channel_alpha(dest[idx]) & color_channel_alpha(source[idx]));
  }
}

static void compositor_OR(
    color_t* source, color_t* dest, size_t width, void* args) {
  for (size_t idx = 0; idx < width; idx++) {
    dest[idx] = color_from_channels(
        color_channel_red(dest[idx]) | color_channel_red(source[idx]),
        color_channel_green(dest[idx]) | color_channel_green(source[idx]),
        color_channel_blue(dest[idx]) | color_channel_blue(source[idx]),
        color_channel_alpha(dest[idx]) | color_channel_alpha(source[idx]));
  }
}

static void compositor_XOR(
    color_t* source, color_t* dest, size_t width, void* args) {
  for (size_t idx = 0; idx < width; idx++) {
    dest[idx] = color_from_channels(
        color_channel_red(dest[idx]) ^ color_channel_red(source[idx]),
        color_channel_green(dest[idx]) ^ color_channel_green(source[idx]),
        color_channel_blue(dest[idx]) ^ color_channel_blue(source[idx]),
        color_channel_alpha(dest[idx]) ^ color_channel_alpha(source[idx]));
  }
}

typedef struct _compositor_function_entry_t {
  mp_obj_t name;
  compositor_fn compositor;
} compositor_function_entry_t;

STATIC const compositor_function_entry_t compositor_function_types_table[] = {
    {MP_ROM_QSTR(MP_QSTR_set), compositor_set},
    {MP_ROM_QSTR(MP_QSTR_add), compositor_add_clamped},
    {MP_ROM_QSTR(MP_QSTR_subtract), compositor_subtract_clamped},
    {MP_ROM_QSTR(MP_QSTR_multiply), compositor_multiply_clamped},
    {MP_ROM_QSTR(MP_QSTR_AND), compositor_AND},
    {MP_ROM_QSTR(MP_QSTR_OR), compositor_OR},
    {MP_ROM_QSTR(MP_QSTR_XOR), compositor_XOR},
};
STATIC const size_t NUM_COMPOSITOR_FUNCTION_TYPES =
    sizeof(compositor_function_types_table) /
    sizeof(compositor_function_entry_t);
STATIC int find_compositor_function_type_entry_index(
    mp_obj_t name, size_t* index) {
  int ret = 0;
  if (NULL == index) {
    ret = -EINVAL;
    goto out;
  }

  // try to find the corresponding map for this type
  for (size_t idx = 0; idx < NUM_COMPOSITOR_FUNCTION_TYPES; idx++) {
    if (compositor_function_types_table[idx].name == name) {
      *index = idx;
      goto out;
    }
  }

  ret = -ENOENT;

out:
  return ret;
}

mp_obj_t get_composition_types() {
  mp_obj_t dict = mp_obj_new_dict(NUM_COMPOSITOR_FUNCTION_TYPES);
  for (size_t idx = 0; idx < NUM_COMPOSITOR_FUNCTION_TYPES; idx++) {
    mp_obj_dict_store(
        dict, compositor_function_types_table[idx].name, mp_obj_new_int(idx));
  }
  return dict;
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

  // check bounds of mode
  if ((mode >= NUM_COMPOSITOR_FUNCTION_TYPES) || (mode < 0)) {
    mp_raise_ValueError(NULL);
  }

  // get the compositor function and args for this mode
  compositor_fn compositor = compositor_function_types_table[mode].compositor;
  void* compositor_args = NULL;

  // compose the given screen onto the interface
  int ret = sicgl_compose(
      &self->interface, screen->screen, sprite_info.buf, compositor,
      compositor_args);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}
