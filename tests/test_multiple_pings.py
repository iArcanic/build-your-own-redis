# tests/test_multiple_pings.py

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


def test_multiple_pings(start_server):
    """Test that the server responds to multiple PING commands with multiple +PONG."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 6379))
        
        # Send two PING commands
        command = "*1\r\n$4\r\nPING\r\n*1\r\n$4\r\nPING\r\n"
        s.sendall(command.encode('utf-8'))
        
        # Read responses. We should get two +PONG responses.
        response = b""
        while len(response) < len("+PONG\r\n+PONG\r\n"):
            response += s.recv(1024)
        
        assert response.decode('utf-8') == "+PONG\r\n+PONG\r\n"
