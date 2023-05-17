#include <math.h>
#include <stdio.h>
#include <errno.h>

#include "pysicgl/field.h"
#include "pysicgl/screen.h"
#include "fields/sinusoids.h"
#include "py/runtime.h"

/**
 * @brief Extracts the value of a scalar mp_obj_t object into a double
 * 
 * @param obj 
 * @param value 
 * @return STATIC 
 */
STATIC int extract_double_obj(mp_obj_t obj, double* value) {
  int ret = 0;
  if (mp_obj_is_float(obj)) {
    *value = mp_obj_get_float(obj);
  } else if (mp_obj_is_int(obj)) {
    *value = mp_obj_get_int(obj);
  } else {
    ret = -EINVAL;
    goto out;
  }

out:
  return ret;
}

/**
 * @brief Extracts floating point values from a 2-tuple into doubles.
 * 
 * @param obj 
 * @param u 
 * @param v 
 * @return STATIC 
 */
STATIC int unpack_double_tuple2(mp_obj_t obj, double* u, double* v) {
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
    ret = extract_double_obj(tuple->items[0], u);
    if (0 != ret) {
      goto out;
    }
  }
  if (NULL != v) {
    ret = extract_double_obj(tuple->items[1], v);
    if (0 != ret) {
      goto out;
    }
  }

out:
  return ret;
}

int extract_screen_bounds_double(Screen_obj_t* screen_obj, ext_t* max, double* u, double*v) {
  int ret = 0;

  if (NULL == screen_obj) {
    ret = -ENOMEM;
    goto out;
  }
  screen_t* screen = screen_obj->screen;

  // determine the larger of the dimensions
  ext_t largest = (screen->width > screen->height) ? screen->width : screen->height;

  if (NULL != max) {
    *max = largest;
  }

  if (NULL != u) {
    *u = ((double)screen->width / largest);
  }

  if (NULL != v) {
    *v = ((double)screen->height / largest);
  }

out:
  return ret;
}

/////////////////////////////
// Field Generation Functions


STATIC mp_obj_t sinusoids(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_screen,
    ARG_field,
    ARG_center,
    ARG_scale,
    ARG_frequency,
    ARG_offset,
    ARG_decay,
  };

  Screen_obj_t* screen = screen_from_obj(args[ARG_screen]);
  ScalarField_obj_t* field = scalar_field_from_obj(args[ARG_field]);

  ext_t width = screen->screen->width;
  // ext_t height = screen->screen->height;

  // get the center location
  double cu, cv;
  int ret = unpack_double_tuple2(args[ARG_center], &cu, &cv);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  // get the scale
  double scale;
  ret = extract_double_obj(args[ARG_scale], &scale);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  // get the frequency
  double frequency;
  ret = extract_double_obj(args[ARG_frequency], &frequency);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  // get the offset
  double offset;
  ret = extract_double_obj(args[ARG_offset], &offset);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  // get the decay
  double decay;
  ret = extract_double_obj(args[ARG_decay], &decay);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  if (decay == -1) {
    decay = 0;
  }

  // find screen bounds
  ext_t max_dim;
  ret = extract_screen_bounds_double(screen, &max_dim, NULL, NULL);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  // compute the scalar field
  for (size_t idx = 0; idx < field->length; idx++) {
    double u = ((double)(idx % width)) / max_dim;
    double v = ((double)(idx / width)) / max_dim;

    double du = (u - cu);
    double dv = (v - cv);

    double radius = sqrt(pow(du, 2.0) + pow(dv, 2.0));

    double scalar = (scale * (1.0 / (decay * radius + 1.0)) * sin(frequency * radius)) + offset;

    field->scalars[idx] = scalar;
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(sinusoids_obj, 7, 7, sinusoids);

// Define all properties of the module.
// Table entries are key/value pairs of the attribute name (a string)
// and the MicroPython object reference.
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
STATIC const mp_rom_map_elem_t module_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_buffer)},
    {MP_OBJ_NEW_QSTR(MP_QSTR_sinusoids), (mp_obj_t)&sinusoids_obj},
};
STATIC MP_DEFINE_CONST_DICT(module_globals, module_globals_table);

// Define module object.
const mp_obj_module_t fieldgen_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&module_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_fieldgen, fieldgen_module);
