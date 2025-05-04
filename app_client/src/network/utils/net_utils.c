#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <errno.h>
#include <sys/select.h>
#include "network/utils/net_utils.h"
#include "core_state.h"

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
    printf("Connect to server addr: %s, port: %s\n", ip, port);

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