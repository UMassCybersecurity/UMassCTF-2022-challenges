#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>

// gcc chal.c -o chal -no-pie -fno-stack-protector

#define PORT  9055
#define MAGIC 0x1337

struct P1Header {
    unsigned int magic;
    unsigned int action;
    unsigned int length;
    char         key[32];
};

struct P2Header {
    unsigned int magic;
    unsigned int temperature;
    unsigned int type;
    unsigned int size;
    char         data[4096];
    unsigned int checksum; 
};

char *base46_map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
char *Pass = "password";
int Action = -1;
struct P2Header *p2;
char plain[64];

char* base64_decode(char* cipher) {
    char counts = 0;
    char buffer[4];
    int i = 0, p = 0;

    for(i = 0; cipher[i] != '\0'; i++) {
        char k;
        for(k = 0 ; k < 64 && base46_map[(int)k] != cipher[i]; k++);
        buffer[(int)counts++] = k;
        if(counts == 4) {
            plain[p++] = (buffer[0] << 2) + (buffer[1] >> 4);
            if(buffer[2] != 64)
                plain[p++] = (buffer[1] << 4) + (buffer[2] >> 2);
            if(buffer[3] != 64)
                plain[p++] = (buffer[2] << 6) + buffer[3];
            counts = 0;
        }
    }
    plain[p] = '\0';
    return plain;
}

// Verify that the user is sending proper packets
int verify_initial_packet(char *buffer) {
    struct P1Header *p1_header;

    p1_header = (struct P1Header*) buffer;

    if (p1_header->magic != MAGIC) { return -1; }

    Action = p1_header->action;
    char *key = base64_decode(p1_header->key);

    return strcmp(key, Pass);
}

// Verify that the second packets checksum is correct
int verify_checksum(char *buffer) {
    p2 = (struct P2Header*) buffer;
    long long sum = 0;

    for (int i = 0; i < p2->size; i++) {
        sum += p2->data[i];
    }

    //return sum - p2->checksum;
    return 0;
}

// Start making the coffee
int make_coffee(int sock) {
    char size[16];
    char coffee[1024];

    if (p2->temperature > 150) {
        return 1;
    }

    switch (p2->size) {
        case 0:
            strcpy(size, "Small");
            break;
        case 1:
            strcpy(size, "Medium");
            break;
        case 2:
            strcpy(size, "Large");
            break;
        default:
            strcpy(size, "None");
            break;
    }

    sprintf(coffee, "Good Morning!\n Your %s", size);
    strcat(coffee, p2->data);

    switch (p2->type) {
        case 0:
            strcat(coffee, " Espresso will be ready in 2 minutes.\n");
            send(sock, coffee, strlen(coffee), 0);
            break;
        case 1:
            strcat(coffee, " Decaf will be ready in 10 seconds.\n");
            send(sock, coffee, strlen(coffee), 0);
            break;
        case 2:
            strcat(coffee, " Honey Spiced Latte will be ready in 20 minutes.\n");
            send(sock, coffee, strlen(coffee), 0);
            break;
        default:
            send(sock, "An error has occured, please try again\n", 39, 0);
            return 1;
    }
    return 0;
}

// Handle incoming packets
int handler(int sockfd) {
    char packet_1[128];
    char tmp_p2[sizeof(struct P2Header)];

    // Verify first payload meant for verification purposes
    send(sockfd, "VERIFY\n", 7, 0);
    recv(sockfd, packet_1, sizeof(packet_1), 0);

    // Verify the initial payload and print SUCCESS | FAILURE
    if (verify_initial_packet(packet_1) != 0) {
        send(sockfd, "FAILURE\n", 8, 0);
        return 1;
    }
    send(sockfd, "SUCCESS\n", 8, 0);

    // Receive data packet
    recv(sockfd, tmp_p2, sizeof(struct P2Header), 0);

    // Verify the second packets checksum
    if (verify_checksum(tmp_p2) != 0) {
        send(sockfd, "CHECK FAILURE\n", 14, 0);
        return 1;
    }
    send(sockfd, "CHECK SUCCESS\n", 14, 0);

    switch (Action) {
        case 1: // Reboot
            send(sockfd, "Rebooting your CoffeeMaker9000\n", 31, 0);
            return 1;
        case 2: // Make Coffee
            send(sockfd, "Making Coffee\n", 14, 0);
            make_coffee(sockfd);
            break;
        case 3: // Turn off
            send(sockfd, "Shutting Down...\n", 17, 0);
            return 1;
        default:
            send(sockfd, "An error has occured, please try again\n", 39, 0);
            return 1;
    }
    return 0;
}

int main(int argc, char *argv[]) {
    int sockfd, s;
    static int opt = 1;
    struct sockaddr_in sa;
    int sa_len = sizeof(sa);

    // Create socket
    if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) { return 1; }

    // Prepare socket
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt)) < 0 ) {
        return -1;
    }

    // Assign IP and PORT
    sa.sin_family = AF_INET;
    sa.sin_addr.s_addr = INADDR_ANY;
    sa.sin_port = htons(PORT);

    // Bind to the specified port
    if (bind(sockfd, (struct sockaddr *)&sa, sizeof(sa)) < 0) { return 1; }

    // Start listening for incoming connections
    if (listen(sockfd, 50) < 0) { return 1; }

    // Accept a connection
    if ((s = accept(sockfd, (struct sockaddr *)&sa, (socklen_t*)&sa_len)) < 0) { return 1; }

    // Launch the connection handler
    handler(s);

    // Close socket
    close(sockfd);

    return 0;
}
