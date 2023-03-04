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
 * @brief Set the real and imaginary components of a given frequency bin in the output
 * 
 * @param idx 
 * @param real 
 * @param imaginary 
 * @return int 
 */
static inline int set_output_bin(fft_config_t* config, size_t idx, double real, double imaginary) {
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
static inline int get_output_bin(fft_config_t* config, size_t idx, double* real, double* imaginary) {
  int ret = 0;

  // check input config
  if (NULL == config) {
    ret = -ENOMEM;
    goto out;
  }

  // optionally give the real output
  if (NULL != real) {
    *real = config->output[(2 * idx) + 0];
  }

  // optionally give the imaginary output
  if (NULL != imaginary) {
    *imaginary = config->output[(2 * idx) + 1];
  }

out:
  return ret;
}

/**
 * @brief Get info about relevant real output bins for a given FFT config.
 * 
 * @return 0 for success, negative errno on failure.
*/
STATIC int get_real_output_bins(fft_config_t* config, size_t* len_out, float* real_out, size_t real_len) {
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

  // copy out the lesser of [real_len, relevant_bins] real fft results to the real output array
  if (NULL != real_out) {
    size_t max_bins = real_bins;
    if (max_bins > real_len) {
      max_bins = real_len;
    }
    for (size_t idx = 0; idx < max_bins; idx++) {
      real_out[idx] = config->output[2*idx];
    }
  }

out:
  return ret;
}

/**
 * @brief Get the scaled distance between two integer locations according
 * to an exponential scale factor to account for human hearing.
 *
 * @param factor exponential factor
 * @param low low index
 * @param high high index
 * @return STATIC
 */
STATIC double ear_kernel(double factor, size_t low, size_t high) {
  return pow(high, factor) - pow(low, factor);
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
STATIC double sum_bin_range(
    float* input, size_t size_bins, size_t from, size_t to, mp_float_t floor) {
  double accumulated = 0;
  for (size_t idx = from; idx <= to; idx++) {
    if (idx > size_bins) {
      return accumulated;
    }
    double entry = (double)input[idx];
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

  // apply absolute value
  for (int idx = 0; idx < self->config->size; idx += 2) {
    self->config->output[idx] = fabs((double)self->config->output[idx]);
  }

  return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_1(execute_obj, execute);

STATIC mp_obj_t stats(mp_obj_t self_in) {
  FftPlan_obj_t* self = MP_OBJ_TO_PTR(self_in);
  if (!self->config) {
    mp_raise_OSError(-ENOMEM);
  }

  mp_float_t sum = 0;
  mp_float_t max = 0;
  size_t max_idx = 0;

  // get real output bins
  size_t real_bin_count = 0;
  int ret = get_real_output_bins(self->config, &real_bin_count, NULL, 0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  float real_bins[real_bin_count];
  ret = get_real_output_bins(self->config, NULL, real_bins, real_bin_count);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  // // intentionally zero the DC component
  // real_bins[0] = 0.0f;

  for (size_t idx = 0; idx < real_bin_count; idx++) {
    mp_float_t val = (mp_float_t)real_bins[idx];
    sum += val;
    if (val > max) {
      max = val;
      max_idx = idx;
    }
  }

  // return the maximum value to allow for scaling
  const size_t num_items = 3;
  mp_obj_t items[num_items];
  items[0] = mp_obj_new_float(sum);
  items[1] = mp_obj_new_float(max);
  items[2] = mp_obj_new_int(max_idx);
  return mp_obj_new_tuple(num_items, items);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(stats_obj, stats);

/**
 * @brief This function will zero the DC component of the fft output.
 * This needs to be called once for each fft computation as the output
 * is re-set each time.
 * 
 * @param self_in 
 * @return STATIC 
 */
STATIC mp_obj_t zero_dc(mp_obj_t self_in) {
  FftPlan_obj_t* self = MP_OBJ_TO_PTR(self_in);
  if (!self->config) {
    mp_raise_OSError(-ENOMEM);
  }

  // zero the 0th (DC) bin
  int ret = set_output_bin(self->config, 0, 0, 0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(zero_dc_obj, zero_dc);

STATIC mp_obj_t output(mp_obj_t self_in, mp_obj_t output_obj) {
  FftPlan_obj_t* self = MP_OBJ_TO_PTR(self_in);
  if (!self->config) {
    mp_raise_OSError(-ENOMEM);
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

  // get real output bins
  size_t real_bin_count = 0;
  int ret = get_real_output_bins(self->config, &real_bin_count, NULL, 0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  float real_bins[real_bin_count];
  ret = get_real_output_bins(self->config, NULL, real_bins, real_bin_count);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  // determine limiting size of output
  size_t max_bins_out = real_bin_count;
  if (numout < max_bins_out) {
    max_bins_out = numout;
  }

  // copy items into output
  for (size_t idx = 0; idx < max_bins_out; idx++) {
    output[idx] = mp_obj_new_float((mp_float_t)real_bins[idx]);
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(output_obj, output);

/**
 * @brief Interpolates the FFT bins to fit into the number of elements in the
 * output.
 * 
 * @param self_in 
 * @param output_obj 
 * @return STATIC 
 */
STATIC mp_obj_t align(mp_obj_t self_in, mp_obj_t output_obj) {
  FftPlan_obj_t* self = MP_OBJ_TO_PTR(self_in);
  if (!self->config) {
    mp_raise_OSError(-ENOMEM);
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

  // get the interpolated value for each element of the output list so that
  // the first and last elements correspond to the first and last bins of the
  // fft result
  int ret = 0;
  double interpolated = (double)0.0f;
  for (size_t idx = 0 ; idx < numout; idx++) {
    // get the phase for this output element
    double phase = ((double)idx / (numout - 1));

    // interpolate the fft bins to get the value for this element
    ret = interpolate_real_outputs_linear(self->config, phase, &interpolated);
    if (0 != ret) {
      mp_raise_OSError(ret);
    }

    // store the element in the output list
    output[idx] = mp_obj_new_float(interpolated);
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(align_obj, align);

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

  // get real output bins
  size_t real_bin_count = 0;
  ret = get_real_output_bins(self->config, &real_bin_count, NULL, 0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  float real_bins[real_bin_count];
  ret = get_real_output_bins(self->config, NULL, real_bins, real_bin_count);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  // keep track of how many bins have been handled
  double bins_handled = 0.0;
  size_t bins_handled_int = 0;
  size_t bin_low = 0;
  size_t bin_high = 0;

  // for each of the output bins sum the corresponding range of input bins,
  // according to the ear kernel
  size_t idx = 0;
  mp_float_t sum = 0;
  do {
    // determine the number of bins that should be accumulated into this output
    // index
    bins_handled += ear_kernel((double)factor, idx, idx + 1);
    bins_handled_int = (size_t)bins_handled;

    // when this upper limit advances move the entire window and perform the sum
    if (bins_handled_int > bin_high) {
      bin_low = bin_high;
      bin_high = bins_handled_int;
      sum = sum_bin_range(real_bins, real_bin_count, bin_low, bin_high, floor);
    }

    // the output at this index will either be a new value or the same value as
    // previous depending on whether the upper bin index had moved
    output[idx] = mp_obj_new_float(sum);

    // advance the output index
    idx++;
  } while (idx < numout);

  // return the maximum value for scaling
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(reshape_obj, reshape);

STATIC const mp_rom_map_elem_t plan_locals_dict_table[] = {
    {MP_ROM_QSTR(MP_QSTR_feed), MP_ROM_PTR(&feed_obj)},
    {MP_ROM_QSTR(MP_QSTR_window), MP_ROM_PTR(&window_obj)},
    {MP_ROM_QSTR(MP_QSTR_execute), MP_ROM_PTR(&execute_obj)},
    {MP_ROM_QSTR(MP_QSTR_zero_dc), MP_ROM_PTR(&zero_dc_obj)},
    {MP_ROM_QSTR(MP_QSTR_output), MP_ROM_PTR(&output_obj)},
    {MP_ROM_QSTR(MP_QSTR_align), MP_ROM_PTR(&align_obj)},
    {MP_ROM_QSTR(MP_QSTR_reshape), MP_ROM_PTR(&reshape_obj)},
    {MP_ROM_QSTR(MP_QSTR_stats), MP_ROM_PTR(&stats_obj)},
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
