#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "network/utils/register.h"


void init_registry(CommandRegistry* registry) {
    if (registry == NULL) return;

    registry->size = 0;
    for (size_t i = 0; i < MAX_COMMANDS; ++i) {
        registry->entries[i].name = NULL;
        registry->entries[i].func = NULL;
    }
}

void cleanup_registry(CommandRegistry* registry) {
    if (registry == NULL) return;

    for (size_t i = 0; i < registry->size; ++i) {
        if (registry->entries[i].name != NULL) {
            free(registry->entries[i].name);
            registry->entries[i].name = NULL;
        }
        registry->entries[i].func = NULL;
    }
    registry->size = 0;
}

int register_command(CommandRegistry* registry, const char* name, CommandFunc func) {
    if (registry == NULL || name == NULL || func == NULL) {
        fprintf(stderr, "Error: NULL pointer provided to register_command\n");
        return 0;
    }

    if (registry->size >= MAX_COMMANDS) {
        fprintf(stderr, "Error: Registry capacity exceeded (max %d commands).\n", MAX_COMMANDS);
        return 0;
    }

    for (size_t i = 0; i < registry->size; ++i) {
        if (registry->entries[i].name != NULL && strcmp(registry->entries[i].name, name) == 0) {
            fprintf(stderr, "Warning: Command '%s' is already registered.\n", name);
            return 0;
        }
    }

    size_t name_len = strlen(name) + 1;
    registry->entries[registry->size].name = (char*)malloc(name_len);
    if (registry->entries[registry->size].name == NULL) {
        fprintf(stderr, "Error: Failed to allocate memory for command name.\n");
        return 0;
    }

    strcpy(registry->entries[registry->size].name, name);
    registry->entries[registry->size].func = func;
    registry->size += 1;

    return 1;
}

CommandFunc get_command(const CommandRegistry* registry, const char* name) {
    if (registry == NULL || name == NULL) return NULL;

    for (size_t i = 0; i < registry->size; ++i) {
        if (registry->entries[i].name != NULL && strcmp(registry->entries[i].name, name) == 0) {
            return registry->entries[i].func;
        }
    }
    return NULL;
}

