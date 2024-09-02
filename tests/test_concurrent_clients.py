# src/test_concurrent_clients.py

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


def client_task():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 6379))
        command = "*1\r\n$4\r\nPING\r\n"
        s.sendall(command.encode('utf-8'))
        response = s.recv(1024)
        assert response.decode('utf-8') == "+PONG\r\n"


def test_concurrent_clients(start_server):
    """Test that the server handles multiple concurrent clients."""
    threads = []

    # Create two client threads
    for _ in range(2):
        thread = threading.Thread(target=client_task)
        threads.append(thread)
        thread.start()

    # Wait for both threads to complete
    for thread in threads:
        thread.join()
