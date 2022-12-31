#include "pysicgl/field.h"

#include "pysicgl/color_sequence.h"
#include "pysicgl/drawing/blit.h"
#include "pysicgl/interface.h"
#include "pysicgl/screen.h"
#include "pysicgl/utilities.h"
#include "sicgl/field.h"

mp_obj_t scalar_field(size_t n_args, const mp_obj_t* args) {
  // parse args
  enum {
    ARG_interface,
    ARG_field,
    ARG_scalar_field,
    ARG_color_sequence,
  };
  Interface_obj_t* self = MP_OBJ_TO_PTR(args[ARG_interface]);
  Screen_obj_t* field = screen_from_obj(args[ARG_field]);
  ColorSequence_obj_t* pysequence =
      color_sequence_from_obj(args[ARG_color_sequence]);
  ScalarField_obj_t* scalar_field =
      scalar_field_from_obj(args[ARG_scalar_field]);

  // get length of color sequence
  size_t len;
  int ret = color_sequence_get(pysequence, &len, NULL, 0);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  // allocate sequence on stack
  color_t colors[len];
  ret = color_sequence_get(pysequence, NULL, colors, len);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }
  color_sequence_t sequence = {
      .colors = colors,
      .length = len,
  };

  // apply the field
  ret = sicgl_scalar_field(
      &self->interface, field->screen, scalar_field->scalars, &sequence,
      pysequence->map);
  if (0 != ret) {
    mp_raise_OSError(ret);
  }

  return mp_const_none;
}
