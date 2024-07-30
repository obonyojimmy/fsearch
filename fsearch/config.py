"""This module provides the configuration object for fsearch package."""
# fsearch/config.py

from dataclasses import dataclass

@dataclass
class Config:
    host: str = '0.0.0.0'
    port: int = 8080
    certfile: str = 'server.crt'
    keyfile: str = 'server.key'
    log_level: str = 'INFO'
    reread_on_query: bool = False
