# src/main.py

import socket
import threading
import time
import sys
import argparse

# Global configuration
config = {
    "dir": "/tmp",  # Default directory
    "dbfilename": "dump.rdb"  # Default RDB file name
}

# Data store to keep track of keys, values, and expiry times
data_store = {}
expiry_store = {}


def handle_client(client_socket):
    try:
        while True:
            # Receive data from the client
            data = client_socket.recv(1024)
            if not data:
                break  # No more data, client closed the connection

            # Decode the received data to process commands
            data_str = data.decode('utf-8').strip()
            print(f"Received data: {data_str}")

            # Process the command based on the RESP protocol
            parts = data_str.split("\r\n")

            # PING command
            if parts[2].upper() == "PING":
                response = "+PONG\r\n"
                client_socket.sendall(response.encode('utf-8'))

            # ECHO command
            elif parts[2].upper() == "ECHO":
                message = parts[4]
                response = f"${len(message)}\r\n{message}\r\n"
                client_socket.sendall(response.encode('utf-8'))

            # SET command
            elif parts[2].upper() == "SET":
                key = parts[4]
                value = parts[6]
                expiry = None

                # Check for PX option
                if len(parts) > 8 and parts[8].lower() == "px":
                    expiry = int(parts[10])
                
                # Store the key-value pair with optional expiry
                data_store[key] = value
                if expiry is not None:
                    expiry_store[key] = time.time() + (expiry / 1000.0)  # Convert milliseconds to seconds
                else:
                    expiry_store[key] = None  # No expiry

                response = "+OK\r\n"
                client_socket.sendall(response.encode('utf-8'))

            # GET command
            elif parts[2].upper() == "GET":
                key = parts[4]
                current_time = time.time()
                
                # Check if the key exists and hasn't expired
                if key in expiry_store and (expiry_store[key] is None or current_time <= expiry_store[key]):
                    value = data_store.get(key)
                    response = f"${len(value)}\r\n{value}\r\n"
                else:
                    # If the key is expired or doesn't exist
                    data_store.pop(key, None)  # Clean up expired key
                    expiry_store.pop(key, None)
                    response = "$-1\r\n"
                
                client_socket.sendall(response.encode('utf-8'))

            # CONFIG GET command
            elif parts[2].upper() == "CONFIG" and parts[4].upper() == "GET":
                param = parts[6].lower()
                if param in config:
                    value = config[param]
                    response = f"*2\r\n${len(param)}\r\n{param}\r\n${len(value)}\r\n{value}\r\n"
                else:
                    response = "*2\r\n$-1\r\n$-1\r\n"  # If the config parameter does not exist

                client_socket.sendall(response.encode('utf-8'))

            else:
                print("Unexpected data format received.")
                break  # For simplicity, break on unrecognized commands or unexpected format

    except OSError as e:
        print(f"Socket error: {e}")
    finally:
        # Close the connection
        client_socket.close()


def run_server(dir, dbfilename):
    config["dir"] = dir
    config["dbfilename"] = dbfilename
    print(f"Configuration: dir={config['dir']}, dbfilename={config['dbfilename']}")

    # Create the server socket
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    print("Redis server is listening on port 6379...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        # Create a new thread to handle the client connection
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.daemon = True
        client_thread.start()


def main():
    import sys
    if 'pytest' in sys.modules:  # Running under pytest
        sys.argv = ['main']  # Reset arguments to prevent argparse issues

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Redis-like server clone")
    parser.add_argument("--dir", default="/tmp", help="Directory for storing RDB files")
    parser.add_argument("--dbfilename", default="dump.rdb", help="RDB file name")
    args = parser.parse_args()

    # Start the server with the provided arguments
    run_server(args.dir, args.dbfilename)


if __name__ == "__main__":
    main()
