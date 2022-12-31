#pragma once

#include "py/obj.h"
#include "sicgl/extent.h"

int extract_ext_t_obj(mp_obj_t obj, ext_t* value);
int unpack_ext_t_tuple2(mp_obj_t obj, ext_t* u, ext_t* v);
