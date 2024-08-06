# tests/test_server.py
import pytest
import unittest
import socket
import ssl
import sys
import time
import threading
from unittest.mock import patch, MagicMock
from fsearch.server import Server
from fsearch.config import Config
from unittest import mock

@pytest.fixture
def mock_server(config_file_path):
    with patch('fsearch.utils.read_file'), \
        patch('ssl.wrap_socket', return_value=MagicMock()), \
        patch('fsearch.utils.read_config') as mock_read_config:
        
        mock_config = MagicMock()
        mock_read_config.return_value = mock_config

        server = Server(config_file_path, re_connect=False)
        yield server

class TestServer:
    def test_init(self, mock_server):
        server = mock_server
        assert isinstance(server.configs, Config)
        #assert isinstance(server.server_socket, socket.socket)
        assert not server.is_running

    def test_connect(self, mock_server: Server):
        server = mock_server
        host, port = server.configs.host, server.configs.port

        with patch.object(socket.socket, 'bind') as mock_bind, \
            patch.object(socket.socket, 'listen') as mock_listen, \
            patch.object(server, 'receive') as mock_receive, \
            patch.object(server, 'stop') as mock_stop, \
            patch('sys.exit') as mock_sys_exit:
                try:
                    server.connect()
                except KeyboardInterrupt:
                    mock_stop.assert_called_once()
                    mock_sys_exit.assert_called_once()
                except OSError:
                    mock_sys_exit.assert_called_once()

                mock_bind.assert_called_once_with((host, port))
                mock_listen.assert_called_once_with(server.max_conn)
                mock_bind.assert_called_once()
                mock_receive.assert_called_once()
                assert server.is_running
                mock_sys_exit.assert_not_called()

    def test_receive(self, mock_server: Server):
        server = mock_server
        #server = MagicMock()
        mock_client_address = ('127.0.0.1', 12345)
        #patch(threading.Thread) as mock_thread, \
        #patch.object(server, 'is_running', return_value=[True, False]), \
        #patch.object(server, 'is_running', return_value=[True, False]) as mock_running, \
        #patch.object(server, 'receive') as mock_recive, \
        #patch('threading.Thread.start') as mock_thread_start, \
        #patch.object(socket.socket, 'accept', return_value=(mock_client_socket, mock_client_address)) as mock_accept
        
        with patch('time.time') as mock_time, \
            patch.object(threading, 'Thread') as mock_thread, \
            patch('fsearch.utils.read_config') as mock_read_config, \
            patch.object(server, 'is_running', side_effect=[True, False]), \
            patch.object(server, 'receive') as mock_receive:
            #server.is_running = True
            assert server.is_running
            def stop_server():
                server.is_running = False
            #mock_receive.side_effect = stop_server
            #server.receive()
            mock_receive()
            
            #mock_read_config.assert_called_once()
            mock_thread.assert_called_once()
            #mock_time.assert_called_once()
            
            #server.is_running = True
            #mock_recive()
            #mock_time.assert_called_once()
            #mock_thread.start.assert_called_once()

    def test_handle_client(self, mock_server):
        server = mock_server

        mock_client_socket = MagicMock()
        mock_client_socket.recv.return_value = b'hello\x00\x00'

        with patch.object(mock_client_socket, 'close') as mock_close:
            start_time = time.time()
            client_address = '1.1.1.1.1'
            server._handle_client(mock_client_socket, start_time, client_address)

            mock_client_socket.recv.assert_called_once_with(1024)
            mock_client_socket.sendall.assert_called_once_with(b'STRING NOT FOUND')
            mock_close.assert_called_once()

    def test_stop(self, mock_server):
        server = mock_server

        server.is_running = True
        with patch.object(socket.socket, 'close') as mock_close, \
            patch.object(socket.socket, 'shutdown') as mock_shutdown:
                server.stop()

                assert not server.is_running
                mock_shutdown.assert_called_once()
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