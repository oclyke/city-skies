#pragma once

#include "py/obj.h"
#include "py/runtime.h"

mp_obj_t interface_fill(size_t n_args, const mp_obj_t* args);
mp_obj_t interface_pixel(size_t n_args, const mp_obj_t* args);
mp_obj_t interface_line(size_t n_args, const mp_obj_t* args);
mp_obj_t interface_rectangle(size_t n_args, const mp_obj_t* args);
mp_obj_t interface_rectangle_filled(size_t n_args, const mp_obj_t* args);
mp_obj_t interface_circle(size_t n_args, const mp_obj_t* args);
mp_obj_t interface_ellipse(size_t n_args, const mp_obj_t* args);
