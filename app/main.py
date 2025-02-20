import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()

    # server_socket.accept() # wait for client
    # msg = "HTTP/1.1 200 OK\r\n\r\n"
    # server = server_socket.accept()
    # server[0].send(msg.encode())

    while True:
        conn, addr = server_socket.accept()
        with conn:
            print(f"Connection accepted from {addr}")
            request = conn.recv(4096).decode()
            print(f"Request = {request}")

            lines = request.split("\r\n")
            if lines:
                req_line = lines[0]
                parts = req_line.split(" ")
                print(f"Parts = {parts}")
                
                if len(parts) >= 2:
                    method, path = parts[0], parts[1]
                    print(f"Method = {method}, Path = {path}")
                    # if path.startswith("/echo"):
                    #     echo_str = path[len("/echo/"):]
                    #     content_length = len(echo_str.encode())
                    #     response = (
                    #         "HTTP/1.1 200 OK\r\n"
                    #         "Content-Type: text/plain\r\n"
                    #         f"Content-Length: {content_length}\r\n"
                    #         "\r\n"
                    #         f"{echo_str}"
                    #     )

                    if path == "/user-agent":
                        user_agent_val = ""
                        for line in lines[1:]:
                            if line.lower().startswith("user-agent:"):
                                user_agent_val = line[len("/user-agent"):].strip()
                                break
                        
                        cont_length = len(user_agent_val.encode())
                        response = (
                            "HTTP/1.1 200 OK\r\n"
                            "Content-Type: text/plain\r\n"
                            f"Content-Length: {cont_length}\r\n"
                            "\r\n"
                            f"{user_agent_val}"
                        )
                    elif path == "/":
                        response = "HTTP/1.1 200 OK\r\n\r\n"
                    else:
                        response = "HTTP/1.1 404 Not Found\r\n\r\n"
                else:
                    response = "HTTP/1.1 400 Bad Request\r\n\r\n"
            else:
                response = "HTTP/1.1 400 Bad Request\r\n\r\n"

            conn.send(response.encode())

if __name__ == "__main__":
    main()
