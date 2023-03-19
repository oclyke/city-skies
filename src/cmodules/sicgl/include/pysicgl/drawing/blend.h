#pragma once

#include "py/obj.h"
#include "py/runtime.h"

mp_obj_t get_blending_types(void);
mp_obj_t blend(size_t n_args, const mp_obj_t* args);
