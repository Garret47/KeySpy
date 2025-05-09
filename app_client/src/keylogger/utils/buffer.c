#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include "keylogger/utils/buffer.h"


int buffer_text_init(BufferText *buffer) {
    buffer->data = malloc(BUFFER_CAPACITY);
    if (!buffer->data){
        return 1;
    }
    buffer->size = 0;
    buffer->capacity = BUFFER_CAPACITY;
    buffer->data[buffer->size] = '\0';
    return 0;
}

static int buffer_text_add(BufferText *buffer, const char *str, pthread_mutex_t *mutex, Logfile *fh){
    int len = strlen(str);
    if (len >= BUFFER_CAPACITY){
        fprintf(stderr,
        "[Buffer Overflow] Attempted to write a string of length %d: \"%s\" — "
        "exceeds buffer capacity (%d bytes)\n",
        len, str, BUFFER_CAPACITY);
        return 1;
    }
    if (buffer->size + len >= BUFFER_CAPACITY){
        pthread_mutex_lock(mutex);
        Logfile_write(fh, buffer->data);
        pthread_mutex_unlock(mutex);
        buffer->size = 0;
        buffer->data[0] = '\0';
    }

    memcpy(buffer->data + buffer->size, str, len);
    buffer->size += len;
    buffer->data[buffer->size] = '\0';
    return 0;
}

void buffer_text_clear(BufferText *buffer){
    if (buffer->data){
        free(buffer->data);
        buffer->data = NULL;
        buffer->size = 0;
        buffer->capacity = 0;
    }
}

int write_or_buffer_event(Logfile *fh, BufferText *buffer, const char *event_str, pthread_mutex_t *mutex){
    if (pthread_mutex_trylock(mutex) == 0) {
        if (buffer->size){
            Logfile_write(fh, buffer->data);
            buffer->size = 0;
        }
        Logfile_write(fh, event_str);
        pthread_mutex_unlock(mutex);
        return 0;
    }
    if (buffer_text_add(buffer, event_str, mutex, fh)){
        return 1;
    }
    return 0;
}
