import pytest
from unittest.mock import patch, MagicMock, mock_open
from fsearch.server import Server
from fsearch.config import Config

# Sample configuration data
config_content = """
[DEFAULT]
host = 127.0.0.1
port = 8080
certfile = server.crt
keyfile = server.key
log_level = INFO
linuxpath = samples/200k.txt
reread_on_query = False
"""

# Sample file content
file_content = "Sample file content"

@pytest.fixture
def mock_config():
    with patch('fsearch.utils.read_config', return_value=Config(
        host='127.0.0.1', port=8080, certfile='server.crt', keyfile='server.key',
        log_level='INFO', linuxpath='samples/200k.txt', reread_on_query=False
    )), patch('fsearch.utils.read_file', return_value=file_content):
        yield

@pytest.fixture
def mock_server(mock_config):
    with patch('ssl.wrap_socket', return_value=MagicMock()):
        server = Server(config_path='dummy_path')
        yield server

def test_server_init(mock_server):
    assert mock_server.configs.host == '127.0.0.1'
    assert mock_server.configs.port == 8080
    assert mock_server.configs.certfile == 'server.crt'
    assert mock_server.configs.keyfile == 'server.key'
    assert mock_server.configs.linuxpath == 'samples/200k.txt'
    assert not mock_server.configs.reread_on_query
    assert mock_server.is_running is False

def test_server_connect(mock_server):
    with patch('socket.socket.bind') as mock_bind, \
         patch('socket.socket.listen') as mock_listen, \
         patch('threading.Thread.start') as mock_thread_start, \
         patch('fsearch.server.Server.receive', return_value=None):
        mock_server.connect()
        mock_bind.assert_called_with(('127.0.0.1', 8080))
        mock_listen.assert_called_with(5)
        assert mock_server.is_running is True

def test_server_receive(mock_server):
    client_socket_mock = MagicMock()
    client_socket_mock.recv.return_value = b"test query"

    with patch('socket.socket.accept', return_value=(client_socket_mock, ('127.0.0.1', 12345))), \
         patch('threading.Thread.start') as mock_thread_start:
        mock_server.is_running = True
        mock_server.receive()
        mock_thread_start.assert_called_once()

def test_server_handle_client(mock_server):
    client_socket_mock = MagicMock()
    client_socket_mock.recv.return_value = b"test query"

    with patch('fsearch.server.regex_search', return_value=True):
        mock_server._handle_client(client_socket_mock)
        client_socket_mock.sendall.assert_called_with(b"STRING EXISTS")

    with patch('fsearch.server.regex_search', return_value=False):
        mock_server._handle_client(client_socket_mock)
        client_socket_mock.sendall.assert_called_with(b"STRING NOT FOUND")

def test_server_stop(mock_server):
    with patch('socket.socket.close') as mock_close:
        mock_server.stop()
        assert mock_server.is_running is False
        mock_close.assert_called_once()

def test_server_search(mock_server):
    with patch('fsearch.server.regex_search', return_value=True):
        response = mock_server.search("test query")
        assert response == "STRING EXISTS"

    with patch('fsearch.server.regex_search', return_value=False):
        response = mock_server.search("test query")
        assert response == "STRING NOT FOUND"
