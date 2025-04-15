#ifndef CoreSignal_H_SENTRY
#define CoreSignal_H_SENTRY

#include <stdatomic.h>
#include <signal.h>

extern _Atomic sig_atomic_t exit_flag;
extern int pipe_fd_email[2];
extern int pipe_fd_network[2];

void signal_handler(int sig);
int init_state();

#endif