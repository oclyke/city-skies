#pragma once

#include "py/obj.h"
#include "py/runtime.h"
#include "sicgl/screen.h"

// declare the type
extern const mp_obj_type_t ScalarField_type;

// underlying data comes from sicgl definition
typedef struct _ScalarField_obj_t {
  mp_obj_base_t base;
  double* scalars;
  size_t length;
} ScalarField_obj_t;

// utility for getting underlying data
STATIC inline ScalarField_obj_t* scalar_field_from_obj(mp_obj_t o) {
  if (!mp_obj_is_type(o, &ScalarField_type)) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }
  return MP_OBJ_TO_PTR(o);
}
