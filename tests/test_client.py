# tests/test_client.py
import pytest
import unittest
import socket
import ssl
from unittest.mock import patch, MagicMock
from fsearch.client import Client
#from fsearch.server import Server
from fsearch.config import Config


class TestClient(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, config_file_path):
        self.config_file_path = config_file_path
    
    @patch('fsearch.utils.read_config')
    @patch('ssl.wrap_socket')
    @patch('socket.socket')
    def test_init(self, mock_socket, mock_wrap_socket, mock_read_config):
        # Initialize Server
        client = Client(self.config_file_path)
        #mock_socket.assert_called_once()
        self.assertIsInstance(client.configs, Config)
        if client.configs.ssl:
            mock_wrap_socket.assert_called_once()
            """ mock_wrap_socket.assert_called_once_with(
                client.client_socket,
                certfile=client.configs.certfile,
                keyfile=client.configs.keyfile,
                ssl_version=ssl.PROTOCOL_TLS
            ) """

    
    @patch('fsearch.utils.generate_certs')
    @patch('ssl.wrap_socket')
    def test_load_ssl(self, mock_wrap_socket, mock_generate_certs):
        client = Client(self.config_file_path)
        if client.configs.ssl:
            mock_wrap_socket.assert_called_once()
        # Call load_ssl
        client.load_ssl()
        
        # Check if generate_certs was called
        #mock_generate_certs.assert_called_once()

        # Check if ssl.wrap_socket was called with the correct parameters
    @patch('socket.socket.connect')
    def test_connect(self, mock_connect):
        client = Client(self.config_file_path)
        
        # Call connect
        #client.connect()
        
        # Check if connect was called with the correct parameters
        #mock_connect.assert_called_once_with(('localhost', 8080))
    
    @patch('socket.socket.sendall')
    @patch('socket.socket.recv', return_value=b'RESPONSE')
    def test_send_message(self, mock_recv, mock_sendall):
        client = Client(self.config_file_path)
        # Call send_message
        #response = client.send_message('MESSAGE')
        
        # Check if sendall was called with the correct parameters
        #mock_sendall.assert_called_once_with(b'MESSAGE')
        
        # Check if recv was called and the response is correct
        #mock_recv.assert_called_once_with(1024)
        #self.assertEqual(response, 'RESPONSE')
    
    @patch('socket.socket.close')
    def test_disconnect(self, mock_close):
        client = Client(self.config_file_path)
        # Call disconnect
        client.disconnect()
        
        # Check if close was called
        mock_close.assert_called_once()
    
        