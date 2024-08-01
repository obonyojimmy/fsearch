"""This module provides the client class implementation for the fsearch package."""
# fsearch/client.py

import os
import socket
import ssl
from fsearch.config import Config
from fsearch.utils import read_config, generate_certs

class Client:
    """
    A class to represent the client for the fsearch package.

    Attributes
    ----------
    configs : Config
        Configuration settings for the client.
    client_socket : socket.socket
        The client socket.

    Methods
    -------
    __init__(config_path: str):
        Initializes the client with configurations and creates a socket.
    connect():
        Connects the client to the server.
    send_message(message: str) -> str:
        Sends a message to the server and returns the response.
    disconnect():
        Closes the client socket.
    """

    configs: Config
    client_socket: socket.socket

    def __init__(self, config_path: str):
        """
        Initializes the client with configurations and creates a socket.

        Args
        ----------
        config_path : str
            The path to the configuration file.
        """
        self.configs = read_config(config_path)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.configs.ssl:
            self.load_ssl()

    def load_ssl(self):
        """Secures server socket with self-signed SSL certs if certfile or keyfile do not exist."""
        if not os.path.exists(self.configs.certfile) and not os.path.exists(self.configs.keyfile):
            self.configs.certfile, self.configs.keyfile = generate_certs()

        self.client_socket = ssl.wrap_socket(
            self.client_socket,
            certfile=self.configs.certfile,
            keyfile=self.configs.keyfile,
            ssl_version=ssl.PROTOCOL_TLS
        )

    def connect(self):
        """
        Connects the client to the server.
        """
        host, port = self.configs.host, self.configs.port
        self.client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")

    def send_message(self, message: str) -> str:
        """
        Sends a message to the server and returns the response.

        Args
        ----------
        message : str
            The message to send to the server.

        Returns
        -------
        str
            The response from the server.
        """
        try:
            self.client_socket.sendall(message.encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')
            return response
        except Exception as e:
            print(f"Error sending message: {e}")
            return ""
        finally:
            self.client_socket.close()

    def disconnect(self):
        """
        Closes the client socket.
        """
        self.client_socket.close()
        print("Disconnected from server")
