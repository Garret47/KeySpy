#pragma once

#define BUFFER_CAPACITY 1024

#include "keylogger/utils/log_file.h"

typedef struct {
    char *data;
    size_t size;
    size_t capacity;
} BufferText;

int buffer_text_init(BufferText *buffer);
void buffer_text_clear(BufferText *buffer);
int write_or_buffer_event(Logfile *fh, BufferText *buffer, const char *event_str, pthread_mutex_t *mutex);
