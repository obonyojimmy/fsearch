"""
fsearch/config.py

This module provides the configuration class for the `fsearch` package.
It defines the `Config` class, which is responsible for managing the server's
configuration settings, including network details, SSL certificates,
logging levels, and other optional parameters.

Classes:
    - Config: Represents the configuration settings for the `fsearch` server.

Example usage:

    >>> config = Config(host="127.0.0.1", port=9090, ssl=True)
    >>> print(config.host)
    127.0.0.1

    >>> print(config.port)
    9090

    >>> print(config.ssl)
    True
"""

from dataclasses import dataclass, field, fields
from typing import Optional


@dataclass
class Config:
    """The base server configuration class.

    Attributes:
        host (str): The server's hostname or IP address. Defaults to '0.0.0.0'.
        port (int): The port number on which the server will listen. Defaults to 8080.
        ssl (bool): Whether SSL is enabled. Defaults to False.
        certfile (str): The path to the SSL certificate file. Defaults to 'server.crt'.
        keyfile (str): The path to the SSL key file. Defaults to 'server.key'.
        log_level (str): The logging level for the server. Defaults to 'DEBUG'.
        linuxpath (str): The default path for sample data files. Defaults to 'samples/200k.txt'.
        reread_on_query (bool): Whether to reread the configuration file on each query. Defaults to False.
        extra (dict): Additional configuration parameters not explicitly defined as attributes.
    """  # noqa: E501

    host: str = "0.0.0.0"
    port: int = 8080
    ssl: bool = False
    certfile: str = "server.crt"
    keyfile: str = "server.key"
    log_level: str = "DEBUG"
    linuxpath: str = "samples/200k.txt"
    reread_on_query: bool = False
    extra: dict = field(default_factory=dict)

    def __init__(self, **kwargs):
        """
        Initializes the Config object with the provided keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments used to initialize the configuration fields.
        """  # noqa: E501
        for f in fields(self):
            key = f.name.lower()
            if key in kwargs:
                val: str = kwargs.pop(key)
                if f.type == "bool" and not isinstance(val, bool):  # type: ignore
                    val = val.lower() in ("yes", "true", "on" "1")  # type: ignore

                if f.type == "int" and not isinstance(val, int):  # type: ignore
                    val = int(val)  # type: ignore

                setattr(self, key, val)
            else:
                setattr(self, key, f.default)

        # Store any additional kwargs in the extra dictionary
        self.extra = kwargs
