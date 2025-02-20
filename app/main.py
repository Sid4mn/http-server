#!/usr/bin/env python3
import socket
import threading
import sys
import os

FILES_DIR = "."

def handle_client(conn, addr):
    with conn:
        print(f"Connection accepted from {addr}")
        request = conn.recv(4096)
        try:
            request_str = request.decode()
        except UnicodeDecodeError:
            conn.send("HTTP/1.1 400 Bad Request\r\n\r\n".encode())
            return

        print(f"Request = {request_str}")

        parts = request_str.split("\r\n\r\n", 1)
        header_part = parts[0]
        body_part = parts[1] if len(parts) > 1 else ""
        lines = header_part.split("\r\n")
        
        if not lines:
            conn.send("HTTP/1.1 400 Bad Request\r\n\r\n".encode())
            return

        client_accepts_gzip = False
        for line in lines[1:]:
            if line.lower().startswith("accept-encoding:"):
                encoding_list = line.split(":", 1)[1].strip().split(",")
                encoding_list = [enc.strip() for enc in encoding_list]
                if "gzip" in encoding_list:
                    client_accepts_gzip = True
                    break

        req_line = lines[0]
        req_parts = req_line.split(" ")
        print(f"Parts = {req_parts}")

        if len(req_parts) < 2:
            conn.send("HTTP/1.1 400 Bad Request\r\n\r\n".encode())
            return
        
        method, path = req_parts[0], req_parts[1]
        print(f"Method = {method}, Path = {path}")

        if path.startswith("/echo/"):
            echo_str = path[len("/echo/"):]
            body_bytes = echo_str.encode()
            content_length = len(body_bytes)
            headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
            )
            if client_accepts_gzip:
                headers += "Content-Encoding: gzip\r\n"
            headers += f"Content-Length: {content_length}\r\n\r\n"
            response = headers + echo_str
            conn.send(response.encode())

        elif path == "/user-agent":
            user_agent_val = ""
            for line in lines[1:]:
                if line.lower().startswith("user-agent:"):
                    user_agent_val = line[len("User-Agent:"):].strip()
                    break
            body_bytes = user_agent_val.encode()
            content_length = len(body_bytes)
            headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
            )
            if client_accepts_gzip:
                headers += "Content-Encoding: gzip\r\n"
            headers += f"Content-Length: {content_length}\r\n\r\n"
            response = headers + user_agent_val
            conn.send(response.encode())

        elif path.startswith("/files/"):
            filename = path[len("/files/"):]
            full_path = os.path.join(FILES_DIR, filename)
            if method == "GET":
                if os.path.isfile(full_path):
                    try:
                        with open(full_path, "rb") as f:
                            file_data = f.read()
                        content_length = len(file_data)
                        header = (
                            "HTTP/1.1 200 OK\r\n"
                            "Content-Type: application/octet-stream\r\n"
                        )
                        if client_accepts_gzip:
                            header += "Content-Encoding: gzip\r\n"
                        header += f"Content-Length: {content_length}\r\n\r\n"
                        conn.send(header.encode() + file_data)
                        return
                    except Exception:
                        response = "HTTP/1.1 404 Not Found\r\n\r\n"
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\n"
                conn.send(response.encode())

            elif method == "POST":
                content_length_value = None
                for line in lines[1:]:
                    if line.lower().startswith("content-length:"):
                        try:
                            content_length_value = int(line.split(":", 1)[1].strip())
                        except Exception:
                            content_length_value = 0
                        break

                if content_length_value is None:
                    response = "HTTP/1.1 400 Bad Request\r\n\r\n"
                    conn.send(response.encode())
                    return
                
                body_data = body_part[:content_length_value]
                try:
                    with open(full_path, "wb") as f:
                        f.write(body_data.encode())
                    response = "HTTP/1.1 201 Created\r\n\r\n"
                except Exception:
                    response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
                conn.send(response.encode())

            else:
                response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"
                conn.send(response.encode())

        elif path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
            conn.send(response.encode())

        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
            conn.send(response.encode())

def main():
    global FILES_DIR
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
