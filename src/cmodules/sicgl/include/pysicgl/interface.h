#pragma once

#include "py/obj.h"
#include "py/runtime.h"
#include "sicgl/interface.h"

// declare the type
extern const mp_obj_type_t Interface_type;

// underlying data comes from sicgl definition
typedef struct _Interface_obj_t {
  mp_obj_base_t base;
  interface_t interface;
} Interface_obj_t;

STATIC inline Interface_obj_t* interface_from_obj(mp_obj_t o) {
  if (!mp_obj_is_type(o, &Interface_type)) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }
  return MP_OBJ_TO_PTR(o);
}
