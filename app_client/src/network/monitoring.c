#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <unistd.h>
#include <sys/sysinfo.h>
#include <sys/statvfs.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <arpa/inet.h>
#include <dirent.h>
#include <ifaddrs.h>
#include <sys/utsname.h>
#include <netdb.h>
#include <time.h>
#include "network/utils/net_utils.h"
#include "network/monitoring.h"

#define MAX_BUFFER_SIZE 8192
#define MAX_PROC_COUNT 300
#define MAX_PROC_TOP 15
#define MAX_LINE_LENGTH 256
#define BYTES_PER_UNIT 1024
#define CONST_UPTIME 65536.0

#define PROC "/proc"
#define PROC_STAT "/proc/stat"
#define MEMINFO "/proc/meminfo"
#define DISKSTAT "/proc/diskstats"
#define NETWORK "/proc/net/dev"
#define CPU "/proc/cpuinfo"
#define OS_RELEASE "/etc/os-release"

static int prepare_screenshot_buffer(ImageData *data, unsigned char **buffer, size_t *len_buffer){
    size_t header_size = 12;
    size_t image_size = data->width * data->height * (data->bits_per_pixel / 8);
    size_t total_size = header_size + image_size;

    *buffer = (unsigned char *)malloc(total_size);
    if (*buffer == NULL) return 1;

    uint32_t *header = (uint32_t *)(*buffer);
    header[0] = htonl(data->width);
    header[1] = htonl(data->height);
    header[2] = htonl(data->bits_per_pixel);

    memcpy(*buffer + header_size, data->image_data, image_size);
    *len_buffer = total_size;
    return 0;
}


int create_screenshot(int sock) {
    ImageData img;
    Display *display;
    int send_code = 0;
    unsigned char *buffer;
    size_t len_buffer;

    display = XOpenDisplay(NULL);
    if (display == NULL) {
        fprintf(stderr, "Failed to connect to the X server\n");
        return send_code;
    }

    int screen = DefaultScreen(display);
    Window root = RootWindow(display, screen);
    img.width = DisplayWidth(display, screen);
    img.height = DisplayHeight(display, screen);
    printf("Display dimensions: %dx%d\n", img.width, img.height);

    XImage *image = XGetImage(display, root, 0, 0, img.width, img.height, AllPlanes, ZPixmap);
    if (image == NULL) {
        fprintf(stderr, "Failed to create screenshot\n");
        XCloseDisplay(display);
        return send_code;
    }
    img.bits_per_pixel = image->bits_per_pixel;
    img.image_data = (unsigned char *)image->data;

    if (!prepare_screenshot_buffer(&img, &buffer, &len_buffer)){
        send_code = safe_send(sock, buffer, len_buffer);
        free(buffer);
    }

    XDestroyImage(image);
    return send_code;
}

static int get_cpu_load(unsigned char* buffer, size_t *len_buffer){
    FILE *fp;
    char line[MAX_LINE_LENGTH];
    unsigned long long user, nice, system, idle, iowait, irq, softirq, total_cpu_time, total_idle;
    static unsigned long long prev_total = 0, prev_idle = 0;
    float cpu_usage = 0.0;

    fp = fopen(PROC_STAT, "r");
    if (fp == NULL) {
        fprintf(stderr, "Error: Cannot open /proc/stat\n");
        return 1;
    }

    if (fgets(line, MAX_LINE_LENGTH, fp) == NULL) {
        fprintf(stderr, "Error: Cannot read from /proc/stat\n");
        fclose(fp);
        return 1;
    }

    sscanf(line, "cpu %llu %llu %llu %llu %llu %llu %llu", &user, &nice, &system, &idle, &iowait, &irq, &softirq);
    fclose(fp);

    total_cpu_time = user + nice + system + idle + iowait + irq + softirq;
    total_idle = idle + iowait;

    if (prev_total > 0 && total_cpu_time > prev_total) {
        unsigned long long total_diff = total_cpu_time - prev_total;
        unsigned long long idle_diff = total_idle - prev_idle;
        cpu_usage = 100.0 * (1.0 - ((float)idle_diff / (float)total_diff));
    }

    prev_total = total_cpu_time;
    prev_idle = total_idle;

    size_t len = snprintf((char *)buffer, MAX_BUFFER_SIZE,
                      "--------- CPU Load ---------\n"
                      "CPU Load Information:\n"
                      "Current CPU Usage: %.2f%%\n"
                      "User: %llu\n"
                      "Nice: %llu\n"
                      "System: %llu\n"
                      "Idle: %llu\n"
                      "IOWait: %llu\n"
                      "IRQ: %llu\n"
                      "SoftIRQ: %llu\n",
                      cpu_usage, user, nice, system, idle, iowait, irq, softirq);
    *len_buffer = len;

    return 0;
}


int info_cpu(int sock) {
    unsigned char *buffer;
    int send_code = 0;
    size_t len_buffer;
    buffer = (unsigned char *)malloc(MAX_BUFFER_SIZE);
    if (buffer == NULL){
        fprintf(stderr, "Cannot allocate memory for data buffer\n");
        return send_code;
    }
    get_cpu_load(buffer, &len_buffer);
    sleep(1);
    if (get_cpu_load(buffer, &len_buffer)){
        free(buffer);
        return send_code;
    }
    send_code = safe_send(sock, buffer, len_buffer);
    free(buffer);
    return send_code;
}

int info_memory(int sock) {
    FILE *fp;
    char line[256];
    unsigned long mem_total = 0, mem_free = 0, buffers = 0, cached = 0;
    unsigned long swap_total = 0, swap_free = 0;
    unsigned long used_ram = 0, used_swap = 0;
    float ram_usage_percent = 0.0f, swap_usage_percent = 0.0f;
    unsigned char *buffer;
    int send_code = 0;

    buffer = (unsigned char *)malloc(MAX_BUFFER_SIZE);
    if (!buffer) {
        fprintf(stderr, "Cannot allocate memory for data buffer\n");
        return send_code;
    }

    fp = fopen(MEMINFO, "r");
    if (!fp) {
        fprintf(stderr, "Error opening /proc/meminfo");
        free(buffer);
        return send_code;
    }

    while (fgets(line, sizeof(line), fp)) {
        if (sscanf(line, "MemTotal: %lu kB", &mem_total) == 1) continue;
        if (sscanf(line, "MemFree: %lu kB", &mem_free) == 1) continue;
        if (sscanf(line, "Buffers: %lu kB", &buffers) == 1) continue;
        if (sscanf(line, "Cached: %lu kB", &cached) == 1) continue;
        if (sscanf(line, "SwapTotal: %lu kB", &swap_total) == 1) continue;
        if (sscanf(line, "SwapFree: %lu kB", &swap_free) == 1) continue;
    }
    fclose(fp);

    used_ram = mem_total - mem_free - buffers - cached;
    used_swap = swap_total - swap_free;

    if (mem_total > 0)
        ram_usage_percent = (float)used_ram / mem_total * 100.0f;
    if (swap_total > 0)
        swap_usage_percent = (float)used_swap / swap_total * 100.0f;

    size_t len = snprintf((char *)buffer, MAX_BUFFER_SIZE,
                 "--------- Memory Usage ---------\n"
                 "Memory Usage Information:\n"
                 "Total RAM:   %lu MB\n"
                 "Used RAM:    %lu MB (%.2f%%)\n"
                 "Free RAM:    %lu MB\n"
                 "Buffers:     %lu MB\n"
                 "Cached:      %lu MB\n"
                 "Total Swap:  %lu MB\n"
                 "Used Swap:   %lu MB (%.2f%%)\n"
                 "Free Swap:   %lu MB\n",
                  mem_total/BYTES_PER_UNIT, used_ram/BYTES_PER_UNIT, ram_usage_percent, mem_free/BYTES_PER_UNIT,
                  buffers / BYTES_PER_UNIT, cached / BYTES_PER_UNIT, swap_total / BYTES_PER_UNIT,
                  used_swap / BYTES_PER_UNIT, swap_usage_percent, swap_free / BYTES_PER_UNIT);

    send_code = safe_send(sock, buffer, len);
    free(buffer);

    return send_code;
}

int info_process(int sock) {
    DIR *dir;
    struct dirent *entry;
    FILE *fp;
    char path[MAX_LINE_LENGTH];
    char line[MAX_LINE_LENGTH];
    process_info processes[MAX_PROC_COUNT];
    int process_count = 0;
    unsigned char *buffer;
    int send_code = 0;

    buffer = (unsigned char *)malloc(MAX_BUFFER_SIZE);
    if (!buffer) {
        fprintf(stderr, "Cannot allocate memory for data buffer\n");
        return send_code;
    }

    dir = opendir(PROC);
    if (!dir) {
        fprintf(stderr, "Cannot open %s\n", PROC);
        free(buffer);
        return send_code;
    }

    strcpy((char *)buffer, "--------- Process Information ---------\n");
    int offset = strlen((char *)buffer);

    while ((entry = readdir(dir)) != NULL && process_count < MAX_PROC_COUNT) {
        int pid = atoi(entry->d_name);
        if (pid <= 0) continue;

        snprintf(path, sizeof(path), "%s/%d/status", PROC, pid);
        fp = fopen(path, "r");
        if (!fp) continue;

        char name[256] = {0};
        char state = '?';
        unsigned long memory = 0;

        while (fgets(line, sizeof(line), fp)) {
            if (strncmp(line, "Name:", 5) == 0) {
                sscanf(line + 5, "%255s", name);
            } else if (strncmp(line, "State:", 6) == 0) {
                sscanf(line + 6, " %c", &state);
            } else if (strncmp(line, "VmRSS:", 6) == 0) {
                sscanf(line + 6, "%lu", &memory); // VmRSS in kB
            }
        }

        fclose(fp);

        processes[process_count].pid = pid;
        strncpy(processes[process_count].name, name, sizeof(processes[process_count].name) - 1);
        processes[process_count].state = state;
        processes[process_count].memory = memory;
        processes[process_count].cpu_usage = 0.0;

        process_count++;
    }

    closedir(dir);

    for (int i = 0; i < process_count - 1; i++) {
        for (int j = 0; j < process_count - i - 1; j++) {
            if (processes[j].memory < processes[j + 1].memory) {
                process_info temp = processes[j];
                processes[j] = processes[j + 1];
                processes[j + 1] = temp;
            }
        }
    }

    int max_processes = process_count > MAX_PROC_TOP ? MAX_PROC_TOP : process_count;

    offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset,
                      "Total processes: %d\n"
                      "Top %d processes by memory usage:\n"
                      "%-15s %-15s %-15s %-30s\n", process_count, max_processes, "PID", "STATE", "MEMORY(MB)", "NAME");

    for (int i = 0; i < max_processes; i++) {
        offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset,
                          "%-15d %-15c %-15lu %-30s\n",
                          processes[i].pid, processes[i].state,
                          processes[i].memory / BYTES_PER_UNIT, processes[i].name);
    }

    send_code = safe_send(sock, buffer, offset);
    free(buffer);

    return send_code;
}

int info_disk(int sock) {
    struct statvfs fs_info;
    FILE *fp;
    char line[MAX_LINE_LENGTH];
    int size_buffer_str = 20;
    unsigned char *buffer;
    int send_code = 0;

    buffer = (unsigned char *)malloc(MAX_BUFFER_SIZE);
    if (!buffer) {
        fprintf(stderr, "Cannot allocate memory for data buffer\n");
        return send_code;
    }

    strcpy((char *)buffer, "--------- Disk Usage ---------\n");
    int offset = strlen((char *)buffer);

    if (statvfs("/", &fs_info) == 0) {
        float total_space = (float)(fs_info.f_blocks * fs_info.f_frsize) /
                            (BYTES_PER_UNIT * BYTES_PER_UNIT * BYTES_PER_UNIT);
        float free_space = (float)(fs_info.f_bfree * fs_info.f_frsize) /
                            (BYTES_PER_UNIT * BYTES_PER_UNIT * BYTES_PER_UNIT);
        float used_space = total_space - free_space;
        float usage_percent = used_space / total_space * 100.0;

        offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset,
                          "Root filesystem:\n"
                          "Total space: %.2f GB\n"
                          "Used space: %.2f GB (%.2f%%)\n"
                          "Free space: %.2f GB\n",
                          total_space, used_space, usage_percent, free_space);
    } else {
        offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset,
                          "Error: Cannot get filesystem information\n");
    }

    fp = fopen(DISKSTAT, "r");
    if (fp) {
        offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset,
                          "\nDisk I/O Statistics:\n"
                          "%-*s %-*s %-*s\n",
                          size_buffer_str, "Device", size_buffer_str, "Reads", size_buffer_str, "Writes");

        while (fgets(line, sizeof(line), fp) != NULL) {
            char dev_name[size_buffer_str];
            unsigned long rd, wr;

            if (sscanf(line, "%*d %*d %s %lu %*d %*d %*d %lu", dev_name, &rd, &wr) == 3) {

                if (strncmp(dev_name, "loop", 4) == 0) continue;

                float read_gb = rd * fs_info.f_frsize / (BYTES_PER_UNIT * BYTES_PER_UNIT);
                float write_gb = wr * fs_info.f_frsize / (BYTES_PER_UNIT * BYTES_PER_UNIT);
                char reads[size_buffer_str], writes[size_buffer_str];
                snprintf(reads, size_buffer_str, "%lu %.2f MB", rd, read_gb);
                snprintf(writes, size_buffer_str, "%lu %.2f MB", wr, write_gb);
                offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset, "%-*s %-*s %-*s\n",
                                   size_buffer_str, dev_name, size_buffer_str, reads, size_buffer_str, writes);

            }
        }
        fclose(fp);
    } else {
        offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset, "Cannot open %s\n", DISKSTAT);
    }

    send_code = safe_send(sock, buffer, offset);
    free(buffer);

    return send_code;
}

int info_network(int sock) {
    FILE *fp;
    char line[MAX_LINE_LENGTH];
    struct ifaddrs *ifaddr, *ifa;
    int size_buffer_str = 20;
    char host[NI_MAXHOST];
    unsigned char *buffer;
    int send_code = 0;

    buffer = (unsigned char *)malloc(MAX_BUFFER_SIZE);
    if (!buffer) {
        fprintf(stderr, "Cannot allocate memory for data buffer\n");
        return send_code;
    }

    strcpy((char *)buffer, "--------- Network Activity ---------\n");
    int offset = strlen((char *)buffer);

    if (getifaddrs(&ifaddr) == -1) {
        fprintf(stderr, "Cannot get network interfaces\n");
        free(buffer);
        return send_code;
    }

    offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset,
                        "%-*s %-*s\n", size_buffer_str, "Interfaces", size_buffer_str, "IP");

    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr == NULL)
            continue;

        if (ifa->ifa_addr->sa_family == AF_INET) {
            if (getnameinfo(ifa->ifa_addr, sizeof(struct sockaddr_in), host, NI_MAXHOST, NULL, 0, NI_NUMERICHOST)) {
                fprintf(stderr, "getnameinfo() failed\n");
                continue;
            }

            offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset,
                               "%-*s %-*s\n", size_buffer_str, ifa->ifa_name, size_buffer_str, host);
        }
    }
    freeifaddrs(ifaddr);

    fp = fopen(NETWORK, "r");
    if (fp) {
        for (int i = 0; i < 2; i++) {
            if (fgets(line, sizeof(line), fp) == NULL) {
                fclose(fp);
                free(buffer);
                return -1;
            }
        }

        offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset,
                          "\nNetwork Traffic\n"
                          "%-*s %-*s %-*s\n",
                          size_buffer_str, "Interface", size_buffer_str, "Receive", size_buffer_str, "Transmit");

        while (fgets(line, sizeof(line), fp) != NULL) {
            char iface[32];
            unsigned long rx_bytes, tx_bytes;

            if (sscanf(line, " %31[^:]: %lu %*s %*s %*s %*s %*s %*s %*s %lu", iface, &rx_bytes, &tx_bytes) == 3) {
                char rx[size_buffer_str], tx[size_buffer_str];
                char *trim_iface = iface;

                while (*trim_iface == ' ') trim_iface++;
                snprintf(rx, size_buffer_str, "%.2f MB", (float)rx_bytes / (BYTES_PER_UNIT * BYTES_PER_UNIT));
                snprintf(tx, size_buffer_str, "%.2f MB", (float)tx_bytes / (BYTES_PER_UNIT * BYTES_PER_UNIT));


                offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset,
                                  "%-*s %-*s %-*s\n",
                                  size_buffer_str, trim_iface, size_buffer_str, rx, size_buffer_str, tx);
            }
        }
        fclose(fp);
    } else {
        offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset, "Error: Cannot open %s\n", NETWORK);
    }

    send_code = safe_send(sock, buffer, offset);
    free(buffer);

    return send_code;
}

int info_uptime(int sock) {
    struct sysinfo info;
    time_t current_time;
    struct tm *time_info;
    char time_str[64];
    unsigned char *buffer;
    int send_code = 0;

    buffer = (unsigned char *)malloc(MAX_BUFFER_SIZE);
    if (!buffer) {
        fprintf(stderr, "Cannot allocate memory for data buffer\n");
        return send_code;
    }

    if (sysinfo(&info) != 0) {
        fprintf(stderr, "Cannot get system information\n");
        free(buffer);
        return send_code;
    }

    time(&current_time);
    time_info = localtime(&current_time);
    strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", time_info);

    unsigned long uptime_seconds = info.uptime;
    unsigned int days = uptime_seconds / (60 * 60 * 24);
    unsigned int hours = (uptime_seconds % (60 * 60 * 24)) / (60 * 60);
    unsigned int minutes = (uptime_seconds % (60 * 60)) / 60;
    unsigned int seconds = uptime_seconds % 60;

    time_t boot_time = current_time - uptime_seconds;
    struct tm *boot_time_info = localtime(&boot_time);
    char boot_time_str[64];
    strftime(boot_time_str, sizeof(boot_time_str), "%Y-%m-%d %H:%M:%S", boot_time_info);

    int len = snprintf((char *)buffer, MAX_BUFFER_SIZE,
                      "--------- System Uptime ---------\n"
                      "System Uptime Information\n"
                      "Current time: %s\n"
                      "System boot time: %s\n"
                      "Uptime: %u days, %u hours, %u minutes, %u seconds\n"
                      "Number of current processes: %d\n"
                      "System load averages (1, 5, 15 min): %.2f, %.2f, %.2f\n",
                      time_str, boot_time_str,
                      days, hours, minutes, seconds,
                      info.procs,
                      info.loads[0]/CONST_UPTIME, info.loads[1]/CONST_UPTIME, info.loads[2]/CONST_UPTIME);

    send_code = safe_send(sock, buffer, len);
    free(buffer);

    return send_code;
}

int info_sys(int sock) {
    struct utsname sys_info;
    FILE *fp;
    char line[MAX_LINE_LENGTH];
    unsigned char *buffer;
    int send_code = 0;

    buffer = (unsigned char *)malloc(MAX_BUFFER_SIZE);
    if (!buffer) {
        fprintf(stderr, "Cannot allocate memory for data buffer\n");
        return send_code;
    }

    strcpy((char *)buffer, "--------- System Information ---------\n");
    int offset = strlen((char *)buffer);

    if (uname(&sys_info) != 0) {
        fprintf(stderr, "Cannot get system information\n");
        free(buffer);
        return send_code;
    }

    offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset,
                      "System: %s\n"
                      "Node name: %s\n"
                      "Release: %s\n"
                      "Version: %s\n"
                      "Machine: %s\n",
                      sys_info.sysname, sys_info.nodename,
                      sys_info.release, sys_info.version, sys_info.machine);

    fp = fopen(CPU, "r");
    if (fp) {
        char model_name[MAX_LINE_LENGTH] = "Unknown";
        int cpu_cores = 0;

        while (fgets(line, sizeof(line), fp) != NULL) {
            if (strncmp(line, "model name", 10) == 0) {
                char *value = strchr(line, ':');
                if (value) {
                    strncpy(model_name, value + 2, sizeof(model_name) - 1);
                    char *nl = strchr(model_name, '\n');
                    if (nl) *nl = '\0';
                }
                cpu_cores++;
            }
        }

        offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset,
                          "\nCPU Information:\n"
                          "Processor: %s\n"
                          "CPU cores: %d\n",
                          model_name, cpu_cores);

        fclose(fp);
    }

    fp = fopen(OS_RELEASE, "r");
    if (fp) {
        char pretty_name[MAX_LINE_LENGTH] = "Unknown";

        while (fgets(line, sizeof(line), fp) != NULL) {
            if (strncmp(line, "PRETTY_NAME", 11) == 0) {
                char *value = strchr(line, '=');
                if (value) {
                    value++;
                    if (*value == '"') value++;

                    strncpy(pretty_name, value, sizeof(pretty_name) - 1);
                    char *nl = strchr(pretty_name, '\n');
                    if (nl) *nl = '\0';
                    nl = strchr(pretty_name, '"');
                    if (nl) *nl = '\0';
                }
            }
        }

        offset += snprintf((char *)buffer + offset, MAX_BUFFER_SIZE - offset,
                          "\nOS Information:\n"
                          "Distribution: %s\n",
                          pretty_name);

        fclose(fp);
    }

    send_code = safe_send(sock, buffer, offset);
    free(buffer);

    return send_code;
}