from dataclasses import fields

# import pytest
from fsearch.config import Config


class TestConfig:
    def test_default_values(self):
        custom_values = {
            "host": "127.0.0.1",
            "port": 9090,
            "certfile": "custom.crt",
            "keyfile": "custom.key",
            "log_level": "DEBUG",
            "linuxpath": "custom/path.txt",
            "reread_on_query": True,
        }
        config = Config(**custom_values)
        for key, value in custom_values.items():
            assert getattr(config, key) == value
        assert config.extra == {}

    def test_extra_values(self):
        extra_values = {
            "host": "127.0.0.1",
            "port": 9090,
            "custom_param1": "value1",
            "custom_param2": 12345,
        }
        config = Config(**extra_values)
        assert config.host == "127.0.0.1"
        assert config.port == 9090
        assert config.extra == {
            "custom_param1": "value1",
            "custom_param2": 12345,
        }
