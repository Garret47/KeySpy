#include <stdlib.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "file_handler.h"

int FileHandler_init(FileHandler *fh)
{
    fh->filename = NULL;
    fh->mode = NULL;
    fh->file = NULL;

    fh->filename = strdup(FILENAME);
    if (!(fh->filename)) {
        fprintf(stderr, "Error allocating memory for filename\n");
        return 1;
    }


    fh->mode = strdup(MODE);
    if (!(fh->mode)) {
        fprintf(stderr, "Error allocating memory for mode\n");
        return 1;
    }

    fh->file = fopen(fh->filename, fh->mode);
    if (!(fh->file)) {
        fprintf(stderr, "Error opening file %s\n", fh->filename);
        return 1;
    }

    return 0;
}

int FileHandler_write(FileHandler *fh, const char *text)
{
    if (fprintf(fh->file, "%s", text) < 0) {
        fprintf(stderr, "Error writing file\n");
        return 1;
    }
    return 0;
}

int FileHandler_close(FileHandler *fh) {
    int flag_error = 0;

    if (fh->filename){
        free(fh->filename);
        fh->filename = NULL;
    }
    if (fh->mode){
        free(fh->mode);
        fh->mode = NULL;
    }

    if (fh->file){
        if (fflush(fh->file) != 0) {
            fprintf(stderr, "Error flushing buffer\n");
            flag_error = 1;
        }

        if (fclose(fh->file) != 0) {
            fprintf(stderr, "Error closing file\n");
            flag_error = 1;
        }

        fh->file = NULL;
    }
    return flag_error;
}
