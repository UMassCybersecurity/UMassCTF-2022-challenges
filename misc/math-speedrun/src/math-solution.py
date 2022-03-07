import socket

def netcat(hostname, port, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, port))
    # s.sendall(content)
    # s.shutdown(socket.SHUT_WR)
    while 1:
        data = s.recv(1024)
        if len(data) == 0:
            break
        print("\nReceived:", repr(data))
        senddata = 5
        s.sendall(senddata.to_bytes(50, 'big'))
    print("Connection closed.")
    s.close()

if __name__ == "__main__":
    netcat("127.0.0.1", 8085, "")
