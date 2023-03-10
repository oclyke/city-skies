#include <math.h>

#include "buffer/float.h"
#include "plan.h"
#include "py/runtime.h"

/**
 * @brief Get the distance between 'location' and 'start' on the exponential
 * curve with exponent 'factor'
 *
 * Given: y(x) = x^f
 * Return y(location) - y(start) for the provided f
 *
 * @param factor the exponential factor used in the computation
 * @param start the low bound of the input
 * @param distance the distance from the 'start' bound to the higher bound
 * @return the scaled distance
 */
STATIC double ear_kernel(double factor, double location, double start) {
  return pow(location, factor) - pow(start, factor);
}

/**
 * @brief Reshapes a floating point array 'input' according to a logarithmic
 * mapping such that the nth element of the 'output' represents the sum of the
 * input elements over the range [n^f, (n+1)^f]
 *
 * https://www.audiocheck.net/soundtests_nonlinear.php
 *
 * @param factor_obj the exponential factor by which the bins are reshaped.
 * @param input_obj input from which the summed bins are drawn.
 * @param output_obj output into which to put the summed bins. optional, when
 * present must be a FloatBuffer.
 * @return None, when output was supplied. when output was None, will return the
 * number of bins required to contain the input after reshaping with the given
 * factor
 */
STATIC mp_obj_t
reshape(mp_obj_t factor_obj, mp_obj_t input_obj, mp_obj_t output_obj) {
  // reshapes input samples into output samples to compensate for nonlinearity
  // of the human ear https://www.audiocheck.net/soundtests_nonlinear.php

  // get the exponential factor
  mp_float_t factor;
  bool result = mp_obj_get_float_maybe(factor_obj, &factor);
  if (true != result) {
    mp_raise_TypeError(NULL);
  }

  // get the input
  FloatBuffer_obj_t* input = float_buffer_from_obj(input_obj);

  double progress = 0.0;
  if (output_obj == mp_const_none) {
    // no output supplied, return the required size for output to contain input
    // with this reshape factor

    // prevent excessive waste
    if (factor < 0.5) {
      mp_raise_ValueError(NULL);
    }

    size_t high = 0;
    size_t idx = 0;
    do {
      progress += ear_kernel(factor, idx + 1, idx);
      high = (size_t)progress;
      idx++;
    } while (high < input->length);
    return mp_obj_new_int(idx);
  } else {
    // output was supplied, fill the output and return None
    FloatBuffer_obj_t* output = float_buffer_from_obj(output_obj);
    double sum = 0.0;
    size_t input_bin_low = 0;
    size_t input_bin_high = 0;
    for (size_t idx = 0; idx < output->length; idx++) {
      progress += ear_kernel(factor, idx + 1, idx);
      size_t high = (size_t)progress;

      // when the upper bound increases the sum must be computed for the new
      // range of inputs
      if (high > input_bin_high) {
        input_bin_low = input_bin_high;
        input_bin_high = high;

        // compute sum for this range
        sum = 0.0;
        for (size_t sum_idx = input_bin_low; sum_idx < input_bin_high;
             sum_idx++) {
          if (sum_idx > input->length) {
            break;
          }
          sum += (double)input->elements[sum_idx];
        }
      }

      output->elements[idx] = sum;
    }
    return mp_const_none;
  }
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(reshape_obj, reshape);

// Define all properties of the module.
// Table entries are key/value pairs of the attribute name (a string)
// and the MicroPython object reference.
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
STATIC const mp_rom_map_elem_t module_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_reshape)},

    {MP_ROM_QSTR(MP_QSTR_reshape), MP_ROM_PTR(&reshape_obj)},
};
STATIC MP_DEFINE_CONST_DICT(module_globals, module_globals_table);

// Define module object.
const mp_obj_module_t reshape_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&module_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_reshape, reshape_module);
