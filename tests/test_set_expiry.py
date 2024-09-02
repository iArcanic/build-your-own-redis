# tests/test_set_expiry.py

import socket
import threading
import time
import pytest

from src.main import main


@pytest.fixture(scope="module")
def start_server():
    # Start the server in a separate thread
    server_thread = threading.Thread(target=main, daemon=True)
    server_thread.start()
    time.sleep(1)  # Give the server a second to start up
    print("Redis server started.")


def test_set_expiry(start_server):
    """Test SET with expiry and GET before and after expiry."""
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 6379))
        
        # SET command with expiry
        set_command = "*4\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n$2\r\npx\r\n$3\r\n100\r\n"
        s.sendall(set_command.encode('utf-8'))
        response = s.recv(1024)
        assert response.decode('utf-8') == "+OK\r\n"
        
        # GET command before expiry
        s.sendall("*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n".encode('utf-8'))
        response = s.recv(1024)
        assert response.decode('utf-8') == "$3\r\nbar\r\n"
        
        # Wait for the key to expire
        time.sleep(0.2)
        
        # GET command after expiry
        s.sendall("*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n".encode('utf-8'))
        response = s.recv(1024)
        assert response.decode('utf-8') == "$-1\r\n"
        