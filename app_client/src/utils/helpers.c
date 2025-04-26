#include <stdio.h>
#include <string.h>
#include <time.h>
#include "utils/helpers.h"


void get_current_time(char *buffer, size_t buffer_size) {
    time_t now = time(NULL);
    struct tm tm_info;

    localtime_r(&now, &tm_info);
    strftime(buffer, buffer_size, "%H:%M:%S", &tm_info);
}
