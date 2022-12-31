#pragma once

#include "py/obj.h"
#include "py/runtime.h"

mp_obj_t screen_pixel(size_t n_args, const mp_obj_t *args);
mp_obj_t screen_line(size_t n_args, const mp_obj_t *args);
mp_obj_t screen_rectangle(size_t n_args, const mp_obj_t *args);
mp_obj_t screen_circle(size_t n_args, const mp_obj_t *args);
mp_obj_t screen_ellipse(size_t n_args, const mp_obj_t *args);
