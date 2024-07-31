import pytest
from unittest.mock import mock_open, patch
from fsearch.utils import read_config, read_file, generate_self_signed_cert
from fsearch.config import Config

# Test data for read_config
config_content = """
[DEFAULT]
Server = 127.0.0.1
Port = 8080

[database]
User = admin
Password = secret
"""

def test_read_config_success():
    with patch('builtins.open', mock_open(read_data=config_content)):
        with patch('os.path.isfile') as mock_isfile:
            mock_isfile.return_value = True
            config = read_config("dummy_path")
            assert isinstance(config, Config)

def test_read_config_file_not_found():
    with patch('os.path.isfile') as mock_isfile:
        mock_isfile.return_value = False
        with pytest.raises(FileNotFoundError):
            read_config("non_existent_path")

def test_read_config_parsing_error():
    with patch('builtins.open', mock_open(read_data="[INVALID")):
        with patch('os.path.isfile') as mock_isfile:
            mock_isfile.return_value = True
            with pytest.raises(Exception):
                read_config("dummy_path")

# Test data for read_file
file_content = "Hello, world!"

def test_read_file_success():
    with patch('builtins.open', mock_open(read_data=file_content)):
        with patch('os.path.isfile') as mock_isfile:
            mock_isfile.return_value = True
            content = read_file("dummy_path")
            assert content == file_content

def test_read_file_file_not_found():
    with patch('os.path.isfile') as mock_isfile:
        mock_isfile.return_value = False
        with pytest.raises(FileNotFoundError):
            read_file("non_existent_path")

def test_read_file_generic_error():
    with patch('builtins.open', side_effect=Exception("Generic error")):
        with patch('os.path.isfile') as mock_isfile:
            mock_isfile.return_value = True
            content = read_file("dummy_path")
            assert content is None

