#pragma once

#include "open-simplex-noise.h"
#include "py/runtime.h"

// type instance fwd declarations
extern const mp_obj_type_t open_simplex_noise_obj_type;

typedef struct _open_simplex_noise_obj_t {
  mp_obj_base_t base;
  struct osn_context* osn_ctx;
  mp_int_t seed;
} open_simplex_noise_obj_t;

STATIC inline open_simplex_noise_obj_t* open_simplex_noise_from_obj(
    mp_obj_t o) {
  if (!mp_obj_is_type(o, &open_simplex_noise_obj_type)) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }
  return MP_OBJ_TO_PTR(o);
}
