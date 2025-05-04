#pragma once

#define MAX_COMMANDS 10

typedef int (*CommandFunc)(int sock);

typedef struct {
    char* name;
    CommandFunc func;
} CommandEntry;

typedef struct {
    CommandEntry entries[MAX_COMMANDS];
    size_t size;
} CommandRegistry;

void init_registry(CommandRegistry* registry);
void cleanup_registry(CommandRegistry* registry);
int register_command(CommandRegistry* registry, const char* name, CommandFunc func);
CommandFunc get_command(const CommandRegistry* registry, const char* name);