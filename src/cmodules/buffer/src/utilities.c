#include <errno.h>
#include <math.h>

#include "fft.h"
#include "py/runtime.h"

/**
 * @brief Small utility to aid in interpolating a floating point value between
 * two others.
 *
 * @param lower the value returned when phase is 0
 * @param upper the value returned when phase is 1
 * @param phase the ratio of upper to lower - e.g. phase 0.5 means half way
 * between lower and upper. [0.0, 1.0]
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
 * @brief Interpolate a floating point array.
 *
 * @param array the a pointer to the floating point array to interpolate
 * @param length the number of floats contained in the buffer
 * @param phase the fractional completion along the input array
 * @param output the resulting interpolated value
 * @return int 0 on success, negative errno on failure
 */
int interpolate_float_array_linear(
    float* array, size_t length, double phase, double* output) {
  int ret = 0;
  // user does not need result
  if (NULL == output) {
    goto out;
  }

  // cannot interpolate nonexistent list
  if (NULL == array) {
    ret = -ENOMEM;
    goto out;
  }

  // cannot interpolate a zero-length input
  if (0 == length) {
    ret = -EINVAL;
    goto out;
  }

  // nothing to interpolate when input has single element
  if (1 == length) {
    *output = array[0];
    goto out;
  }

  // get maximum index
  size_t max_idx = length - 1;

  // linear interpolation gets clamped at the array bounds
  if (phase <= 0.0f) {
    *output = array[0];
    goto out;
  } else if (phase >= 1.0f) {
    *output = array[max_idx];
    goto out;
  }

  // get bounding bins
  double center = phase * max_idx;   // center E [0, max_idx]
  size_t lower_idx = floor(center);  // lower E [0, max_idx], integer
  size_t upper_idx = ceil(center);   // upper E [0, max_idx], integer

  // handle balance case
  if (lower_idx == upper_idx) {
    *output = array[lower_idx];
    goto out;
  }

  // get delta from the lower index
  double spacing = 1.0f / max_idx;
  double delta = (phase / spacing) - lower_idx;

  // interpolate between these two bins
  ret = interpolate_double_between(
      array[lower_idx], array[upper_idx], delta, output);
  if (0 != ret) {
    goto out;
  }

out:
  return ret;
}