#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <errno.h>
#include <sys/select.h>
#include <pthread.h>
#include "network/utils/net_utils.h"
#include "network/utils/register.h"
#include "network/monitoring.h"
#include "network/network.h"
#include "core_state.h"

#ifndef SERVER_IP
#error "SERVER_IP is not defined"
#endif

#ifndef SERVER_PORT_STR
#error "SERVER_PORT_STR is not defined"
#endif

#define BUFFER_SIZE_READ 2048


void *tcp_client_thread(void *arg) {
    CommandRegistry registry;
    const char *command_names[] = {"create_screenshot", "info_cpu", "info_memory", "info_process", "info_disk",
                                   "info_network", "info_uptime", "info_sys"};
    CommandFunc command_funcs[] = { create_screenshot, info_cpu, info_memory, info_process, info_disk,
                                   info_network, info_uptime, info_sys};

    char buffer[BUFFER_SIZE_READ];
    int sock = -1;
    fd_set read_fds;

    init_registry(&registry);

    for (int i = 0; i < sizeof(command_names) / sizeof(command_names[0]); i++){
        register_command(&registry, command_names[i], command_funcs[i]);
    }

    if (reconnect(&sock, SERVER_IP, SERVER_PORT_STR)) {
        fprintf(stderr, "Failed to connect to server\n");
        pthread_exit((void *)1);
    }

    printf("Connected. Waiting for commands...\n");

    while (!exit_flag) {
        FD_ZERO(&read_fds);
        FD_SET(sock, &read_fds);
        FD_SET(pipe_fd_network[0], &read_fds);

        int max_fd = (sock > pipe_fd_network[0]) ? sock : pipe_fd_network[0];

        if (select(max_fd + 1, &read_fds, NULL, NULL, NULL) < 0) {
            if (errno == EINTR) continue;
            perror("select");
            close(sock);
            pthread_exit((void *)1);
        }

        if (FD_ISSET(pipe_fd_network[0], &read_fds)) {
            char signal_buf;
            read(pipe_fd_network[0], &signal_buf, 1);
            break;
        }

        if (FD_ISSET(sock, &read_fds)) {
            memset(buffer, 0, BUFFER_SIZE_READ);
            ssize_t bytes_received = recv(sock, buffer, BUFFER_SIZE_READ - 1, 0);

            if (bytes_received <= 0) {
                printf("Server closed the connection\n");
                if (exit_flag || reconnect(&sock, SERVER_IP, SERVER_PORT_STR)) break;
            } else {
                printf("Command received: %s\n", buffer);

                int send_status = 0;
                CommandFunc func = get_command(&registry, buffer);
                if (func){
                    send_status = func(sock);
                }

                if (send_status == 1) {
                    fprintf(stderr, "Server disconnected during send. Reconnecting...\n");
                    if (exit_flag || reconnect(&sock, SERVER_IP, SERVER_PORT_STR) < 0) break;
                } else if (send_status < 0) {
                    break;
                }
            }
        }
    }

    if (sock >= 0) {
        close(sock);
    }
    cleanup_registry(&registry);

    pthread_exit((void *)0);
}