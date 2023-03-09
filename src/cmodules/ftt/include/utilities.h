#pragma once

#include "fft.h"
#include "py/obj.h"
#include "sicgl/extent.h"

int extract_float_obj(mp_obj_t obj, mp_float_t* value);
int unpack_float_tuple2(mp_obj_t obj, mp_float_t* u, mp_float_t* v);
int interpolate_linear(
    float* array, size_t length, double phase, double* output);
