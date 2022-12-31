#include <stdlib.h>

#include "py/binary.h"
#include "py/objarray.h"
#include "py/runtime.h"
#include "pysicgl.h"
#include "pysicgl/color_sequence.h"
#include "pysicgl/interface.h"
#include "pysicgl/screen.h"

// module methods
STATIC mp_obj_t allocate_memory(mp_obj_t obj) {
  // allocate memory
  // the amount of memory allocated is determined according to the type of the
  // argument
  size_t pixels = 0;
  if (mp_obj_is_int(obj)) {
    // allocate the specified number of pixels
    mp_int_t desired = mp_obj_get_int(obj);
    if (desired <= 0) {
      mp_raise_ValueError(NULL);
    }
    pixels = desired;
  } else if (mp_obj_get_type(obj) == &Screen_type) {
    Screen_obj_t* screen = screen_from_obj(obj);
    if (NULL == screen->screen) {
      mp_raise_ValueError(NULL);
    }
    ext_t desired = screen->screen->width * screen->screen->height;
    if (desired <= 0) {
      mp_raise_ValueError(NULL);
    }
    pixels = desired;
  } else {
    mp_raise_TypeError(NULL);
  }

  // allocate memory
  // not sure if this could be a memory leak... will the memory be freed when
  // the bytearray is collected?
  size_t bpp = bytes_per_pixel();
  size_t len = pixels * bpp;
  void* mem = m_malloc(len);
  memset(mem, 0, len);
  return mp_obj_new_bytearray_by_ref(bpp * pixels, mem);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(allocate_memory_obj, allocate_memory);

// module
STATIC const mp_map_elem_t sicgl_globals_table[] = {
    {MP_OBJ_NEW_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_sicgl)},

    // methods
    {MP_OBJ_NEW_QSTR(MP_QSTR_allocate_memory),
     (mp_obj_t)MP_ROM_PTR(&allocate_memory_obj)},

    // classes
    {MP_OBJ_NEW_QSTR(MP_QSTR_ColorSequence), (mp_obj_t)&ColorSequence_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_Screen), (mp_obj_t)&Screen_type},
    {MP_OBJ_NEW_QSTR(MP_QSTR_Interface), (mp_obj_t)&Interface_type},
};
STATIC MP_DEFINE_CONST_DICT(sicgl_globals, sicgl_globals_table);

const mp_obj_module_t sicgl_module = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t*)&sicgl_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_sicgl, sicgl_module);
