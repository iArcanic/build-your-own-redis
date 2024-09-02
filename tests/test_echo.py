# tests/test_echo.py

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


def test_echo(start_server):
    """Test that the server responds to ECHO with the provided argument."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 6379))
        
        # Send ECHO command with argument 'hey'
        command = "*2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n"
        s.sendall(command.encode('utf-8'))
        
        # Read the response
        response = b""
        while b'\r\n' not in response:
            response += s.recv(1024)
        
        print(f"Response received: {response.decode('utf-8')}")  # Debug output
        
        # The response should be $3\r\nhey\r\n
        expected_response = "$3\r\nhey\r\n"
        assert response.decode('utf-8') == expected_response
