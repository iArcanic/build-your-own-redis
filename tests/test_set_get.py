# tests/test_set_get.py

import socket
import threading
import time
import pytest

from src.main import main


@pytest.fixture(scope="module")
def start_server():
    server_thread = threading.Thread(target=main, daemon=True)
    server_thread.start()
    time.sleep(1)  # Give the server a second to start up
    print("Redis server started.")


def test_set_get(start_server):
    """Test that the server handles SET and GET commands correctly."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 6379))
        
        # Test SET command
        set_command = "*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n"
        s.sendall(set_command.encode('utf-8'))
        set_response = s.recv(1024)
        assert set_response.decode('utf-8') == "+OK\r\n"
        
        # Test GET command
        get_command = "*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n"
        s.sendall(get_command.encode('utf-8'))
        get_response = s.recv(1024)
        assert get_response.decode('utf-8') == "$3\r\nbar\r\n"
        
        # Test GET for non-existent key
        get_command = "*2\r\n$3\r\nGET\r\n$6\r\nnonkey\r\n"
        s.sendall(get_command.encode('utf-8'))
        get_response = s.recv(1024)
        assert get_response.decode('utf-8') == "$-1\r\n"
