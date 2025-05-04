#pragma once

typedef struct {
    int width;
    int height;
    int bits_per_pixel;
    unsigned char *image_data;
} ImageData;

int create_screenshot();
