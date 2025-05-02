#pragma once

#include <X11/Xlib.h>
#include <X11/Xmu/WinUtil.h>

int get_active_window(Display *d, char **window);
