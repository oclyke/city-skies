#include <errno.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "buffer/utilities.h"
#include "fft.h"
#include "plan.h"
#include "py/misc.h"
#include "py/obj.h"
#include "py/objstr.h"
#include "py/runtime.h"
#include "py/stream.h"

typedef struct _FloatBuffer_obj_t {
  mp_obj_base_t base;
  float* elements;
  size_t length;
} FloatBuffer_obj_t;

const mp_obj_type_t FloatBuffer_type;

typedef struct _fft_buffer_iter_t {
  mp_obj_base_t base;
  mp_fun_1_t iternext;
  FloatBuffer_obj_t* buffer;
  size_t idx;
} fft_buffer_iter_t;

STATIC FloatBuffer_obj_t* create_new_float_buffer_reference(
    size_t size, float* elements) {
  if (NULL == elements) {
    mp_raise_OSError(-ENOMEM);
  }

  // instantiate the object
  FloatBuffer_obj_t* self = m_new_obj(FloatBuffer_obj_t);
  self->base.type = &FloatBuffer_type;
  self->length = size;
  self->elements = elements;

  return self;
}

STATIC FloatBuffer_obj_t* create_new_float_buffer(size_t size) {
  float* elements = (float*)malloc(size * sizeof(float));
  return create_new_float_buffer_reference(size, elements);
}

/**
 * @brief This function scales the buffer in place
 *
 * @param self_in
 * @param factor
 * @return STATIC
 */
STATIC mp_obj_t scale(mp_obj_t self_in, mp_obj_t factor_obj) {
  FloatBuffer_obj_t* self = MP_OBJ_TO_PTR(self_in);
  mp_float_t factor;
  bool result = mp_obj_get_float_maybe(factor_obj, &factor);
  if (true != result) {
    mp_raise_TypeError(NULL);
    return mp_const_none;
  }

  for (size_t idx = 0; idx < self->length; idx++) {
    self->elements[idx] *= factor;
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(scale_obj, scale);

STATIC mp_obj_t output(mp_obj_t self_in, mp_obj_t output_obj) {
  FloatBuffer_obj_t* self = MP_OBJ_TO_PTR(self_in);

  // get the output list
  size_t numout = 0;
  mp_obj_t* output = NULL;
  if (!mp_obj_is_type(output_obj, &mp_type_list)) {
    mp_raise_TypeError(NULL);
  }
  mp_obj_list_get(output_obj, &numout, &output);
  if (NULL == output) {
    mp_raise_OSError(-ENOMEM);
  }

  // determine limiting size of output
  size_t max_bins_out = self->length;
  if (numout < max_bins_out) {
    max_bins_out = numout;
  }

  // copy items into output
  for (size_t idx = 0; idx < max_bins_out; idx++) {
    output[idx] = mp_obj_new_float((mp_float_t)self->elements[idx]);
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(output_obj, output);

/**
 * @brief Interpolates the buffer values to fit into the number of elements in
 * the output.
 *
 * @param self_in
 * @param output_obj
 * @return STATIC
 */
STATIC mp_obj_t align(mp_obj_t self_in, mp_obj_t output_obj) {
  FloatBuffer_obj_t* self = MP_OBJ_TO_PTR(self_in);

  // get the output list
  size_t numout = 0;
  mp_obj_t* output = NULL;
  if (!mp_obj_is_type(output_obj, &mp_type_list)) {
    mp_raise_TypeError(NULL);
  }
  mp_obj_list_get(output_obj, &numout, &output);
  if (NULL == output) {
    mp_raise_OSError(-ENOMEM);
  }

  // get the interpolated value for each element of the output list so that
  // the first and last elements correspond to the first and last bins of the
  // fft result
  int ret = 0;
  double interpolated = (double)0.0f;
  for (size_t idx = 0; idx < numout; idx++) {
    // get the phase for this output element
    double phase = ((double)idx / (numout - 1));

    // interpolate the fft bins to get the value for this element
    ret = interpolate_float_array_linear(
        self->elements, self->length, phase, &interpolated);
    if (0 != ret) {
      mp_raise_OSError(ret);
    }

    // store the element in the output list
    output[idx] = mp_obj_new_float(interpolated);
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(align_obj, align);

/**
 * @brief Make a reference to this buffer.
 * It is illegal to destroy the memory allocated for a buffer, as there is no
 * mechanism to inform refrences that this memory is no longer valid.
 *
 * @param n_args
 * @param pos_args
 * @param kw_args
 * @return STATIC
 */
STATIC mp_obj_t
reference(size_t n_args, const mp_obj_t* pos_args, mp_map_t* kw_args) {
  FloatBuffer_obj_t* self = MP_OBJ_TO_PTR(pos_args[0]);

  enum { ARG_window };
  const mp_arg_t allowed_args[] = {
      {MP_QSTR_window, MP_ARG_OBJ | MP_ARG_KW_ONLY, {.u_obj = mp_const_none}},
  };
  mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
  mp_arg_parse_all(
      n_args - 1, &pos_args[1], kw_args, MP_ARRAY_SIZE(allowed_args),
      allowed_args, args);

  // prepare the window bounds
  mp_int_t low = 0;
  mp_int_t high = self->length;
  mp_obj_t window_obj = args[ARG_window].u_obj;
  if (window_obj != mp_const_none) {
    if (!mp_obj_is_type(window_obj, &mp_type_tuple)) {
      mp_raise_TypeError(NULL);
    }
    mp_obj_tuple_t* window_tuple = MP_OBJ_TO_PTR(window_obj);
    if ((!mp_obj_get_int_maybe(window_tuple->items[0], &low)) ||
        (!mp_obj_get_int_maybe(window_tuple->items[1], &high))) {
      mp_raise_TypeError(NULL);
    }
    if ((low < 0) || (high < 0)) {
      mp_raise_ValueError(NULL);
    }
  }
  mp_int_t size = high - low;
  if (size > self->length) {
    mp_raise_ValueError(NULL);
  }

  // create the reference
  FloatBuffer_obj_t* reference =
      create_new_float_buffer_reference((size_t)size, &self->elements[low]);

  return MP_OBJ_FROM_PTR(reference);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_KW(reference_obj, 1, reference);

// binary / unary operations
STATIC mp_obj_t unary_op(mp_unary_op_t op, mp_obj_t self_in) {
  FloatBuffer_obj_t* self = MP_OBJ_TO_PTR(self_in);
  switch (op) {
    case MP_UNARY_OP_LEN:
      return mp_obj_new_int(self->length);
      break;

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
STATIC mp_obj_t iternext(mp_obj_t iter_in) {
  fft_buffer_iter_t* iter = MP_OBJ_TO_PTR(iter_in);
  FloatBuffer_obj_t* self = MP_OBJ_TO_PTR(iter->buffer);

  // check buffer existence
  if (NULL == self) {
    mp_raise_OSError(-ENOMEM);
  }

  if (iter->idx < self->length) {
    float value = self->elements[iter->idx];
    iter->idx++;
    return mp_obj_new_float((mp_float_t)value);
  } else {
    // signal to stop iteration
    return MP_OBJ_STOP_ITERATION;
  }
}

STATIC mp_obj_t getiter(mp_obj_t self_in, mp_obj_iter_buf_t* iter_buf) {
  FloatBuffer_obj_t* self = MP_OBJ_TO_PTR(self_in);

  // get the iterbuf that is provided by the interpreter
  assert(sizeof(fft_buffer_iter_t) <= sizeof(mp_obj_iter_buf_t));
  fft_buffer_iter_t* iter = (fft_buffer_iter_t*)iter_buf;

  // set the type as an iterable
  iter->base.type = &mp_type_polymorph_iter;

  // assign the custom fields
  iter->iternext = iternext;
  iter->buffer = self;
  iter->idx = 0;

  // return the iterator object
  return MP_OBJ_FROM_PTR(iter);
}

STATIC mp_obj_t subscr(mp_obj_t self_in, mp_obj_t index, mp_obj_t value) {
  FloatBuffer_obj_t* self = MP_OBJ_TO_PTR(self_in);

  if (value == MP_OBJ_SENTINEL) {
    // getting elements
#if MICROPY_PY_BUILTINS_SLICE
    if (mp_obj_is_type(index, &mp_type_slice)) {
      mp_bound_slice_t slice;
      mp_seq_get_fast_slice_indexes(self->length, index, &slice);
      uint16_t slice_len = (slice.stop - slice.start) / slice.step;
      FloatBuffer_obj_t* res = create_new_float_buffer(slice_len);
      for (size_t idx = 0; idx < slice_len; idx++) {
        size_t element_index = slice.start + idx * slice.step;
        if (element_index >= self->length) {
          break;
        }
        res->elements[idx] = self->elements[element_index];
      }
      return MP_OBJ_FROM_PTR(res);
    }
#endif

    // check bounds
    size_t idx = mp_obj_get_int(index);
    if (idx >= self->length) {
      mp_raise_ValueError(NULL);
    }

    return mp_obj_new_float((mp_float_t)self->elements[idx]);
  } else {
    // setting elements
#if MICROPY_PY_BUILTINS_SLICE
    if (mp_obj_is_type(index, &mp_type_slice)) {
      mp_bound_slice_t slice;
      mp_seq_get_fast_slice_indexes(self->length, index, &slice);
      uint16_t slice_len = (slice.stop - slice.start) / slice.step;

      // assume that the value is iterable
      mp_obj_iter_buf_t iter_buf;
      mp_obj_t iterable = mp_getiter(value, &iter_buf);
      mp_obj_t item;

      // iterate over the value setting slice elements until:
      // - all slices are filled
      // - the iterable empties
      // - there is no more space in the buffer
      size_t idx = 0;
      while (((item = mp_iternext(iterable)) != MP_OBJ_STOP_ITERATION) &&
             (idx < slice_len)) {
        size_t element_index = slice.start + idx * slice.step;
        if (element_index >= self->length) {
          break;
        }
        mp_float_t val;
        bool result = mp_obj_get_float_maybe(item, &val);
        if (true != result) {
          mp_raise_TypeError(NULL);
        }
        self->elements[element_index] = val;
        idx++;
      }

      return mp_const_none;
    }
#endif

    // check bounds
    size_t idx = mp_obj_get_int(index);
    if (idx >= self->length) {
      mp_raise_ValueError(NULL);
    }

    // set the real component at this index
    mp_float_t val;
    bool result = mp_obj_get_float_maybe(value, &val);
    if (true != result) {
      mp_raise_TypeError(NULL);
    }
    self->elements[idx] = val;

    return mp_const_none;
  }
}

STATIC const mp_rom_map_elem_t locals_dict_table[] = {
    {MP_ROM_QSTR(MP_QSTR_reference), MP_ROM_PTR(&reference_obj)},
    {MP_ROM_QSTR(MP_QSTR_scale), MP_ROM_PTR(&scale_obj)},
    {MP_ROM_QSTR(MP_QSTR_output), MP_ROM_PTR(&output_obj)},
    {MP_ROM_QSTR(MP_QSTR_align), MP_ROM_PTR(&align_obj)},
};
STATIC MP_DEFINE_CONST_DICT(locals_dict, locals_dict_table);

STATIC void print(
    const mp_print_t* print, mp_obj_t self_in, mp_print_kind_t kind) {
  (void)kind;
  FloatBuffer_obj_t* self = MP_OBJ_TO_PTR(self_in);
  mp_print_str(print, "FloatBuffer(");
  mp_obj_print_helper(print, mp_obj_new_int(self->length), PRINT_REPR);
  mp_print_str(print, ")");
}

/**
 * @brief Creates a new FLoatBuffer backed by an array of sufficient size.
 * It is illegal to destroy a FloatBuffer or free its memory, due to there
 * being no mechanism for informing references that this change has occurred.
 *
 * @param type
 * @param n_args
 * @param n_kw
 * @param all_args
 * @return STATIC
 */
STATIC mp_obj_t make_new(
    const mp_obj_type_t* type, size_t n_args, size_t n_kw,
    const mp_obj_t* all_args) {
  // parse args
  enum {
    ARG_size,
  };
  static const mp_arg_t allowed_args[] = {
      {MP_QSTR_size, MP_ARG_REQUIRED | MP_ARG_INT, {.u_int = 0}},
  };
  mp_map_t kw_args;
  mp_map_init_fixed_table(&kw_args, n_kw, all_args + n_args);
  mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
  mp_arg_parse_all_kw_array(
      n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

  // get the size
  mp_int_t size = args[ARG_size].u_int;

  // create the buffer
  FloatBuffer_obj_t* self = create_new_float_buffer(size);

  return MP_OBJ_FROM_PTR(self);
}

MP_DEFINE_CONST_OBJ_TYPE(
    FloatBuffer_type, MP_QSTR_FloatBuffer,
    MP_TYPE_FLAG_NONE | MP_TYPE_FLAG_ITER_IS_GETITER, make_new, make_new, print,
    print, unary_op, unary_op, binary_op, binary_op, subscr, subscr, iter,
    getiter, locals_dict, &locals_dict);
