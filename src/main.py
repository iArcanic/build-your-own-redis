# src/main.py

import socket
import threading


def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # No more data, client closed the connection

            # Handle multiple PING commands in a single connection
            while b"PING" in data:
                response = "+PONG\r\n"
                client_socket.sendall(response.encode('utf-8'))

                # Remove the handled command from the data
                data = data[data.find(b"PING") + 4:]
    except OSError:
        # Handle any socket-related errors gracefully
        pass
    finally:
        client_socket.close()


def main():
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    print("Redis server is listening on port 6379...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        # Create a new thread to handle the client connection
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.daemon = True
        client_thread.start()


if __name__ == "__main__":
    main()
