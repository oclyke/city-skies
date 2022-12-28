#pragma once

#include "py/obj.h"
#include "pychinvat/system/firmware.h"
#include "pychinvat/system/hardware.h"
#include "pychinvat/system/identity.h"
#include "pychinvat/system/network.h"
#include "pychinvat/system/uuidv4.h"
#include "pychinvat/system/version.h"

// declare the type
const mp_obj_type_t System_SystemInfo_type;
