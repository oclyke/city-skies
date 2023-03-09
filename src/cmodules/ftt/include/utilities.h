#pragma once

#include "fft.h"
#include "py/obj.h"
#include "sicgl/extent.h"

int unpack_float_tuple2(mp_obj_t obj, mp_float_t* u, mp_float_t* v);
int interpolate_linear(
    float* array, size_t length, double phase, double* output);
