#include "pysicgl/color_sequence.h"

#include <errno.h>
#include <stdio.h>

#include "py/obj.h"
#include "py/runtime.h"
#include "pysicgl/utilities.h"

typedef struct _map_type_entry_t {
  mp_obj_t key;
  sequence_map_fn map;
} map_type_entry_t;

STATIC const map_type_entry_t color_sequence_map_types_table[] = {
    {MP_ROM_QSTR(MP_QSTR_continuous_circular),
     color_sequence_get_color_continuous_circular},
    {MP_ROM_QSTR(MP_QSTR_continuous_linear),
     color_sequence_get_color_continuous_linear},
    {MP_ROM_QSTR(MP_QSTR_discrete_circular),
     color_sequence_get_color_discrete_circular},
    {MP_ROM_QSTR(MP_QSTR_discrete_linear),
     color_sequence_get_color_discrete_linear},
};
STATIC const size_t NUM_COLOR_SEQUENCE_MAP_TYPES =
    sizeof(color_sequence_map_types_table) / sizeof(map_type_entry_t);
int find_color_sequence_map_type_entry_index(mp_obj_t key, size_t* index) {
  int ret = 0;
  if (NULL == index) {
    ret = -EINVAL;
    goto out;
  }

  // try to find the
  for (size_t idx = 0; idx < NUM_COLOR_SEQUENCE_MAP_TYPES; idx++) {
    if (color_sequence_map_types_table[idx].key == key) {
      *index = idx;
      goto out;
    }
  }

  ret = -ENOENT;

out:
  return ret;
}

// utilities for c bindings
/**
 * @brief get information regarding a color sequence.
 *
 * @param sequence the color sequence in question
 * @param length an output into which the color sequence length will be placed,
 * if non-null.
 * @param colors array of color_t into which the colors will be fetched, if
 * non-null.
 * @param size size of the colors array, indicating how many colors may be
 * fetched.
 * @return int
 */
int color_sequence_get(
    ColorSequence_obj_t* sequence, size_t* length, color_t* colors_out,
    size_t size) {
  int ret = 0;
  if (NULL == sequence) {
    ret = -EINVAL;
    goto out;
  }

  // len will be used locally even when user does not request its value
  size_t len = 0;

  // check for none
  if (sequence->colors == mp_const_none) {
    goto out;
  }

  // check the type of colors
  mp_obj_t colors = sequence->colors;
  const mp_obj_type_t* colors_type = mp_obj_get_type(sequence->colors);
  if (&mp_type_list == colors_type) {
    // when colors is a list each item is a color
    mp_obj_t* items;
    mp_obj_list_get(colors, &len, &items);

    if (NULL != colors) {
      size_t numel = MIN(len, size);
      for (size_t idx = 0; idx < numel; idx++) {
        colors_out[idx] = mp_obj_get_int(items[idx]);
      }
    }

  } else if (&mp_type_tuple == colors_type) {
    // when colors is a tuple each item is a color
    mp_obj_t* items;
    mp_obj_tuple_get(colors, &len, &items);

    if (NULL != colors) {
      size_t numel = MIN(len, size);
      for (size_t idx = 0; idx < numel; idx++) {
        colors_out[idx] = mp_obj_get_int(items[idx]);
      }
    }

  } else if (&mp_type_bytearray == colors_type) {
    // when colors is a byte array each color is represented by bytes_per_pixel
    // elements
    mp_buffer_info_t buffer_info;
    mp_get_buffer_raise(colors, &buffer_info, MP_BUFFER_READ);

    // determine whole number of colors in the sequence
    len = buffer_info.len / bytes_per_pixel();

    if (NULL != colors) {
      size_t numel = MIN(len, size);
      color_t* source = (color_t*)buffer_info.buf;
      for (size_t idx = 0; idx < numel; idx++) {
        colors_out[idx] = source[idx];
      }
    }

  } else {
    ret = -EINVAL;
    goto out;
  }

out:
  // pass out the length
  if (NULL != length) {
    *length = len;
  }

  return ret;
}

// class methods
STATIC mp_obj_t set_colors(mp_obj_t self_in, mp_obj_t colors) {
  ColorSequence_obj_t* self = MP_OBJ_TO_PTR(self_in);

  if (mp_const_none == colors) {
    self->colors = mp_const_none;
  } else {
    const mp_obj_type_t* type = mp_obj_get_type(colors);
    if ((&mp_type_list != type) && (&mp_type_tuple != type) &&
        (&mp_type_bytearray != type)) {
      mp_raise_msg(&mp_type_Exception, NULL);
    }
    self->colors = colors;
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(set_colors_obj, set_colors);

STATIC mp_obj_t set_type(mp_obj_t self_in, mp_obj_t type_obj) {
  ColorSequence_obj_t* self = MP_OBJ_TO_PTR(self_in);

  size_t type = 0;
  int ret = find_color_sequence_map_type_entry_index(type_obj, &type);
  if (0 != ret) {
    mp_raise_ValueError(NULL);
  }
  self->type = type_obj;
  self->map = color_sequence_map_types_table[type].map;

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(set_type_obj, set_type);

// locals dict
STATIC const mp_rom_map_elem_t locals_table[] = {
    // methods
    {MP_ROM_QSTR(MP_QSTR_set_colors), MP_ROM_PTR(&set_colors_obj)},
    {MP_ROM_QSTR(MP_QSTR_set_type), MP_ROM_PTR(&set_type_obj)},
};
STATIC MP_DEFINE_CONST_DICT(locals_dict, locals_table);

// attributes
STATIC void attr(mp_obj_t self_in, qstr attribute, mp_obj_t* destination) {
  switch (attribute) {
    case MP_QSTR_colors:
      destination[0] = ((ColorSequence_obj_t*)MP_OBJ_TO_PTR(self_in))->colors;
      break;

    default:
      // No attribute found, continue lookup in locals dict.
      destination[1] = MP_OBJ_SENTINEL;
      break;
  }
}

// type methods
STATIC void print(
    const mp_print_t* print, mp_obj_t self_in, mp_print_kind_t kind) {
  (void)kind;
  ColorSequence_obj_t* self = MP_OBJ_TO_PTR(self_in);
  size_t length;
  int ret = color_sequence_get(self, &length, NULL, 0);
  if (0 != ret) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }

  mp_print_str(print, "ColorSequence( type: ");
  mp_obj_print_helper(print, self->type, PRINT_REPR);
  mp_print_str(print, ", length: ");
  mp_obj_print_helper(print, mp_obj_new_int(length), PRINT_REPR);
  mp_print_str(print, ", colors: ");
  mp_obj_print_helper(print, self->colors, PRINT_REPR);
  mp_print_str(print, "))");
}

STATIC mp_obj_t make_new(
    const mp_obj_type_t* type, size_t n_args, size_t n_kw,
    const mp_obj_t* all_args) {
  // parse args
  enum {
    ARG_colors,
    ARG_type,
  };
  static const mp_arg_t allowed_args[] = {
      {MP_QSTR_colors, MP_ARG_OBJ, {.u_obj = mp_const_none}},
      {MP_QSTR_type,
       MP_ARG_OBJ,
       {.u_obj = MP_ROM_QSTR(MP_QSTR_continuous_circular)}},
  };
  mp_map_t kw_args;
  mp_map_init_fixed_table(&kw_args, n_kw, all_args + n_args);
  mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
  mp_arg_parse_all_kw_array(
      n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

  // create instance object
  ColorSequence_obj_t* self = m_new_obj(ColorSequence_obj_t);
  self->base.type = &ColorSequence_type;
  mp_obj_t self_obj = MP_OBJ_FROM_PTR(self);

  // set colors and type
  set_colors(self_obj, args[ARG_colors].u_obj);
  // set_type(self_obj, mp_obj_new_int(args[ARG_type].u_int));
  set_type(self_obj, args[ARG_type].u_obj);

  return self_obj;
}

const mp_obj_type_t ColorSequence_type = {
    {&mp_type_type}, .name = MP_QSTR_ColorSequence,
    .print = print,  .make_new = make_new,
    .attr = attr,    .locals_dict = (mp_obj_dict_t*)&locals_dict,
};
