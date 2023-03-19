#include "pysicgl/drawing/interface.h"

#include <errno.h>
#include <stdio.h>

#include "pysicgl/interface.h"
#include "pysicgl/utilities.h"
#include "sicgl/domain/interface.h"

static inline color_t clamp_u8(color_t channel) {
  if (channel > 255) {
    return 255;
  } else if (channel < 0) {
    return 0;
  } else {
    return channel;
  }
}

static inline color_t color_scale(color_t color, double scale) {
  // scales only the color components, alpha channel is untouched
  return color_from_channels(
      clamp_u8((color_t)(color_channel_red(color) * scale)),
      clamp_u8((color_t)(color_channel_green(color) * scale)),
      clamp_u8((color_t)(color_channel_blue(color) * scale)),
      color_channel_alpha(color));
}

mp_obj_t interface_scale(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_scale,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  double scale = mp_obj_float_get(args[ARG_scale]);
  color_t* memory = self->interface.memory;
  for (size_t idx = 0; idx < self->interface.length; idx++) {
    memory[idx] = color_scale(memory[idx], scale);
  }

  return mp_const_none;
}

mp_obj_t interface_fill(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_color,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  int ret =
      sicgl_interface_fill(&self->interface, mp_obj_get_int(args[ARG_color]));
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
