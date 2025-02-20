import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    # server_socket.accept() # wait for client
    msg = "HTTP/1.1 200 OK\r\n\r\n"
    server_socket.listen()
    server = server_socket.accept()
    server[0].send(msg.encode())


if __name__ == "__main__":
    main()
