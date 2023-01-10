#include "pysicgl/drawing/interface.h"

#include <stdio.h>

#include "pysicgl/interface.h"
#include "pysicgl/utilities.h"
#include "sicgl/domain/interface.h"

mp_obj_t interface_fill(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_color,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  int ret = sicgl_interface_fill(
      &self->interface, mp_obj_get_int(args[ARG_color]));
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}

mp_obj_t interface_pixel(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_color,
    ARG_coordinates,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  ext_t u, v;
  int ret = unpack_ext_t_tuple2(args[ARG_coordinates], &u, &v);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = sicgl_interface_pixel(
      &self->interface, mp_obj_get_int(args[ARG_color]), u, v);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}

mp_obj_t interface_line(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_color,
    ARG_from,
    ARG_to,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  ext_t u0, v0, u1, v1;
  int ret = unpack_ext_t_tuple2(args[ARG_from], &u0, &v0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = unpack_ext_t_tuple2(args[ARG_to], &u1, &v1);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = sicgl_interface_line(
      &self->interface, mp_obj_get_int(args[ARG_color]), u0, v0, u1, v1);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}

mp_obj_t interface_rectangle(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_color,
    ARG_from,
    ARG_to,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  ext_t u0, v0, u1, v1;
  int ret = unpack_ext_t_tuple2(args[ARG_from], &u0, &v0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = unpack_ext_t_tuple2(args[ARG_to], &u1, &v1);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = sicgl_interface_rectangle(
      &self->interface, mp_obj_get_int(args[ARG_color]), u0, v0, u1, v1);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}

mp_obj_t interface_rectangle_filled(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_color,
    ARG_from,
    ARG_to,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  ext_t u0, v0, u1, v1;
  int ret = unpack_ext_t_tuple2(args[ARG_from], &u0, &v0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = unpack_ext_t_tuple2(args[ARG_to], &u1, &v1);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = sicgl_interface_rectangle_filled(
      &self->interface, mp_obj_get_int(args[ARG_color]), u0, v0, u1, v1);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}

mp_obj_t interface_circle(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_color,
    ARG_center,
    ARG_diameter,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  ext_t u0, v0;
  int ret = unpack_ext_t_tuple2(args[ARG_center], &u0, &v0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = sicgl_interface_circle_ellipse(
      &self->interface, mp_obj_get_int(args[ARG_color]), u0, v0,
      mp_obj_get_int(args[ARG_diameter]));
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}

mp_obj_t interface_ellipse(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_color,
    ARG_center,
    ARG_semis,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  ext_t u0, v0, semiu, semiv;
  int ret = unpack_ext_t_tuple2(args[ARG_center], &u0, &v0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = unpack_ext_t_tuple2(args[ARG_semis], &semiu, &semiv);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = sicgl_interface_ellipse(
      &self->interface, mp_obj_get_int(args[ARG_color]), u0, v0, semiu, semiv);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  return mp_const_none;
}
