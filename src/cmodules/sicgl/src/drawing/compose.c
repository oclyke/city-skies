#include "sicgl/compose.h"

#include <errno.h>

#include "py/obj.h"
#include "py/runtime.h"
#include "pysicgl/drawing/blit.h"
#include "pysicgl/interface.h"
#include "pysicgl/screen.h"
#include "pysicgl/utilities.h"
#include "sicgl/compositors.h"

typedef struct _compositor_function_entry_t {
  mp_obj_t name;
  compositor_fn compositor;
} compositor_function_entry_t;

STATIC const compositor_function_entry_t compositor_function_types_table[] = {
    {MP_ROM_QSTR(MP_QSTR_direct_none), compositor_direct_none},
    {MP_ROM_QSTR(MP_QSTR_direct_clear), compositor_direct_clear},
    {MP_ROM_QSTR(MP_QSTR_direct_set), compositor_direct_set},

    {MP_ROM_QSTR(MP_QSTR_bitwise_and), compositor_bitwise_and},
    {MP_ROM_QSTR(MP_QSTR_bitwise_or), compositor_bitwise_or},
    {MP_ROM_QSTR(MP_QSTR_bitwise_xor), compositor_bitwise_xor},
    {MP_ROM_QSTR(MP_QSTR_bitwise_nand), compositor_bitwise_nand},
    {MP_ROM_QSTR(MP_QSTR_bitwise_nor), compositor_bitwise_nor},
    {MP_ROM_QSTR(MP_QSTR_bitwise_xnor), compositor_bitwise_xnor},

    {MP_ROM_QSTR(MP_QSTR_channelwise_min), compositor_channelwise_min},
    {MP_ROM_QSTR(MP_QSTR_channelwise_max), compositor_channelwise_max},
    {MP_ROM_QSTR(MP_QSTR_channelwise_sum), compositor_channelwise_sum},
    {MP_ROM_QSTR(MP_QSTR_channelwise_diff), compositor_channelwise_diff},
    {MP_ROM_QSTR(MP_QSTR_channelwise_diff_reverse),
     compositor_channelwise_diff_reverse},
    {MP_ROM_QSTR(MP_QSTR_channelwise_multiply),
     compositor_channelwise_multiply},
    {MP_ROM_QSTR(MP_QSTR_channelwise_divide), compositor_channelwise_divide},
    {MP_ROM_QSTR(MP_QSTR_channelwise_divide_reverse),
     compositor_channelwise_divide_reverse},
    {MP_ROM_QSTR(MP_QSTR_channelwise_sum_clamped),
     compositor_channelwise_sum_clamped},
    {MP_ROM_QSTR(MP_QSTR_channelwise_diff_clamped),
     compositor_channelwise_diff_clamped},
    {MP_ROM_QSTR(MP_QSTR_channelwise_diff_reverse_clamped),
     compositor_channelwise_diff_reverse_clamped},
    {MP_ROM_QSTR(MP_QSTR_channelwise_multiply_clamped),
     compositor_channelwise_multiply_clamped},
    {MP_ROM_QSTR(MP_QSTR_channelwise_divide_clamped),
     compositor_channelwise_divide_clamped},
    {MP_ROM_QSTR(MP_QSTR_channelwise_divide_reverse_clamped),
     compositor_channelwise_divide_reverse_clamped},

    {MP_ROM_QSTR(MP_QSTR_alpha_clear), compositor_alpha_clear},
    {MP_ROM_QSTR(MP_QSTR_alpha_copy), compositor_alpha_copy},
    {MP_ROM_QSTR(MP_QSTR_alpha_destination), compositor_alpha_destination},
    {MP_ROM_QSTR(MP_QSTR_alpha_source_over), compositor_alpha_source_over},
    {MP_ROM_QSTR(MP_QSTR_alpha_destination_over),
     compositor_alpha_destination_over},
    {MP_ROM_QSTR(MP_QSTR_alpha_source_in), compositor_alpha_source_in},
    {MP_ROM_QSTR(MP_QSTR_alpha_destination_in),
     compositor_alpha_destination_in},
    {MP_ROM_QSTR(MP_QSTR_alpha_source_out), compositor_alpha_source_out},
    {MP_ROM_QSTR(MP_QSTR_alpha_destination_out),
     compositor_alpha_destination_out},
    {MP_ROM_QSTR(MP_QSTR_alpha_source_atop), compositor_alpha_source_atop},
    {MP_ROM_QSTR(MP_QSTR_alpha_destination_atop),
     compositor_alpha_destination_atop},
    {MP_ROM_QSTR(MP_QSTR_alpha_xor), compositor_alpha_xor},
    {MP_ROM_QSTR(MP_QSTR_alpha_lighter), compositor_alpha_lighter},
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
