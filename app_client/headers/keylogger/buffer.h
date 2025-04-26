#ifndef Keylogger_Buffer_H_SENTRY
#define Keylogger_Buffer_H_SENTRY

#define BUFFER_CAPACITY 1024

#include "keylogger/file_handler.h"

typedef struct {
    char *data;
    size_t size;
    size_t capacity;
} BufferText;

int buffer_text_init(BufferText *buffer);
int buffer_text_add(BufferText *buffer, const char *str, pthread_mutex_t *mutex, FileHandler *fh);
void buffer_text_clear(BufferText *buffer);
int write_or_buffer_event(FileHandler *file, BufferText *buffer, const char *event_str, pthread_mutex_t *mutex);

#endif