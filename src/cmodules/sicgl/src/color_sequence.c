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
     color_sequence_interpolate_color_continuous_circular},
    {MP_ROM_QSTR(MP_QSTR_continuous_linear),
     color_sequence_interpolate_color_continuous_linear},
    {MP_ROM_QSTR(MP_QSTR_discrete_circular),
     color_sequence_interpolate_color_discrete_circular},
    {MP_ROM_QSTR(MP_QSTR_discrete_linear),
     color_sequence_interpolate_color_discrete_linear},
};
STATIC const size_t NUM_COLOR_SEQUENCE_MAP_TYPES =
    sizeof(color_sequence_map_types_table) / sizeof(map_type_entry_t);
STATIC int find_color_sequence_map_type_entry_index(
    mp_obj_t key, size_t* index) {
  int ret = 0;
  if (NULL == index) {
    ret = -EINVAL;
    goto out;
  }

  // try to find the corresponding map for this type
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

  mp_obj_t colors = sequence->colors;

  // len will be used locally even when user does not request its value
  size_t len = 0;

  // check for none
  if (colors == mp_const_none) {
    goto out;
  }

  mp_obj_t* items;
  mp_obj_list_get(colors, &len, &items);

  if (NULL != colors_out) {
    size_t numel = MIN(len, size);
    for (size_t idx = 0; idx < numel; idx++) {
      colors_out[idx] = mp_obj_get_int(items[idx]);
    }
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
    if (&mp_type_list != type) {
      mp_raise_TypeError(NULL);
    }
    self->colors = colors;
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(set_colors_obj, set_colors);

STATIC mp_obj_t set_map_type(mp_obj_t self_in, mp_obj_t type_obj) {
  ColorSequence_obj_t* self = MP_OBJ_TO_PTR(self_in);

  size_t type = 0;
  int ret = find_color_sequence_map_type_entry_index(type_obj, &type);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  self->map_type = type_obj;
  self->map = color_sequence_map_types_table[type].map;

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(set_map_type_obj, set_map_type);

// binary / unary operations
STATIC mp_obj_t unary_op(mp_unary_op_t op, mp_obj_t self_in) {
  ColorSequence_obj_t* self = MP_OBJ_TO_PTR(self_in);
  switch (op) {
    case MP_UNARY_OP_LEN: {
      size_t length = 0;
      int ret = color_sequence_get(self, &length, NULL, 0);
      if (0 != ret) {
        mp_raise_OSError(ret);
      }
      return mp_obj_new_int(length);
    } break;

    default:
      // operator not supported
      return MP_OBJ_NULL;
      break;
  }
}

STATIC mp_obj_t binary_op(mp_binary_op_t op, mp_obj_t lhs, mp_obj_t rhs) {
  // ColorSequence_obj_t *left_hand_side = MP_OBJ_TO_PTR(lhs);
  // ColorSequence_obj_t *right_hand_side = MP_OBJ_TO_PTR(rhs);
  switch (op) {
    // case MP_BINARY_OP_EQUAL:
    //   return mp_obj_new_bool((left_hand_side->a == right_hand_side->a) &&
    //   (left_hand_side->b == right_hand_side->b));
    // case MP_BINARY_OP_ADD:
    //   return create_new_myclass(left_hand_side->a + right_hand_side->a,
    //   left_hand_side->b + right_hand_side->b);
    // case MP_BINARY_OP_MULTIPLY:
    //   return create_new_myclass(left_hand_side->a * right_hand_side->a,
    //   left_hand_side->b * right_hand_side->b);
    default:
      // operator not supported
      return MP_OBJ_NULL;
  }
}

// iteration / subscripting
STATIC mp_obj_t subscr(mp_obj_t self_in, mp_obj_t index, mp_obj_t value) {
  ColorSequence_obj_t* self = MP_OBJ_TO_PTR(self_in);
  mp_obj_t colors = self->colors;
  size_t idx = mp_obj_get_int(index);

  // check for none
  if (colors == mp_const_none) {
    mp_raise_ValueError(NULL);
  }

  // determine length of colors
  size_t len = 0;
  mp_obj_t* items;
  mp_obj_list_get(colors, &len, &items);

  // check bounds
  if (idx >= len) {
    mp_raise_ValueError(NULL);
  }

  if (value == MP_OBJ_SENTINEL) {
    return items[idx];
  } else {
    // check type
    if (!mp_obj_is_int(value)) {
      mp_raise_TypeError(NULL);
    }

    mp_obj_list_store(colors, index, value);
  }
  return mp_const_none;
}

// locals dict
STATIC const mp_rom_map_elem_t locals_table[] = {
    // methods
    {MP_ROM_QSTR(MP_QSTR_set_colors), MP_ROM_PTR(&set_colors_obj)},
    {MP_ROM_QSTR(MP_QSTR_set_map_type), MP_ROM_PTR(&set_map_type_obj)},
};
STATIC MP_DEFINE_CONST_DICT(locals_dict, locals_table);

// attributes
STATIC void attr(mp_obj_t self_in, qstr attribute, mp_obj_t* destination) {
  switch (attribute) {
    case MP_QSTR_colors:
      destination[0] = ((ColorSequence_obj_t*)MP_OBJ_TO_PTR(self_in))->colors;
      break;

    case MP_QSTR_map_type:
      destination[0] = ((ColorSequence_obj_t*)MP_OBJ_TO_PTR(self_in))->map_type;
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
  mp_obj_print_helper(print, self->map_type, PRINT_REPR);
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
    ARG_map_type,
  };
  static const mp_arg_t allowed_args[] = {
      {MP_QSTR_colors, MP_ARG_OBJ, {.u_obj = mp_const_none}},
      {MP_QSTR_map_type,
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
  set_map_type(self_obj, args[ARG_map_type].u_obj);

  return self_obj;
}

const mp_obj_type_t ColorSequence_type = {
    {&mp_type_type},        .name = MP_QSTR_ColorSequence,
    .print = print,         .make_new = make_new,
    .attr = attr,           .locals_dict = (mp_obj_dict_t*)&locals_dict,
    .subscr = subscr,       .unary_op = unary_op,
    .binary_op = binary_op,
};
