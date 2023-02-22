#pragma once

#include "py/obj.h"
#include "sicgl/extent.h"
#include "fft.h"

int extract_float_obj(mp_obj_t obj, mp_float_t* value);
int unpack_float_tuple2(mp_obj_t obj, mp_float_t* u, mp_float_t* v);
int interpolate_real_outputs_linear(fft_config_t* config, double phase, double* output);
