#include "plan.h"

#include <errno.h>
#include <math.h>
#include <stdio.h>

#include "buffer/float.h"
#include "fft.h"
#include "py/misc.h"
#include "py/obj.h"
#include "py/objstr.h"
#include "py/runtime.h"
#include "py/stream.h"
#include "utilities.h"

#define NOT_CONFIGURED_ERROR_MSG "fft plan not configured!"

typedef struct _FftPlan_obj_t {
  mp_obj_base_t base;
  fft_config_t* config;
  double sample_frequency;
  double bin_width;
  FloatBuffer_obj_t* input_buffer;
  FloatBuffer_obj_t* output_buffer;
} FftPlan_obj_t;

const mp_obj_type_t FftPlan_type;

typedef struct _fft_plan_iter_t {
  mp_obj_base_t base;
  mp_fun_1_t iternext;
  FftPlan_obj_t* plan;
  int size;
  int idx;
} fft_plan_iter_t;

/**
 * @brief Get the width of the output frequency bins for a given sample
 * frequency and sample length
 *
 * @param sample_frequency in hz
 * @param num_samples
 * @return bin width in hz
 */
STATIC double get_bin_width(double sample_frequency, size_t num_samples) {
  return sample_frequency / num_samples;
}

/**
 * @brief Set the real and imaginary components of a given frequency bin in the
 * output
 *
 * @param idx
 * @param real
 * @param imaginary
 * @return int
 */
static inline int set_output_bin(
    fft_config_t* config, size_t idx, double real, double imaginary) {
  int ret = 0;

  // check input config
  if (NULL == config) {
    ret = -ENOMEM;
    goto out;
  }

  // set the values
  config->output[(2 * idx) + 0] = real;
  config->output[(2 * idx) + 1] = imaginary;

out:
  return ret;
}

/**
 * @brief Optionally get the real and or imaginary components of the output bin.
 *
 * @param config
 * @param idx
 * @param real
 * @param imaginary
 * @return int
 */
static inline int get_output_bin(
    fft_config_t* config, size_t idx, double* real, double* imaginary) {
  int ret = 0;

  // check input config
  if (NULL == config) {
    ret = -ENOMEM;
    goto out;
  }

  // optionally give the real output
  if (NULL != real) {
    *real = (double)config->output[(2 * idx) + 0];
  }

  // optionally give the imaginary output
  if (NULL != imaginary) {
    *imaginary = (double)config->output[(2 * idx) + 1];
  }

out:
  return ret;
}

/**
 * @brief Get info about relevant real output bins for a given FFT config.
 *
 * @return 0 for success, negative errno on failure.
 */
STATIC int get_real_output_bins(
    fft_config_t* config, size_t* len_out, float* real_out, size_t real_len) {
  int ret = 0;

  if (NULL == config) {
    ret = -ENOMEM;
    goto out;
  }

  // the fft output gives both real and imaginary results interleaved, so
  // the number of real output bins is half the output size
  size_t real_bins = config->size / 2;

  // give the user the number of relevant bins
  if (NULL != len_out) {
    *len_out = real_bins;
  }

  // copy out the lesser of [real_len, relevant_bins] real fft results to the
  // real output array
  if (NULL != real_out) {
    size_t max_bins = real_bins;
    if (max_bins > real_len) {
      max_bins = real_len;
    }
    for (size_t idx = 0; idx < max_bins; idx++) {
      real_out[idx] = config->output[2 * idx];
    }
  }

out:
  return ret;
}

/**
 * @brief for now this function simply applies a hamming window - call it after
 *  setting input data and before executing the fft. only call once per
 * execution.
 *
 * @param self_in
 * @return STATIC
 */
STATIC mp_obj_t window(mp_obj_t self_in) {
  FftPlan_obj_t* self = MP_OBJ_TO_PTR(self_in);

  size_t capacity = self->config->size;
  float a0 = 25.0 / 46.0;
  for (size_t idx = 0; idx < capacity; idx++) {
    self->config->input[idx] *=
        a0 - (1 - a0) * (float)cos(2 * M_PI * ((double)idx / capacity));
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(window_obj, window);

STATIC mp_obj_t execute(mp_obj_t self_in) {
  FftPlan_obj_t* self = MP_OBJ_TO_PTR(self_in);
  if (!self->config) {
    mp_raise_OSError(-ENOMEM);
  }

  // execute the fft
  fft_execute(self->config);

  // get real output bin info
  size_t real_bin_count = 0;
  int ret = get_real_output_bins(self->config, &real_bin_count, NULL, 0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  // format the real outputs into the users output buffer
  // formatting includes:
  // - selecting only the real components of the fft
  // - applying an absolute value to the real component
  for (size_t idx = 0; idx < real_bin_count; idx++) {
    double real;
    ret = get_output_bin(self->config, idx, &real, NULL);

    if (0 != ret) {
      mp_raise_OSError(ret);
    }

    self->output_buffer->elements[idx] = fabs(real);
  }

  return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_1(execute_obj, execute);

// binary / unary operations
STATIC mp_obj_t unary_op(mp_unary_op_t op, mp_obj_t self_in) {
  FftPlan_obj_t* self = MP_OBJ_TO_PTR(self_in);
  switch (op) {
    case MP_UNARY_OP_LEN: {
      size_t length = 0;
      int ret = get_real_output_bins(self->config, &length, NULL, 0);
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
STATIC mp_obj_t iternext(mp_obj_t self_in) {
  fft_plan_iter_t* self = MP_OBJ_TO_PTR(self_in);
  FftPlan_obj_t* plan = MP_OBJ_TO_PTR(self->plan);
  int ret = 0;

  // check plan existence
  if (NULL == plan) {
    mp_raise_OSError(-ENOMEM);
  }

  // get number of bins
  size_t num_real_bins = 0;
  ret = get_real_output_bins(plan->config, &num_real_bins, NULL, 0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  if (self->idx < num_real_bins) {
    double real;
    ret = get_output_bin(plan->config, self->idx, &real, NULL);
    if (0 != ret) {
      mp_raise_OSError(ret);
    }

    // increment the current index of this iterable
    self->idx++;

    // return the real component of the output at this index
    return mp_obj_new_float(real);
  } else {
    // signal to stop iteration
    return MP_OBJ_STOP_ITERATION;
  }
}

STATIC mp_obj_t getiter(mp_obj_t self_in, mp_obj_iter_buf_t* iter_buf) {
  FftPlan_obj_t* self = MP_OBJ_TO_PTR(self_in);

  // get the iterbuf that is provided by the interpreter
  assert(sizeof(fft_plan_iter_t) <= sizeof(mp_obj_iter_buf_t));
  fft_plan_iter_t* iter = (fft_plan_iter_t*)iter_buf;

  // set the type as an iterable
  iter->base.type = &mp_type_polymorph_iter;

  // assign the custom fields
  iter->iternext = iternext;
  iter->plan = self;
  iter->idx = 0;

  // return the iterator object
  return MP_OBJ_FROM_PTR(iter);
}

STATIC mp_obj_t subscr(mp_obj_t self_in, mp_obj_t index, mp_obj_t value) {
  FftPlan_obj_t* self = MP_OBJ_TO_PTR(self_in);

  size_t idx = mp_obj_get_int(index);

  // get length
  size_t len = 0;
  int ret = get_real_output_bins(self->config, &len, NULL, 0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  // check bounds
  if (idx >= len) {
    mp_raise_ValueError(NULL);
  }

  if (value == MP_OBJ_SENTINEL) {
    // get the real component at this index
    double real;
    ret = get_output_bin(self->config, idx, &real, NULL);
    if (0 != ret) {
      mp_raise_OSError(ret);
    }
    return mp_obj_new_float(real);
  } else {
    // set the real component at this index
    double real;
    if (mp_obj_is_float(value)) {
      real = (double)mp_obj_get_float(value);
    } else if (mp_obj_is_int(value)) {
      real = (double)mp_obj_get_int(value);
    } else {
      mp_raise_TypeError(NULL);
    }

    ret = set_output_bin(self->config, idx, real, 0);
    if (0 != ret) {
      mp_raise_OSError(ret);
    }
    return mp_const_none;
  }
}

STATIC const mp_rom_map_elem_t locals_dict_table[] = {
    {MP_ROM_QSTR(MP_QSTR_window), MP_ROM_PTR(&window_obj)},
    {MP_ROM_QSTR(MP_QSTR_execute), MP_ROM_PTR(&execute_obj)},
};
STATIC MP_DEFINE_CONST_DICT(locals_dict, locals_dict_table);

// attributes
STATIC void attr(mp_obj_t self_in, qstr attribute, mp_obj_t* destination) {
  switch (attribute) {
    case MP_QSTR_bin_width:
      destination[0] =
          mp_obj_new_float(((FftPlan_obj_t*)MP_OBJ_TO_PTR(self_in))->bin_width);
      break;

    default:
      // No attribute found, continue lookup in locals dict.
      destination[1] = MP_OBJ_SENTINEL;
      break;
  }
}

STATIC void print(
    const mp_print_t* print, mp_obj_t self_in, mp_print_kind_t kind) {
  (void)kind;
  FftPlan_obj_t* self = MP_OBJ_TO_PTR(self_in);
  mp_print_str(print, "FftPlan(");
  mp_obj_print_helper(print, mp_obj_new_int(self->config->size), PRINT_REPR);
  mp_print_str(print, ")");
}

STATIC mp_obj_t make_new(
    const mp_obj_type_t* type, size_t n_args, size_t n_kw,
    const mp_obj_t* all_args) {
  // parse args
  enum {
    ARG_buffers,
    ARG_sample_freq,
  };
  static const mp_arg_t allowed_args[] = {
      {MP_QSTR_buffers, MP_ARG_REQUIRED | MP_ARG_OBJ, {.u_obj = mp_const_none}},
      {MP_QSTR_sample_frequency,
       MP_ARG_REQUIRED | MP_ARG_OBJ,
       {.u_obj = mp_const_none}},
  };
  mp_map_t kw_args;
  mp_map_init_fixed_table(&kw_args, n_kw, all_args + n_args);
  mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
  mp_arg_parse_all_kw_array(
      n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

  // instantiate the object
  FftPlan_obj_t* self = m_new_obj(FftPlan_obj_t);
  self->base.type = &FftPlan_type;

  // get the buffers
  mp_obj_t buffers_obj = args[ARG_buffers].u_obj;
  if (!mp_obj_is_type(buffers_obj, &mp_type_tuple)) {
    mp_raise_TypeError(NULL);
  }
  mp_obj_tuple_t* buffers_tuple = MP_OBJ_TO_PTR(buffers_obj);
  if (2 != buffers_tuple->len) {
    mp_raise_ValueError(NULL);
  }
  FloatBuffer_obj_t* input_buffer =
      float_buffer_from_obj(buffers_tuple->items[0]);
  FloatBuffer_obj_t* output_buffer =
      float_buffer_from_obj(buffers_tuple->items[1]);

  // check the sizes of the buffers
  if ((input_buffer->length / 2) != output_buffer->length) {
    mp_raise_ValueError(NULL);
  }
  size_t size = input_buffer->length;

  // get the sample frequency
  mp_obj_t sample_freq_obj = args[ARG_sample_freq].u_obj;
  double sample_frequency = 1.0;
  if (mp_obj_is_float(sample_freq_obj)) {
    sample_frequency = mp_obj_get_float(sample_freq_obj);
  } else if (mp_obj_is_int(sample_freq_obj)) {
    sample_frequency = mp_obj_get_int(sample_freq_obj);
  } else {
    mp_raise_TypeError(NULL);
  }
  self->sample_frequency = sample_frequency;
  self->input_buffer = input_buffer;
  self->output_buffer = output_buffer;

  // compute the bin width
  self->bin_width = get_bin_width(sample_frequency, size);

  // init the plan
  // - use the input buffer directly
  // - request the fft plan to allocate memory for the output
  // - the user-supplied output buffer will be filled with the real data
  self->config =
      fft_init(size, FFT_REAL, FFT_FORWARD, input_buffer->elements, NULL);
  if (!self->config) {
    mp_raise_OSError(-EACCES);
  }

  return MP_OBJ_FROM_PTR(self);
}

MP_DEFINE_CONST_OBJ_TYPE(
  FftPlan_type,
  MP_QSTR_FftPlan,
  MP_TYPE_FLAG_NONE | MP_TYPE_FLAG_ITER_IS_GETITER,
  make_new, make_new,
  print, print,
  unary_op, unary_op,
  binary_op, binary_op,
  subscr, subscr,
  iter, getiter,
  attr, attr,
  locals_dict, &locals_dict
);
