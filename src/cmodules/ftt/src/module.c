#include <math.h>

#include "buffer.h"
#include "plan.h"
#include "py/runtime.h"
#include "utilities.h"

/**
 * @brief Computes bin statistics
 *
 * @param self_in
 * @param bins_obj
 * @return STATIC
 */
STATIC mp_obj_t bin_stats(mp_obj_t bins_obj) {
  mp_float_t sum = 0;
  mp_float_t max = 0;
  size_t max_idx = 0;

  // assume that the bins object is iterable
  mp_obj_iter_buf_t iter_buf;
  mp_obj_t iterable = mp_getiter(bins_obj, &iter_buf);
  mp_obj_t item;

  // iterate over the bins tracking stats
  size_t idx = 0;
  while (((item = mp_iternext(iterable)) != MP_OBJ_STOP_ITERATION)) {
    mp_float_t val;
    bool result = mp_obj_get_float_maybe(item, &val);
    if (true != result) {
      mp_raise_TypeError(NULL);
    }

    sum += val;
    if (val > max) {
      max = val;
      max_idx = idx;
    }

    // increment the index counter
    idx++;
  }

  // return statistics as a tuple
  const size_t num_items = 3;
  mp_obj_t items[num_items];
  items[0] = mp_obj_new_float(sum);
  items[1] = mp_obj_new_float(max);
  items[2] = mp_obj_new_int(max_idx);

  return mp_obj_new_tuple(num_items, items);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(bin_stats_obj, bin_stats);

// Define all properties of the module.
// Table entries are key/value pairs of the attribute name (a string)
// and the MicroPython object reference.
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
STATIC const mp_rom_map_elem_t module_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_fft)},
    {MP_OBJ_NEW_QSTR(MP_QSTR_FftPlan), (mp_obj_t)&FftPlan_type},

    {MP_ROM_QSTR(MP_QSTR_bin_stats), MP_ROM_PTR(&bin_stats_obj)},
};
STATIC MP_DEFINE_CONST_DICT(module_globals, module_globals_table);

// Define module object.
const mp_obj_module_t fft_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&module_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_fft, fft_module);
