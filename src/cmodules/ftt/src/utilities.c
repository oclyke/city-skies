#include <errno.h>
#include <math.h>

#include "fft.h"
#include "py/runtime.h"

int extract_float_obj(mp_obj_t obj, mp_float_t* value) {
  int ret = 0;
  if (mp_obj_is_float(obj)) {
    *value = mp_obj_get_float(obj);
  } else if (mp_obj_is_int(obj)) {
    *value = (mp_float_t)mp_obj_get_int(obj);
  } else {
    ret = -EINVAL;
    goto out;
  }

out:
  return ret;
}

int unpack_float_tuple2(mp_obj_t obj, mp_float_t* u, mp_float_t* v) {
  int ret = 0;
  if (!mp_obj_is_type(obj, &mp_type_tuple)) {
    ret = -EINVAL;
    goto out;
  }
  mp_obj_tuple_t* tuple = MP_OBJ_TO_PTR(obj);
  if (2 != tuple->len) {
    ret = -EINVAL;
    goto out;
  }
  if (NULL != u) {
    ret = extract_float_obj(tuple->items[0], u);
    if (0 != ret) {
      goto out;
    }
  }
  if (NULL != v) {
    ret = extract_float_obj(tuple->items[1], v);
    if (0 != ret) {
      goto out;
    }
  }

out:
  return ret;
}

/**
 * @brief Small utility to aid in interpolating a floating point value between two others.
 * 
 * @param lower the value returned when phase is 0
 * @param upper the value returned when phase is 1
 * @param phase the ratio of upper to lower - e.g. phase 0.5 means half way between lower and upper. [0.0, 1.0]
 * @param output the resulting value
 * @return int 0 on success, else negative error number
 */
static inline int interpolate_double_between(
    double lower, double upper, double phase, double* output) {
  int ret = 0;
  if (NULL == output) {
    ret = -ENOMEM;
    goto out;
  }

  *output = (phase * (upper - lower)) + lower;

out:
  return ret;
}

/**
 * @brief Returns the index of the nth real element in an fft config output.
 * Assumes that n a contiguous integer in the range [0, (config->size/2) - 1]
 * 
 * @param idx 
 * @return size_t 
 */
static inline size_t real_index(size_t n) {
  return 2 * n;
}

/**
 * @brief 
 * 
 * @param config the fft_config_t object containing the bins to interpolate
 * @param phase the fractional completion from the DC bin to the high frequency bin at which to get the output
 * @param output the resulting interpolated value
 * @return int 0 on success, negative errno on failure
 */
int interpolate_real_outputs_linear(
    fft_config_t* config, double phase, double* output) {
  int ret = 0;
  // user does not need result
  if (NULL == output) {
    goto out;
  }

  // cannot interpolate nonexistent list
  if (NULL == config) {
    ret = -ENOMEM;
    goto out;
  }
  if (NULL == config->output) {
    ret = -ENOMEM;
    goto out;
  }

  // we only take the real components so the number of outputs is half the size
  // of the fft
  size_t length = config->size / 2;

  // cannot interpolate a zero-length input
  if (0 == length) {
    ret = -EINVAL;
    goto out;
  }

  // nothing to interpolate when input has single element
  if (1 == length) {
    *output = config->output[real_index(0)];
    goto out;
  }

  // linear interpolation gets clamped at the array bounds
  if (phase <= 0.0f) {
    *output = config->output[real_index(0)];
    goto out;
  } else if (phase >= 1.0f) {
    *output = config->output[real_index(length - 1)];
    goto out;
  }

  // get bounding bins
  size_t max_idx = length - 1;
  double center = phase * max_idx;   // center E [0, max_idx]
  size_t lower_idx = floor(center);  // lower E [0, max_idx], integer
  size_t upper_idx = ceil(center);   // upper E [0, max_idx], integer

  // handle balance case
  if (lower_idx == upper_idx) {
    *output = config->output[real_index(lower_idx)];
    goto out;
  }

  // get delta from the lower index
  double spacing = 1.0f / max_idx;
  double delta = (phase / spacing) - lower_idx;

  // interpolate between these two bins
  ret = interpolate_double_between(
      config->output[real_index(lower_idx)],
      config->output[real_index(upper_idx)],
      delta,
      output
  );
  if (0 != ret) {
    goto out;
  }

out:
  return ret;
}
