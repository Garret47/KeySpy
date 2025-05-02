#pragma once

#include <xkbcommon/xkbcommon.h>

const char* get_key_name(xkb_keysym_t keysym);
int get_key_string(xkb_keysym_t keysym, char *buffer, int buffer_len);
