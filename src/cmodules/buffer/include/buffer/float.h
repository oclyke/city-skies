#pragma once

#include "py/obj.h"
#include "py/runtime.h"

// declare the type
extern const mp_obj_type_t FloatBuffer_type;

// define the underlying data structure
typedef struct _FloatBuffer_obj_t {
  mp_obj_base_t base;
  float* elements;
  size_t length;
} FloatBuffer_obj_t;

// utility for getting underlying data
STATIC inline FloatBuffer_obj_t* float_buffer_from_obj(mp_obj_t o) {
  if (!mp_obj_is_type(o, &FloatBuffer_type)) {
    mp_raise_TypeError(NULL);
  }
  return MP_OBJ_TO_PTR(o);
}
