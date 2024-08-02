import pytest
from dataclasses import fields
from fsearch.config import Config

class TestConfig:
    def test_default_values(self):
        custom_values = {
            'host': '127.0.0.1',
            'port': 9090,
            'certfile': 'custom.crt',
            'keyfile': 'custom.key',
            'log_level': 'DEBUG',
            'linuxpath': 'custom/path.txt',
            'reread_on_query': True
        }
        config = Config(**custom_values)
        for key, value in custom_values.items():
            assert getattr(config, key) == value
        assert config.extra == {}

    def test_extra_values(self):
        extra_values = {
            'host': '127.0.0.1',
            'port': 9090,
            'custom_param1': 'value1',
            'custom_param2': 12345
        }
        config = Config(**extra_values)
        assert config.host == '127.0.0.1'
        assert config.port == 9090
        assert config.extra == {'custom_param1': 'value1', 'custom_param2': 12345}

    def test_combined_values(self):
        combined_values = {
            'host': '127.0.0.1',
            'port': 9090,
            'certfile': 'custom.crt',
            'keyfile': 'custom.key',
            'log_level': 'DEBUG',
            'linuxpath': 'custom/path.txt',
            'reread_on_query': True,
            'custom_param1': 'value1',
            'custom_param2': 12345
        }
        config = Config(**combined_values)
        assert config.host == '127.0.0.1'
        assert config.port == 9090
        assert config.certfile == 'custom.crt'
        assert config.keyfile == 'custom.key'
        assert config.log_level == 'DEBUG'
        assert config.linuxpath == 'custom/path.txt'
        assert config.reread_on_query is True
        assert config.extra == {'custom_param1': 'value1', 'custom_param2': 12345}

    def test_partial_values(self):
        partial_values = {
            'host': '192.168.1.1',
            'certfile': 'partial.crt'
        }
        config = Config(**partial_values)
        assert config.host == '192.168.1.1'
        assert config.certfile == 'partial.crt'
        assert config.port == 8080
        assert config.keyfile == 'server.key'
        assert config.log_level == 'INFO'
        assert config.linuxpath == 'samples/200k.txt'
        assert config.reread_on_query is False
        assert config.extra == {}
