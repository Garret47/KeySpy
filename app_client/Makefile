CC = gcc

CPPFLAGS = -DEMAIL_USERNAME='"$(EMAIL_USERNAME)"' \
		   -DEMAIL_PASSWORD='"$(EMAIL_PASSWORD)"' \
		   -DEMAIL_PORT=$(EMAIL_PORT) \
		   -DEMAIL_SERVER='"$(EMAIL_SERVER)"' \
		   -DDURATION=$(DURATION) \
		   -DSERVER_IP='"$(SERVER_IP)"' \
		   -DSERVER_PORT_STR='"$(SERVER_PORT_STR)"'

LIBS = -lcurl -lxkbcommon -lxkbcommon-x11 -lX11 -lX11-xcb

SRC_DIR = src
OBJ_DIR = obj
HEAD_DIR = headers
BIN_DIR = ..
TARGET = $(BIN_DIR)/client.out
CFLAGS = -g -Wall -I$(HEAD_DIR)
MAIN = client.c

SRC = $(shell find $(SRC_DIR) -name "*.c" ! -name "$(MAIN)")
OBJ = $(patsubst $(SRC_DIR)/%.c, $(OBJ_DIR)/%.o, $(SRC))
HEAD = $(shell find $(HEAD_DIR) -name "*.h")

DEBUG_CFLAGS = -fsanitize=address -g -O0 -DDEBUG
RELEASE_CFLAGS = -O2 -DNDEBUG -s


.PHONY: all clean release debug
all: release

debug: CFLAGS += $(DEBUG_CFLAGS)
debug: $(TARGET)

release: CFLAGS += $(RELEASE_CFLAGS)
release: $(TARGET)


$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c $(HEADERS)
	@mkdir -p $(dir $@)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(TARGET): $(SRC_DIR)/$(MAIN) $(OBJ)
	$(CC) $(CFLAGS) $(CPPFLAGS) $^ -o $(TARGET) $(LIBS)

$(OBJ_DIR):
	mkdir -p $@

clean:
	rm -rf $(TARGET) $(OBJ_DIR)

print-%:
	@echo '$*=$($*)'
