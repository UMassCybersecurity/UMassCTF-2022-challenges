TARGET = sixmacs.so

CC = gcc

CFLAGS = -fPIC -Wall

SRC = sixmacs.c
OBJ = $(SRC:.c=.o)

all:$(TARGET)

$(TARGET):$(OBJ)
		$(CC) -shared -o $@ $(OBJ) -lsixel

.SUFFIXES: .c .o

.c.o:
		$(CC) -c $(CFLAGS) $<
clean:
		rm -f $(TARGET)
		rm -f *.o *.obj
