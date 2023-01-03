#include "plan.h"

#include <errno.h>
#include <math.h>
#include <stdio.h>

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
} FftPlan_obj_t;

const mp_obj_type_t FftPlan_type;

/**
 * @brief Get the scaled distance between two integer locations according
 * to an exponential scale factor to account for human hearing.
 *
 * @param factor exponential factor
 * @param low low index
 * @param high high index
 * @return STATIC
 */
STATIC mp_int_t ear_kernel(mp_int_t factor, size_t low, size_t high) {
  return (pow(high, factor) - pow(low, factor));
}

/**
 * @brief Sum a range of floating point values from the given input buffer.
 *
 * @param input
 * @param min
 * @param max
 * @param floor
 * @return
 */
STATIC mp_float_t sum_bin_range(
    float* input, size_t size_bins, size_t from, size_t to, mp_float_t floor) {
  mp_float_t accumulated = 0;
  for (size_t idx = from; idx <= to; idx++) {
    if (idx > size_bins) {
      return accumulated;
    }
    size_t odx = 2 * idx;
    mp_float_t entry = input[odx];
    if (entry >= floor) {
      accumulated += entry;
    }
  }
  return accumulated;
}

// Class methods
STATIC mp_obj_t feed(mp_obj_t self_in, mp_obj_t o_in) {
  FftPlan_obj_t* self = MP_OBJ_TO_PTR(self_in);

  size_t idx = 0;
  size_t capacity = self->config->size;

  mp_obj_iter_buf_t iter_buf;
  mp_obj_t iterable = mp_getiter(o_in, &iter_buf);
  mp_obj_t item;

  while (((item = mp_iternext(iterable)) != MP_OBJ_STOP_ITERATION) &&
         (idx < capacity)) {
    self->config->input[idx] = (float)mp_obj_get_float(item);
    idx++;
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(feed_obj, feed);

/**
 * @brief for now this function simply applies a hamming window - call it after
 *  feeding in data and before executing the fft. only call once per feed
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
        a0 - (1 - a0) * (float)cos(2 * M_PI * ((float)idx / capacity));
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

  // apply absolute value
  for (int idx = 0; idx < self->config->size; idx += 2) {
    self->config->output[idx] = fabs(self->config->output[idx]);
  }

  return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_1(execute_obj, execute);

STATIC mp_obj_t output(mp_obj_t self_in, mp_obj_t output_obj) {
  FftPlan_obj_t* self = MP_OBJ_TO_PTR(self_in);
  if (!self->config) {
    mp_raise_OSError(-ENOMEM);
  }

  // we only take the real components so the number of outputs is half the size
  // of the fft
  size_t num_bins = self->config->size / 2;

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
  size_t max_bins_out = num_bins;
  if (numout < max_bins_out) {
    max_bins_out = numout;
  }

  // find the max value of the real outputs and store their absolute value
  // note: we ignore the value of the dc component (output[0])
  bool initmax = true;
  mp_float_t max = 0.0;
  for (size_t idx = 0; idx < max_bins_out; idx++) {
    size_t odx = 2 * idx;
    mp_float_t val = self->config->output[odx];
    if (initmax && (idx > 0)) {
      max = val;
      initmax = false;
    }
    if (val > max) {
      max = val;
    }
    output[idx] = mp_obj_new_float(val);
  }

  // return the maximum value to allow for scaling
  return mp_obj_new_float(max);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(output_obj, output);

STATIC mp_obj_t
reshape(mp_obj_t self_in, mp_obj_t output_obj, mp_obj_t config_obj) {
  // reshapes input samples into output samples to compensate for nonlinearity
  // of the human ear https://www.audiocheck.net/soundtests_nonlinear.php
  FftPlan_obj_t* self = MP_OBJ_TO_PTR(self_in);

  // unpack the configuration
  mp_float_t factor;
  mp_float_t floor;
  int ret = unpack_float_tuple2(config_obj, &factor, &floor);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

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

  // get input list, skipping the first (DC) bin (both real and imaginary parts)
  float* input = &self->config->output[2];
  size_t input_bins = self->config->size / 2;

  // keep track of how many bins have been handled
  mp_float_t bins_handled = 0.0;
  size_t bins_handled_int = 0;
  size_t bin_low = 0;
  size_t bin_high = 0;

  // for each of the output bins sum the corresponding range of input bins,
  // according to the ear kernel
  size_t idx = 0;
  mp_float_t sum = 0;
  mp_float_t maximum = sum;
  do {
    // determine the number of bins that should be accumulated into this output
    // index
    bins_handled += ear_kernel(factor, idx, idx + 1);
    bins_handled_int = (size_t)bins_handled;

    // when this upper limit advances move the entire window and perform the sum
    if (bins_handled_int > bin_high) {
      bin_low = bin_high;
      bin_high = bins_handled_int;
      sum = sum_bin_range(input, input_bins, bin_low, bin_high, floor);

      // check the sum to see if it is the maximum
      if (sum > maximum) {
        maximum = sum;
      }
    }

    // the output at this index will either be a new value or the same value as
    // previous depending on whether the upper bin index had moved
    output[idx] = mp_obj_new_float(sum);

    // advance the output index
    idx++;
  } while (idx < numout);

  // return the maximum value for scaling
  return mp_obj_new_int(maximum);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(reshape_obj, reshape);

STATIC const mp_rom_map_elem_t plan_locals_dict_table[] = {
    {MP_ROM_QSTR(MP_QSTR_feed), MP_ROM_PTR(&feed_obj)},
    {MP_ROM_QSTR(MP_QSTR_window), MP_ROM_PTR(&window_obj)},
    {MP_ROM_QSTR(MP_QSTR_execute), MP_ROM_PTR(&execute_obj)},
    {MP_ROM_QSTR(MP_QSTR_output), MP_ROM_PTR(&output_obj)},
    {MP_ROM_QSTR(MP_QSTR_reshape), MP_ROM_PTR(&reshape_obj)},
};
STATIC MP_DEFINE_CONST_DICT(plan_locals_dict, plan_locals_dict_table);

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

  // instantiate the object
  FftPlan_obj_t* self = m_new_obj(FftPlan_obj_t);
  self->base.type = &FftPlan_type;

  // get the size
  mp_int_t size = args[ARG_size].u_int;

  // init the plan
  self->config = fft_init(size, FFT_REAL, FFT_FORWARD, NULL, NULL);
  if (!self->config) {
    mp_raise_OSError(-EACCES);
  }

  return MP_OBJ_FROM_PTR(self);
}

const mp_obj_type_t FftPlan_type = {
    {&mp_type_type},
    .name = MP_QSTR_FftPlan,
    .print = print,
    .make_new = make_new,
    .locals_dict = (mp_obj_dict_t*)&plan_locals_dict,
};