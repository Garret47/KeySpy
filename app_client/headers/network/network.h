#pragma once

int init_connection(const char *ip, const char *port);
int reconnect(int *sock, const char *ip, const char *port);
int safe_send(int sock, const void *buf, size_t len);
void *tcp_client_thread(void *arg);
