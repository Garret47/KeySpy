#pragma once

#define FILENAME "/tmp/log.txt"
#define MODE "w"

typedef struct {
    FILE *file;
    char *filename;
    char *mode;
} Logfile;

int Logfile_init(Logfile *fh);
int Logfile_write(Logfile *fh, const char *text);
int Logfile_close(Logfile *fh);
