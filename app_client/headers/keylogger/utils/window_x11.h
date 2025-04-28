#ifndef Keylogger_Utils_WindowX11_H_SENTRY
#define Keylogger_Utils_WindowX11_H_SENTRY

#include <X11/Xlib.h>

int get_active_window(Display *d, char **window);

#endif
