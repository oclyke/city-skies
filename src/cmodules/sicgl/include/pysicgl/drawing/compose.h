#pragma once

#include "py/obj.h"
#include "py/runtime.h"

mp_obj_t get_composition_types(void);
mp_obj_t compose(size_t n_args, const mp_obj_t* args);
