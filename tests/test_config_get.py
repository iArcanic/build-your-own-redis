# tests/test_config_get.py

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


def send_command(command):
    with socket.create_connection(("localhost", 6379)) as sock:
        sock.sendall(command.encode('utf-8'))
        response = sock.recv(1024)
        return response.decode('utf-8')


def test_config_get_dir(start_server):
    command = "*3\r\n$6\r\nCONFIG\r\n$3\r\nGET\r\n$3\r\ndir\r\n"
    expected_response = "*2\r\n$3\r\ndir\r\n$4\r\n/tmp\r\n"
    actual_response = send_command(command)
    assert actual_response == expected_response


def test_config_get_dbfilename(start_server):
    command = "*3\r\n$6\r\nCONFIG\r\n$3\r\nGET\r\n$10\r\ndbfilename\r\n"
    expected_response = "*2\r\n$10\r\ndbfilename\r\n$8\r\ndump.rdb\r\n"
    actual_response = send_command(command)
    assert actual_response == expected_response
