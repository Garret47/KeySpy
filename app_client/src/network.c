#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <errno.h>
#include <sys/select.h>
#include <pthread.h>
#include "core_state.h"

#ifndef SERVER_IP
#error "SERVER_IP is not defined"
#endif

#ifndef SERVER_PORT_STR
#error "SERVER_PORT_STR is not defined"
#endif

#define BUFFER_SIZE_READ 2048
#define DURATION_RETRY_CONNECT 10

int init_connection(const char *ip, const char *port) {
    struct addrinfo hints, *res;
    int sock;

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    int status = getaddrinfo(ip, port, &hints, &res);
    if (status != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(status));
        return -1;
    }

    sock = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    if (sock < 0) {
        perror("socket");
        freeaddrinfo(res);
        return -1;
    }

    char hostname[256];
    if (gethostname(hostname, sizeof(hostname)) == -1) {
        perror("gethostname");
        strcpy(hostname, "Unknown");
    }

    while (connect(sock, res->ai_addr, res->ai_addrlen) < 0) {
        perror("connect");
        fd_set read_fds;
        struct timeval tv;

        FD_ZERO(&read_fds);
        FD_SET(pipe_fd_network[0], &read_fds);
        tv.tv_sec = DURATION_RETRY_CONNECT;
        tv.tv_usec = 0;

        int select_result = select(pipe_fd_network[0] + 1, &read_fds, NULL, NULL, &tv);

        if (select_result > 0){
            char buffer[10];
            read(pipe_fd_network[0], buffer, sizeof(buffer));
            close(sock);
            freeaddrinfo(res);
            return -1;
        }
        if (exit_flag){
            close(sock);
            freeaddrinfo(res);
            return -1;
        }
    }

    send(sock, hostname, strlen(hostname), MSG_NOSIGNAL);

    freeaddrinfo(res);
    return sock;
}

int reconnect(int *sock, const char *ip, const char *port) {
    if (*sock >= 0) {
        close(*sock);
    }
    *sock = init_connection(ip, port);
    return (*sock >= 0) ? 0 : 1;
}

int safe_send(int sock, const void *buf, size_t len) {
    size_t total_sent = 0;
    const unsigned char *ptr = buf;

    while (total_sent < len && !exit_flag) {
        ssize_t sent = send(sock, ptr + total_sent, len - total_sent, 0);
        if (sent <= 0) {
            if (errno == EPIPE || errno == ECONNRESET) {
                fprintf(stderr, "Connection closed by peer.\n");
                return 1;
            }

            perror("send");
            return -1;
        }

        total_sent += sent;
    }

    return 0;
}

void *tcp_client_thread(void *arg) {
    char buffer[BUFFER_SIZE_READ];
    int sock = -1;
    fd_set read_fds;

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

            if (bytes_received == 0) {
                printf("Server closed the connection\n");
                if (exit_flag || reconnect(&sock, SERVER_IP, SERVER_PORT_STR)) break;
            } else if (bytes_received < 0) {
                perror("Error receiving data");
                break;
            } else {
                printf("Command received: %s\n", buffer);

                const char *response = "Hello World";
                int send_status = safe_send(sock, response, strlen(response));

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

    pthread_exit((void *)0);
}