#pragma once

#include "py/obj.h"
#include "py/runtime.h"

mp_obj_t global_pixel(size_t n_args, const mp_obj_t* args);
mp_obj_t global_line(size_t n_args, const mp_obj_t* args);
mp_obj_t global_rectangle(size_t n_args, const mp_obj_t* args);
mp_obj_t global_circle(size_t n_args, const mp_obj_t* args);
mp_obj_t global_ellipse(size_t n_args, const mp_obj_t* args);
