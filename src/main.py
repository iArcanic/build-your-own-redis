# src/main.py

import socket
import threading


def handle_client(client_socket):
    try:
        while True:
            # Receive data from the client
            data = client_socket.recv(1024)
            if not data:
                break  # No more data, client closed the connection

            # Decode the received data to process commands
            data_str = data.decode('utf-8').strip()

            # Process PING command
            if data_str.startswith("*1") and "PING" in data_str.upper():
                response = "+PONG\r\n"
                client_socket.sendall(response.encode('utf-8'))

            # Process ECHO command
            elif data_str.startswith("*2") and "ECHO" in data_str.upper():
                # Extract the message to echo
                message = data_str.split("\r\n")[-1]
                response = f"${len(message)}\r\n{message}\r\n"
                client_socket.sendall(response.encode('utf-8'))

            else:
                break  # For simplicity, break on unrecognized commands or unexpected format

    except OSError as e:
        print(f"Socket error: {e}")
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
