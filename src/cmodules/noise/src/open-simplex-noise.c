#include <errno.h>
#include <stdio.h>

#include "cnoise/open-simplex.h"
#include "py/runtime.h"
#include "pysicgl/field.h"
#include "pysicgl/screen.h"

STATIC int unpack_float_tuple2(mp_obj_t obj, mp_float_t* u, mp_float_t* v) {
  int ret = 0;
  if (!mp_obj_is_type(obj, &mp_type_tuple)) {
    ret = -EINVAL;
    goto out;
  }
  mp_obj_tuple_t* tuple = MP_OBJ_TO_PTR(obj);
  if (2 != tuple->len) {
    ret = -EINVAL;
    goto out;
  }
  if (NULL != u) {
    bool result = mp_obj_get_float_maybe(tuple->items[0], u);
    if (true != result) {
      goto out;
    }
  }
  if (NULL != v) {
    bool result = mp_obj_get_float_maybe(tuple->items[1], v);
    if (true != result) {
      goto out;
    }
  }

out:
  return ret;
}

STATIC mp_float_t float_from_obj(mp_obj_t obj) {
  if (mp_obj_is_type(obj, &mp_type_float)) {
    return mp_obj_float_get(obj);
  } else if (mp_obj_is_integer(obj)) {
    return (mp_float_t)mp_obj_get_int(obj);
  } else {
    mp_raise_ValueError(NULL);
    return (mp_float_t)0.0;
  }
  return (mp_float_t)0.0;
}

STATIC void unpack_vector(
    mp_obj_t coords, mp_float_t* x, mp_float_t* y, mp_float_t* z) {
  if ((x == NULL) || (y == NULL) || (z == NULL)) {
    mp_raise_ValueError(NULL);
  }
  if (!mp_obj_is_type(coords, &mp_type_tuple)) {
    mp_raise_TypeError(NULL);
  }
  mp_obj_tuple_t* tuple = MP_OBJ_TO_PTR(coords);
  if (tuple->len != 3) {
    mp_raise_ValueError(NULL);
  }
  *x = float_from_obj(tuple->items[0]);
  *y = float_from_obj(tuple->items[1]);
  *z = float_from_obj(tuple->items[2]);
}

STATIC mp_obj_t noise_at(mp_obj_t self_in, mp_obj_t coordinates) {
  open_simplex_noise_obj_t* self = open_simplex_noise_from_obj(self_in);

  if (self->osn_ctx == NULL) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }

  mp_float_t x, y, z;
  unpack_vector(coordinates, &x, &y, &z);

  mp_float_t value;
  // value = open_simplex_noise4(self->osn_ctx, (double) x / FEATURE_SIZE,
  // (double) y / FEATURE_SIZE, 0.0, 0.0);
  value = open_simplex_noise3(self->osn_ctx, (double)x, (double)y, (double)z);
  // value = open_simplex_noise2(self->osn_ctx, (double)x, (double)y);

  return mp_obj_new_float(value);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(noise_at_obj, noise_at);

STATIC mp_obj_t get_1d(size_t n_args, const mp_obj_t* args) {
  mp_raise_NotImplementedError(NULL);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(get_1d_obj, 0, 0, get_1d);

STATIC mp_obj_t fill_scalar_field(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_self,
    ARG_scalar_field,
    ARG_screen,
    ARG_z,
    ARG_scale,
    ARG_center,
  };
  open_simplex_noise_obj_t* self = open_simplex_noise_from_obj(args[ARG_self]);
  if (self->osn_ctx == NULL) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }

  ScalarField_obj_t* scalar_field =
      scalar_field_from_obj(args[ARG_scalar_field]);
  if (NULL == scalar_field) {
    mp_raise_TypeError(NULL);
  }
  if (NULL == scalar_field->scalars) {
    mp_raise_TypeError(NULL);
  }

  Screen_obj_t* screen = screen_from_obj(args[ARG_screen]);
  if (NULL == screen) {
    mp_raise_TypeError(NULL);
  }

  mp_float_t scalex, scaley;
  mp_float_t centerx, centery;
  int ret = unpack_float_tuple2(args[ARG_scale], &scalex, &scaley);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  ret = unpack_float_tuple2(args[ARG_center], &centerx, &centery);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  mp_float_t z = mp_obj_get_float(args[ARG_z]);

  // determine how many values to get
  size_t count = screen->screen->width * screen->screen->height;
  if (scalar_field->length < count) {
    count = scalar_field->length;
  }

  size_t width = screen->screen->width;
  for (size_t idx = 0; idx < count; idx++) {
    size_t idu = idx % width;
    size_t idv = idx / width;
    double x = ((double)idu - centerx) * scalex;
    double y = ((double)idv - centery) * scaley;
    mp_float_t value = open_simplex_noise3(self->osn_ctx, x, y, z);

    // printf("v: %f\n", value);

    scalar_field->scalars[idx] = (value + 1.0) / 2.0;
  }

  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(
    fill_scalar_field_obj, 6, 6, fill_scalar_field);

STATIC mp_obj_t show_noise(mp_obj_t self_in, mp_obj_t z_in) {
  open_simplex_noise_obj_t* self = open_simplex_noise_from_obj(self_in);

  const size_t WIDTH = 8;
  const size_t HEIGHT = 8;
  const double FEATURE_SIZE = 1.0;

  double x, y, z;
  double value;
  // uint32_t rgb;

  if (z_in == mp_const_none) {
    z = 0;
  } else {
    if (!mp_obj_is_type(z_in, &mp_type_float)) {
      mp_raise_TypeError(NULL);
    }
    z = mp_obj_float_get(z_in);
  }

  if (self->osn_ctx == NULL) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }

  printf("\nnoise at %f:\n", z);
  for (y = 0; y < HEIGHT; y++) {
    for (x = 0; x < WIDTH; x++) {
      value = open_simplex_noise3(
          self->osn_ctx, (double)x / FEATURE_SIZE, (double)y / FEATURE_SIZE, z);

      printf("%f, ", value);
    }
    printf("\n");
  }
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(show_noise_obj, show_noise);

// locals
STATIC const mp_rom_map_elem_t locals_dict_table[] = {
    {MP_ROM_QSTR(MP_QSTR_noise_at), MP_ROM_PTR(&noise_at_obj)},

    {MP_ROM_QSTR(MP_QSTR_get_1d), MP_ROM_PTR(&get_1d_obj)},

    {MP_ROM_QSTR(MP_QSTR_fill_scalar_field),
     MP_ROM_PTR(&fill_scalar_field_obj)},

    {MP_ROM_QSTR(MP_QSTR_show_noise), MP_ROM_PTR(&show_noise_obj)},
};

STATIC MP_DEFINE_CONST_DICT(locals_dict, locals_dict_table);

STATIC void print(
    const mp_print_t* print, mp_obj_t self_in, mp_print_kind_t kind) {
  (void)kind;
  open_simplex_noise_obj_t* self = MP_OBJ_TO_PTR(self_in);
  mp_print_str(print, "OpenSimplexNoise(seed: ");
  mp_obj_print_helper(print, mp_obj_new_int(self->seed), PRINT_REPR);
  mp_print_str(print, ", ctx: ");
  mp_obj_print_helper(
      print, mp_obj_new_int((mp_int_t)self->osn_ctx), PRINT_REPR);
  mp_print_str(print, ")");
}

STATIC mp_obj_t make_new(
    const mp_obj_type_t* type, size_t n_args, size_t n_kw,
    const mp_obj_t* all_args) {
  // parse args
  enum {
    ARG_seed,
  };
  static const mp_arg_t allowed_args[] = {
      {MP_QSTR_seed, MP_ARG_INT, {.u_int = 77374}},
  };
  mp_map_t kw_args;
  mp_map_init_fixed_table(&kw_args, n_kw, all_args + n_args);
  mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
  mp_arg_parse_all_kw_array(
      n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

  // make self object
  open_simplex_noise_obj_t* self = m_new_obj(open_simplex_noise_obj_t);
  self->base.type = &open_simplex_noise_obj_type;

  self->osn_ctx = NULL;
  self->seed = args[ARG_seed].u_int;
  int status = open_simplex_noise(self->seed, &self->osn_ctx);
  printf("OSN inited with status: %d\n", status);
  if (status != 0) {
    mp_raise_msg(&mp_type_Exception, NULL);
  }

  return MP_OBJ_FROM_PTR(self);
}

const mp_obj_type_t open_simplex_noise_obj_type = {
    {&mp_type_type},
    .name = MP_QSTR_OpenSimplexNoise,
    .print = print,
    .make_new = make_new,
    .locals_dict = (mp_obj_dict_t*)&locals_dict,
};
