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

    def __init__(self, **kwargs):
        # Initialize the dataclass fields
        for f in fields(self):
            key = f.name.lower()
            if key in kwargs:
                val: str = kwargs.pop(key)
                if f.type.__name__ == 'bool' and not isinstance(val, bool):
                    val = val.lower() in ("yes", "true", "on" "1")
                
                if f.type.__name__ == 'int' and not isinstance(val, int):
                    val = int(val)
                
                setattr(self, key, val)
            else:
                setattr(self, key, f.default)

        # Store any additional kwargs in the extra dictionary
        self.extra = kwargs
