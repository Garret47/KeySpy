#pragma once

typedef struct {
    int width;
    int height;
    int bits_per_pixel;
    unsigned char *image_data;
} ImageData;

typedef struct {
    int pid;
    char name[256];
    char state;
    unsigned long memory;
    float cpu_usage;
} process_info;

int create_screenshot(int sock);
int info_cpu(int sock);
int info_memory(int sock);
int info_process(int sock);
int info_disk(int sock);
int info_network(int sock);
int info_uptime(int sock);
int info_sys(int sock);
