#include "pysicgl/drawing/blit.h"
#include "pysicgl/utilities.h"
#include "pysicgl/interface.h"
#include "pysicgl/screen.h"
#include "sicgl/blit.h"


#include <stdio.h>

mp_obj_t blit(size_t n_args, const mp_obj_t *args) {
  // parse args
  enum {
    ARG_interface,
    ARG_screen,
    ARG_sprite,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  Screen_obj_t* screen = screen_from_obj(args[ARG_screen]);
  mp_buffer_info_t sprite_info;
  mp_get_buffer_raise(args[ARG_sprite], &sprite_info, MP_BUFFER_READ);
  int ret = sicgl_blit(&self->interface, screen->screen, sprite_info.buf);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}
