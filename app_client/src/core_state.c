#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include "core_state.h"

_Atomic sig_atomic_t exit_flag = 0;
int pipe_fd_email[2];
int pipe_fd_network[2];

void signal_handler(int sig) {
    if (sig == SIGINT) {
        exit_flag = 1;
        char signal_data = 'x';
        while (write(pipe_fd_email[1], &signal_data, 1) == -1 && errno == EINTR);
        while (write(pipe_fd_network[1], &signal_data, 1) == -1 && errno == EINTR);
    }
}

int init_state() {
    struct sigaction sa;

    if (pipe(pipe_fd_email) == -1 || pipe(pipe_fd_network) == -1) {
        fprintf(stderr, "Failed to create pipe\n");
        return 1;
    }

    sa.sa_handler = signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;

    if (sigaction(SIGINT, &sa, NULL) == -1) {
        fprintf(stderr, "Error registering signal handler\n");
        return 1;
    }

    return 0;
}