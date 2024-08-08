import unittest
import pytest
from unittest.mock import patch, MagicMock, call, PropertyMock, Mock
import socket
import ssl
from fsearch.server import Server
from fsearch.config import Config
from fsearch.utils import logger, read_config, read_file, generate_certs
from fsearch.algorithms import regex_search

@pytest.mark.usefixtures("config_file_cls")
class TestServer(unittest.TestCase):

    def setUp(self):
        self.config_path = self.config_file #'config.ini'
        self.mock_config = read_config(self.config_path)
        #self.server = Server(self.config_path)
    
    @patch('fsearch.server.read_file')
    @patch('fsearch.server.read_config')
    @patch('fsearch.server.ssl.wrap_socket')
    @patch('fsearch.server.socket.socket', spec=True)
    def test_init(self, mock_socket, mock_wrap_socket, mock_read_config, mock_read_file):
        mock_read_config.return_value = self.mock_config
        server = Server(self.config_path)
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        #assert isinstance(server.server_socket, mock_socket)
        #self.assertEqual(server.server_socket, mock_socket)
        self.assertEqual(server.config_path, self.config_path)
        self.assertEqual(server.configs, self.mock_config)
        self.assertFalse(server.is_running)
        if server.configs.ssl:
            mock_wrap_socket.assert_called_once()
        self.assertEqual(server.database, mock_read_file.return_value)
        self.assertEqual(server.max_conn, 5)
    
    @patch('fsearch.server.generate_certs')
    @patch('fsearch.server.os.path.exists')
    @patch('fsearch.server.ssl.wrap_socket')
    @patch('fsearch.server.read_config')
    def test_load_ssl(self, mock_read_config, mock_wrap_socket, mock_exists, mock_generate_certs):
        mock_read_config.return_value = self.mock_config
        mock_exists.side_effect = [False, False]  # Certfile and keyfile don't exist
        mock_generate_certs.return_value = ('generated_certfile', 'generated_keyfile')
        server = Server(self.config_path)
        server.configs.ssl = True
        server.load_ssl()
        mock_wrap_socket.assert_called_once()
        self.assertEqual(server.configs.certfile, 'generated_certfile')
        self.assertEqual(server.configs.keyfile, 'generated_keyfile')

    @patch('fsearch.server.read_file')
    @patch('fsearch.server.read_config')
    def test_load_database(self, mock_read_config, mock_read_file):
        mock_read_config.return_value = self.mock_config
        server = Server(self.config_path)
        server.load_database()
        self.assertEqual(server.database, mock_read_file.return_value)
    
    @patch('fsearch.server.read_config')
    @patch('fsearch.server.socket.socket')
    def test_connect(self, mock_socket, mock_read_config):
        mock_read_config.return_value = self.mock_config
        mock_socket_inst = mock_socket.return_value
        server = Server(self.config_path)
        host, port = server.configs.host, server.configs.port
        with patch.object(server, 'receive', return_value=None) as mock_receive, \
            patch.object(server, 'stop') as mock_stop, \
            patch('sys.exit') as mock_sys_exit:
                try:
                    server.connect()
                except KeyboardInterrupt:
                    mock_stop.assert_called_once()
                    mock_sys_exit.assert_called_once()
                except OSError:
                    mock_sys_exit.assert_called_once()

                mock_socket_inst.bind.assert_called_once_with((host, port))
                mock_socket_inst.listen.assert_called_once_with(server.max_conn)
                #mock_bind.assert_called_once()
                mock_receive.assert_called_once()
                self.assertTrue(server.is_running)
                assert server.is_running
                mock_sys_exit.assert_not_called()

    @patch('fsearch.server.Server', autospec=True, wraps=Server)
    @patch('fsearch.server.read_config')
    @patch('fsearch.server.socket.socket')
    @patch('fsearch.server.threading.Thread')
    def test_receive(self, mock_thread, mock_socket, mock_read_config, MockServer):
        """ Note: see https://deniscapeto.com/2021/03/06/how-to-test-a-while-true-in-python/ on test in a loop """
        mock_read_config.return_value = self.mock_config
        mock_socket_inst = mock_socket.return_value
        mock_client_socket, mock_client_address = MagicMock(), '122.12.1.2'
        mock_socket_inst.accept.return_value = (mock_client_socket, mock_client_address)
        mock_thread.start.return_value = MagicMock()

        server = Server(self.config_path)
        sentinel = PropertyMock(side_effect=[True, False])
        Server.is_running = sentinel
        #print(sentinel.call_count)
        #server.receive()
        with patch.object(server, 'load_database', return_value=None) as mock_load_database, \
            patch.object(server, '_handle_client', return_value=None) as mock_handle_client, \
            patch('fsearch.server.time.time', side_effect=0) as mock_time:
                
                server.receive()
                mock_socket_inst.accept.assert_called_once()
                mock_time.assert_called_once()
                self.assertTrue(mock_load_database.called or not mock_load_database.called)
                print(mock_thread.call_args)
                """ mock_thread.assert_called_with(
                    args=(mock_client_socket, mock_time, mock_client_address), 
                    target=mock_handle_client
                ) """
                #mock_thread.start.assert_called_once()
               

        print(sentinel.call_count)
        sentinel.reset_mock(side_effect=True, return_value=True)
        MockServer.stop()

    
    @patch('fsearch.server.read_config')
    @patch('fsearch.server.socket.socket')
    @patch('fsearch.server.regex_search')
    def test_handle_client(self, mock_regex_search, mock_socket, mock_read_config):
        mock_read_config.return_value = self.mock_config
        mock_client_socket = MagicMock()
        mock_regex_search.return_value = True
        server = Server(self.config_path)
        server.database = 'database contents'
        
        with patch('fsearch.server.time.time', side_effect=[0, 1]):
            server._handle_client(mock_client_socket, 0, 'client_address')
            mock_client_socket.recv.assert_called_once()
            mock_client_socket.sendall.assert_called_once_with(b'STRING EXISTS')
            mock_client_socket.close.assert_called_once()

    @patch('fsearch.server.Server', autospec=True, wraps=Server)
    @patch('fsearch.server.read_config')
    @patch('fsearch.server.socket.socket')
    def test_stop(self, mock_socket, mock_read_config, MockServer):
        mock_read_config.return_value = self.mock_config
        server = Server(self.config_path)
        #server.is_running = True
        mock_socket_inst = mock_socket.return_value
        sentinel = PropertyMock(return_value=False)
        Server.is_running = sentinel
        server.stop()
        print('stop.is_running.call_count', sentinel.call_count)
        self.assertFalse(server.is_running)
        mock_socket_inst.shutdown.assert_called_once_with(socket.SHUT_RDWR)
        mock_socket_inst.close.assert_called_once()
        sentinel.reset_mock(side_effect=True)
        MockServer.stop()

    @patch('fsearch.server.read_config')
    @patch('fsearch.server.regex_search')
    def test_search(self, mock_regex_search, mock_read_config):
        mock_read_config.return_value = self.mock_config
        mock_regex_search.return_value = True
        server = Server(self.config_path)
        server.database = 'database contents'

        result = server.search('query')
        self.assertEqual(result, 'STRING EXISTS')
        mock_regex_search.assert_called_once_with('database contents', 'query')