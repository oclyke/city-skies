#pragma once

#include "py/obj.h"
#include "py/runtime.h"
#include "sicgl/color_sequence.h"

// declare the type
const mp_obj_type_t ColorSequence_type;

// underlying data comes from sicgl definition
typedef struct _ColorSequence_obj_t {
  mp_obj_base_t base;
  mp_obj_t colors;      // iterable type representing the colors in the sequence
  mp_obj_t type;        // type of sequence
  sequence_map_fn map;  // scalar to color map function
} ColorSequence_obj_t;

// utility for getting underlying data
STATIC inline ColorSequence_obj_t* color_sequence_from_obj(mp_obj_t o) {
  if (!mp_obj_is_type(o, &ColorSequence_type)) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }
  return MP_OBJ_TO_PTR(o);
}

// utilities for c bindings
int color_sequence_get(
    ColorSequence_obj_t* sequence, size_t* length, color_t* colors_out,
    size_t size);
