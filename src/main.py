# src/main.py

import socket


def handle_client(client_socket):
    try:
        while True:
            # Read the incoming data
            data = client_socket.recv(1024)
            if not data:
                break  # No more data, client closed the connection

            # Check for PING commands in the data and respond accordingly
            while data:
                if b"PING" in data:
                    response = "+PONG\r\n"
                    client_socket.sendall(response.encode('utf-8'))

                    # Remove the handled command from the data
                    data = data[data.find(b"PING") + 4:]
                else:
                    break
    finally:
        # Clean up the connection
        client_socket.close()


def main():
    # Create a TCP/IP socket
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    print("Redis server is listening on port 6379...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        handle_client(client_socket)


if __name__ == "__main__":
    main()
