#ifndef FileHandler_H_SENTRY
#define FileHandler_H_SENTRY

#define FILENAME "/tmp/log.txt"
#define MODE "w"

typedef struct {
    FILE *file;
    char *filename;
    char *mode;
} FileHandler;

int FileHandler_init(FileHandler *fh);
int FileHandler_write(FileHandler *fh, const char *text);
int FileHandler_close(FileHandler *fh);

#endif