#pragma once

#include "fft.h"
#include "py/obj.h"
#include "sicgl/extent.h"

int interpolate_float_array_linear(
    float* array, size_t length, double phase, double* output);
