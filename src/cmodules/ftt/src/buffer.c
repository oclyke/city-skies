#include <errno.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "fft.h"
#include "plan.h"
#include "py/misc.h"
#include "py/obj.h"
#include "py/objstr.h"
#include "py/runtime.h"
#include "py/stream.h"
#include "utilities.h"

typedef struct _FftBuffer_obj_t {
  mp_obj_base_t base;
  float* memory;
  size_t length;
} FftBuffer_obj_t;

const mp_obj_type_t AudioBuffer_type;

typedef struct _fft_buffer_iter_t {
  mp_obj_base_t base;
  mp_fun_1_t iternext;
  FftBuffer_obj_t* buffer;
  size_t idx;
} fft_buffer_iter_t;

/**
 * @brief This function scales the buffer
 *
 * @param self_in
 * @param factor
 * @return STATIC
 */
STATIC mp_obj_t scale(mp_obj_t self_in, mp_obj_t factor_obj) {
  FftBuffer_obj_t* self = MP_OBJ_TO_PTR(self_in);
  double factor = mp_obj_get_float(factor_obj);

  for (size_t idx = 0; idx < self->length; idx++) {
    self->memory[idx] *= factor;
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(scale_obj, scale);

STATIC mp_obj_t output(mp_obj_t self_in, mp_obj_t output_obj) {
  FftBuffer_obj_t* self = MP_OBJ_TO_PTR(self_in);

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
    output[idx] = mp_obj_new_float((mp_float_t)self->memory[idx]);
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
  FftBuffer_obj_t* self = MP_OBJ_TO_PTR(self_in);

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
    ret = interpolate_linear(self->memory, self->length, phase, &interpolated);
    if (0 != ret) {
      mp_raise_OSError(ret);
    }

    // store the element in the output list
    output[idx] = mp_obj_new_float(interpolated);
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(align_obj, align);

// binary / unary operations
STATIC mp_obj_t unary_op(mp_unary_op_t op, mp_obj_t self_in) {
  FftBuffer_obj_t* self = MP_OBJ_TO_PTR(self_in);
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
  FftBuffer_obj_t* self = MP_OBJ_TO_PTR(iter->buffer);

  // check buffer existence
  if (NULL == self) {
    mp_raise_OSError(-ENOMEM);
  }

  if (iter->idx < self->length) {
    float value = self->memory[iter->idx];
    iter->idx++;
    return mp_obj_new_float((mp_float_t)value);
  } else {
    // signal to stop iteration
    return MP_OBJ_STOP_ITERATION;
  }
}

STATIC mp_obj_t getiter(mp_obj_t self_in, mp_obj_iter_buf_t* iter_buf) {
  FftBuffer_obj_t* self = MP_OBJ_TO_PTR(self_in);

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
  FftBuffer_obj_t* self = MP_OBJ_TO_PTR(self_in);
  size_t idx = mp_obj_get_int(index);

  // check bounds
  if (idx >= self->length) {
    mp_raise_ValueError(NULL);
  }

  if (value == MP_OBJ_SENTINEL) {
    return mp_obj_new_float((mp_float_t)self->memory[idx]);
  } else {
    // set the real component at this index
    float val;
    if (mp_obj_is_float(value)) {
      val = (double)mp_obj_get_float(value);
    } else if (mp_obj_is_int(value)) {
      val = (double)mp_obj_get_int(value);
    } else {
      mp_raise_TypeError(NULL);
    }
    self->memory[idx] = val;

    return mp_const_none;
  }
}

STATIC const mp_rom_map_elem_t locals_dict_table[] = {
    {MP_ROM_QSTR(MP_QSTR_scale), MP_ROM_PTR(&scale_obj)},
    {MP_ROM_QSTR(MP_QSTR_output), MP_ROM_PTR(&output_obj)},
    {MP_ROM_QSTR(MP_QSTR_align), MP_ROM_PTR(&align_obj)},
};
STATIC MP_DEFINE_CONST_DICT(buffer_locals_dict, locals_dict_table);

STATIC void print(
    const mp_print_t* print, mp_obj_t self_in, mp_print_kind_t kind) {
  (void)kind;
  FftBuffer_obj_t* self = MP_OBJ_TO_PTR(self_in);
  mp_print_str(print, "FftBuffer(");
  mp_obj_print_helper(print, mp_obj_new_int(self->length), PRINT_REPR);
  mp_print_str(print, ")");
}

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

  // attempt to allocate memory
  float* memory = (float*)malloc(size * sizeof(float));
  if (NULL == memory) {
    mp_raise_OSError(-ENOMEM);
  }

  // instantiate the object
  FftBuffer_obj_t* self = m_new_obj(FftBuffer_obj_t);
  self->base.type = &AudioBuffer_type;
  self->length = size;
  self->memory = memory;

  return MP_OBJ_FROM_PTR(self);
}

const mp_obj_type_t AudioBuffer_type = {
    {&mp_type_type},
    .name = MP_QSTR_AudioBuffer,
    .print = print,
    .make_new = make_new,
    .locals_dict = (mp_obj_dict_t*)&buffer_locals_dict,
    .getiter = getiter,
    .subscr = subscr,
    .unary_op = unary_op,
    .binary_op = binary_op,
};