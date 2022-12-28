#include "pysicgl/utilities.h"
#include "py/runtime.h"

#include <errno.h>

int extract_ext_t_obj(mp_obj_t obj, ext_t* value) {
  int ret = 0;
  if (mp_obj_is_float(obj)) {
    *value = (ext_t)mp_obj_get_float(obj);
  } else if (mp_obj_is_int(obj)) {
    *value = mp_obj_get_int(obj);
  } else {
    ret = -EINVAL;
    goto out;
  }

out:
  return ret;
}

int unpack_ext_t_tuple2(mp_obj_t obj, ext_t* u, ext_t* v) {
  int ret = 0;
  if (!mp_obj_is_type(obj, &mp_type_tuple)) {
    ret = -EINVAL;
    goto out;
  }
  mp_obj_tuple_t* tuple = MP_OBJ_TO_PTR(obj);
  if (2 != tuple->len) {
    ret = -EINVAL;
    goto out;
  }
  if (NULL != u) {
    ret = extract_ext_t_obj(tuple->items[0], u);
    if (0 != ret) {
      goto out;
    }
  }
  if (NULL != v) {
    ret = extract_ext_t_obj(tuple->items[1], v);
    if (0 != ret) {
      goto out;
    }
  }

out:
  return ret;
}
