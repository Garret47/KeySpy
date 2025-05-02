#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include "keylogger/utils/key_names.h"


const char* get_key_name(xkb_keysym_t keysym) {
    switch (keysym) {
        case XKB_KEY_Return: return "\n";
        case XKB_KEY_Escape: return "[ESC]";
        case XKB_KEY_Tab: return "\t";
        case XKB_KEY_BackSpace: return "[BackSpace]";
        default: return NULL;
    }
}

int get_key_string(xkb_keysym_t keysym, char *buffer, int buffer_len){
    const char *name = get_key_name(keysym);
    if (name) {
        strncpy(buffer, name, buffer_len - 1);
        buffer[buffer_len - 1] = '\0';
        return 0;
    }
    int len = xkb_keysym_to_utf8(keysym, buffer, buffer_len);
    if (len == 0){
        char keysym_name[64];
        xkb_keysym_get_name(keysym, keysym_name, sizeof(keysym_name));
        snprintf(buffer, buffer_len, "[%s]", keysym_name);
        return 0;
    }
    if (len + 1 > buffer_len){
        return 1;
    }
    return 0;
}