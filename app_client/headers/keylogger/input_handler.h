#pragma once

#include <X11/Xlib.h>

typedef struct {
    Display *display;
    int xi_opcode;
    Atom net_active_window_atom;
} InputHandler;

int InputHandler_init(InputHandler *handler);
void InputHandler_cleanup(InputHandler *handler);
