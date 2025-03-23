#ifndef KeyboardHandler_H_SENTRY
#define KeyboardHandler_H_SENTRY

#include <xkbcommon/xkbcommon.h>
#include <xkbcommon/xkbcommon-x11.h>
#include <X11/Xlib.h>
#include <X11/Xlib-xcb.h>


typedef struct {
    Display *dpy;
    xcb_connection_t *xcb_conn;
    struct xkb_context *ctx;
    struct xkb_keymap *keymap;
    struct xkb_state *state;
    int device_id;
    char *active_window;
} KeyboardHandler;

int KeyboardHandler_init(KeyboardHandler *handler);
void KeyboardHandler_cleanup(KeyboardHandler *handler);
int get_active_window(Display *display, char **window);

#endif