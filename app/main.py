#!/usr/bin/env python3
import socket
import threading
import sys
import os

FILES_DIR = "."

def handle_client(conn, addr):
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

                if path.startswith("/echo/"):
                    echo_str = path[len("/echo/"):]
                    content_length = len(echo_str.encode())
                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        f"Content-Length: {content_length}\r\n"
                        "\r\n"
                        f"{echo_str}"
                    )

                elif path == "/user-agent":
                    user_agent_val = ""
                    for line in lines[1:]:
                        if line.lower().startswith("user-agent:"):
                            user_agent_val = line[len("User-Agent:"):].strip()
                            break
                    content_length = len(user_agent_val.encode())
                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        f"Content-Length: {content_length}\r\n"
                        "\r\n"
                        f"{user_agent_val}"
                    )

                elif path.startswith("/files/"):
                    filename = path[len("/files/"):]
                    full_path = os.path.join(FILES_DIR, filename)
                    if os.path.isfile(full_path):
                        try:
                            with open(full_path, "rb") as f:
                                file_data = f.read()
                            content_length = len(file_data)
                            header = (
                                "HTTP/1.1 200 OK\r\n"
                                "Content-Type: application/octet-stream\r\n"
                                f"Content-Length: {content_length}\r\n"
                                "\r\n"
                            )
                            # Send header and file data as bytes.
                            conn.send(header.encode() + file_data)
                            return  # Exit the function after sending file data.
                        except Exception as e:
                            response = "HTTP/1.1 404 Not Found\r\n\r\n"
                    else:
                        response = "HTTP/1.1 404 Not Found\r\n\r\n"

                elif path == "/":
                    response = "HTTP/1.1 200 OK\r\n\r\n"
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"
            else:
                response = "HTTP/1.1 400 Bad Request\r\n\r\n"
        else:
            response = "HTTP/1.1 400 Bad Request\r\n\r\n"

        conn.send(response.encode())

def main():
    global FILES_DIR
    # Parse the --directory flag from the command line.
    if "--directory" in sys.argv:
        index = sys.argv.index("--directory")
        if index + 1 < len(sys.argv):
            FILES_DIR = sys.argv[index + 1]
    print(f"Using directory: {FILES_DIR}")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    main()
