# src/main.py

import socket

from config import *


def main():
    # Create a TCP/IP socket
    server_socket = socket.create_server((REDIS_SERVER_HOST, REDIS_SERVER_PORT), reuse_port=True)
    print(f"Redis server is listening on port {REDIS_SERVER_PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        try:
            # Regardless of input, respond with "+PONG\r\n"
            response = "+PONG\r\n"
            client_socket.sendall(response.encode('utf-8'))
        finally:
            # Clean up the connection
            client_socket.close()


if __name__ == "__main__":
    main()
