#pragma once

#include "py/obj.h"
#include "py/runtime.h"
#include "sicgl/screen.h"

// declare the type
const mp_obj_type_t Screen_type;

// underlying data comes from sicgl definition
typedef struct _Screen_obj_t {
  mp_obj_base_t base;

  // the screen pointer allows this object to act as a reference
  // when acting as an object rather than a reference the pointer
  // will point to the internal reference
  screen_t* screen;
  screen_t _screen;

  // a flag to explicitly indicate whether this is an object or reference
  bool _is_reference;
} Screen_obj_t;

// utility for getting underlying data
STATIC inline Screen_obj_t* screen_from_obj(mp_obj_t o) {
  if (!mp_obj_is_type(o, &Screen_type)) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }
  return MP_OBJ_TO_PTR(o);
}

mp_obj_t new_screen(screen_t* reference);
