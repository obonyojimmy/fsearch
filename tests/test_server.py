# tests/test_server.py

import pytest
from unittest.mock import patch, MagicMock
from fsearch.server import Server
from fsearch.config import Config

# Sample file content
file_content = "Sample file content"

@pytest.fixture
def mock_server(config_file_path):
    with patch('fsearch.utils.read_file', return_value=file_content), \
         patch('ssl.wrap_socket', return_value=MagicMock()):
        server = Server(config_path=config_file_path)
        yield server

def test_server_init(mock_server):
    server = mock_server
    assert isinstance(server.configs, Config)
