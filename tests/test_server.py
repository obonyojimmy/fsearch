# tests/test_server.py
import pytest
import unittest
import socket
import ssl
from unittest.mock import patch, MagicMock
from fsearch.server import Server
from fsearch.config import Config

@pytest.fixture
def mock_server(config_file_path):
    with patch('fsearch.utils.read_file'), \
         patch('ssl.wrap_socket', return_value=MagicMock()), \
         patch('fsearch.utils.read_config') as mock_read_config:
        
        mock_config = MagicMock()
        mock_read_config.return_value = mock_config

        server = Server(config_file_path)
        yield server

class TestServer:
    def test_init(self, mock_server):
        server = mock_server
        assert isinstance(server.configs, Config)
        #assert isinstance(server.server_socket, socket.socket)
        assert not server.is_running

    def test_connect(self, mock_server):
        server = mock_server
        host, port = server.configs.host, server.configs.port
        with patch.object(server.server_socket, 'bind') as mock_bind:
            with patch.object(server.server_socket, 'listen') as mock_listen:
                with patch.object(server, 'receive', side_effect=KeyboardInterrupt):
                    try:
                        server.connect()
                    except KeyboardInterrupt:
                        pass

                    mock_bind.assert_called_once_with((host, port))
                    mock_listen.assert_called_once_with(5)
                    assert server.is_running

    def test_handle_client(self, mock_server):
        server = mock_server

        mock_client_socket = MagicMock()
        mock_client_socket.recv.return_value = b'hello\x00\x00'

        with patch.object(mock_client_socket, 'close') as mock_close:
            server._handle_client(mock_client_socket)

            mock_client_socket.recv.assert_called_once_with(1024)
            mock_client_socket.sendall.assert_called_once_with(b'STRING NOT FOUND')
            mock_close.assert_called_once()

    def test_stop(self, mock_server):
        server = mock_server

        server.is_running = True
        with patch.object(server.server_socket, 'close') as mock_close:
            server.stop()

            assert not server.is_running
            mock_close.assert_called_once()

    def test_search(self, mock_server):
        server = mock_server

        # Set up mock database
        server.database = 'test string\nanother string\n'

        # Call search function
        result = server.search('test string')
        assert result == "STRING EXISTS" # Simulate that the query was found

        result = server.search('blah')
        assert result == "STRING NOT FOUND" # Simulate that the query was not found