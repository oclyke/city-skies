#include "pysicgl/drawing/screen.h"

#include "pysicgl/interface.h"
#include "pysicgl/screen.h"
#include "pysicgl/utilities.h"
#include "sicgl/domain/screen.h"

mp_obj_t screen_fill(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_screen,
    ARG_color,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  Screen_obj_t* screen = screen_from_obj(args[ARG_screen]);
  int ret = sicgl_screen_fill(
      &self->interface, screen->screen, mp_obj_get_int(args[ARG_color]));
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}

mp_obj_t screen_pixel(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_screen,
    ARG_color,
    ARG_coordinates,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  Screen_obj_t* screen = screen_from_obj(args[ARG_screen]);
  ext_t u, v;
  int ret = unpack_ext_t_tuple2(args[ARG_coordinates], &u, &v);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = sicgl_screen_pixel(
      &self->interface, screen->screen, mp_obj_get_int(args[ARG_color]), u, v);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}

mp_obj_t screen_line(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_screen,
    ARG_color,
    ARG_from,
    ARG_to,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  Screen_obj_t* screen = screen_from_obj(args[ARG_screen]);
  ext_t u0, v0, u1, v1;
  int ret = unpack_ext_t_tuple2(args[ARG_from], &u0, &v0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = unpack_ext_t_tuple2(args[ARG_to], &u1, &v1);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = sicgl_screen_line(
      &self->interface, screen->screen, mp_obj_get_int(args[ARG_color]), u0, v0,
      u1, v1);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}

mp_obj_t screen_rectangle(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_screen,
    ARG_color,
    ARG_from,
    ARG_to,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  Screen_obj_t* screen = screen_from_obj(args[ARG_screen]);
  ext_t u0, v0, u1, v1;
  int ret = unpack_ext_t_tuple2(args[ARG_from], &u0, &v0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = unpack_ext_t_tuple2(args[ARG_to], &u1, &v1);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = sicgl_screen_rectangle(
      &self->interface, screen->screen, mp_obj_get_int(args[ARG_color]), u0, v0,
      u1, v1);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}

mp_obj_t screen_rectangle_filled(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_screen,
    ARG_color,
    ARG_from,
    ARG_to,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  Screen_obj_t* screen = screen_from_obj(args[ARG_screen]);
  ext_t u0, v0, u1, v1;
  int ret = unpack_ext_t_tuple2(args[ARG_from], &u0, &v0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = unpack_ext_t_tuple2(args[ARG_to], &u1, &v1);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = sicgl_screen_rectangle_filled(
      &self->interface, screen->screen, mp_obj_get_int(args[ARG_color]), u0, v0,
      u1, v1);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}

mp_obj_t screen_circle(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_screen,
    ARG_color,
    ARG_center,
    ARG_diameter,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  Screen_obj_t* screen = screen_from_obj(args[ARG_screen]);
  ext_t u0, v0;
  int ret = unpack_ext_t_tuple2(args[ARG_center], &u0, &v0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = sicgl_screen_circle_ellipse(
      &self->interface, screen->screen, mp_obj_get_int(args[ARG_color]), u0, v0,
      mp_obj_get_int(args[ARG_diameter]));
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}

mp_obj_t screen_ellipse(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_screen,
    ARG_color,
    ARG_center,
    ARG_semis,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  Screen_obj_t* screen = screen_from_obj(args[ARG_screen]);
  ext_t u0, v0, semiu, semiv;
  int ret = unpack_ext_t_tuple2(args[ARG_center], &u0, &v0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = unpack_ext_t_tuple2(args[ARG_semis], &semiu, &semiv);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = sicgl_screen_ellipse(
      &self->interface, screen->screen, mp_obj_get_int(args[ARG_color]), u0, v0,
      semiu, semiv);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}
