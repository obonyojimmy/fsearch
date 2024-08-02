"""This module provides the configuration object for fsearch package."""
# fsearch/config.py

from dataclasses import dataclass, field, fields

@dataclass
class Config:
    """ The base server configuration object """
    host: str = '0.0.0.0'
    port: int = 8080
    ssl: bool = True
    certfile: str = 'server.crt'
    keyfile: str = 'server.key'
    log_level: str = 'INFO'
    linuxpath: str = 'samples/200k.txt'
    reread_on_query: bool = False
    extra: dict = field(default_factory=dict)

    def __post_init__(self):
        for key, value in self.extra.items():
            setattr(self, key, value)

    def __init__(self, **kwargs):
        # Initialize the dataclass fields
        for f in fields(self):
            if f.name in kwargs:
                setattr(self, f.name, kwargs.pop(f.name))
            else:
                setattr(self, f.name, f.default)

        # Store any additional kwargs in the extra dictionary
        self.extra = kwargs
