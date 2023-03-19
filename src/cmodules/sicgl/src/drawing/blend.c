#include "sicgl/blend.h"

#include <errno.h>

#include "py/obj.h"
#include "py/runtime.h"
#include "pysicgl/drawing/blit.h"
#include "pysicgl/interface.h"
#include "pysicgl/screen.h"
#include "pysicgl/utilities.h"
#include "sicgl/blenders.h"

typedef struct _blender_function_entry_t {
  mp_obj_t name;
  blender_fn blender;
} blender_function_entry_t;

STATIC const blender_function_entry_t blender_function_types_table[] = {
    {MP_ROM_QSTR(MP_QSTR_normal), blend_normal},
    {MP_ROM_QSTR(MP_QSTR_forget), blend_forget},
    {MP_ROM_QSTR(MP_QSTR_multiply), blend_multiply},
    {MP_ROM_QSTR(MP_QSTR_screen), blend_screen},
    {MP_ROM_QSTR(MP_QSTR_overlay), blend_overlay},
    {MP_ROM_QSTR(MP_QSTR_darken), blend_darken},
    {MP_ROM_QSTR(MP_QSTR_lighten), blend_lighten},
    {MP_ROM_QSTR(MP_QSTR_color_dodge), blend_color_dodge},
    {MP_ROM_QSTR(MP_QSTR_color_burn), blend_color_burn},
    {MP_ROM_QSTR(MP_QSTR_hard_light), blend_hard_light},
    {MP_ROM_QSTR(MP_QSTR_difference), blend_difference},
    {MP_ROM_QSTR(MP_QSTR_exclusion), blend_exclusion},
};
STATIC const size_t NUM_COMPOSITOR_FUNCTION_TYPES =
    sizeof(blender_function_types_table) / sizeof(blender_function_entry_t);
STATIC int find_blender_function_type_entry_index(
    mp_obj_t name, size_t* index) {
  int ret = 0;
  if (NULL == index) {
    ret = -EINVAL;
    goto out;
  }

  // try to find the corresponding map for this type
  for (size_t idx = 0; idx < NUM_COMPOSITOR_FUNCTION_TYPES; idx++) {
    if (blender_function_types_table[idx].name == name) {
      *index = idx;
      goto out;
    }
  }

  ret = -ENOENT;

out:
  return ret;
}

mp_obj_t get_blending_types() {
  mp_obj_t dict = mp_obj_new_dict(NUM_COMPOSITOR_FUNCTION_TYPES);
  for (size_t idx = 0; idx < NUM_COMPOSITOR_FUNCTION_TYPES; idx++) {
    mp_obj_dict_store(
        dict, blender_function_types_table[idx].name, mp_obj_new_int(idx));
  }
  return dict;
}

mp_obj_t blend(size_t n_args, const mp_obj_t* args) {
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
  blender_fn blender = blender_function_types_table[mode].blender;
  void* blender_args = NULL;

  // compose the given screen onto the interface
  int ret = sicgl_blend(
      &self->interface, screen->screen, sprite_info.buf, blender, blender_args);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}
