"""This module provides the server class implementation for fsearch package."""
# fsearch/server.py
import os
import socket
import ssl
import threading
from fsearch.config import Config
from fsearch.utils import read_config, read_file, generate_certs
from fsearch.algorithms import regex_search

global file_contents
file_contents = ""

class Server:
    """
    A class used to represent a Server.

    ...

    Attributes
    ----------
    configs : Config
        Configuration object for the server
    server_socket : socket.socket
        The server's socket
    is_running : bool
        Server running state

    Methods
    -------
    __init__(config_path: str)
        Initializes the server with configs and creates a socket.

    connect()
        Starts the server, binds the socket, and begins listening for connections.

    receive()
        Handles incoming connections and starts a new thread for each client.

    _handle_client(client_socket: socket.socket)
        Handles communication with a connected client.

    stop()
        Stops the server and closes the socket.
    """

    configs: Config
    server_socket: socket.socket
    is_running: bool = False

    def __init__(self, config_path: str):
        """ Initializes the server with configs and creates a socket  """
        self.configs = read_config(config_path)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.configs.ssl:
            self.load_ssl()
        self.is_running = False
        if not self.configs.reread_on_query:
            global file_contents
            file_contents = read_file(self.configs.linuxpath)

    def load_ssl(self):
        """Secures server socket with self-signed SSL certs if certfile or keyfile do not exist."""
        if not os.path.exists(self.configs.certfile) and not os.path.exists(self.configs.keyfile):
            self.configs.certfile, self.configs.keyfile = generate_certs()

        self.server_socket = ssl.wrap_socket(
            self.server_socket,
            server_side=True,
            certfile=self.configs.certfile,
            keyfile=self.configs.keyfile,
            ssl_version=ssl.PROTOCOL_TLS
        )

    def connect(self):
        """ Starts the server, binds the socket, and begins listening for connections. """
        host, port = self.configs.host, self.configs.port
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.is_running = True
        print(f"Server started on {host}:{port}")
        self.receive()

    def receive(self):
        """ Handles incoming connections and starts a new thread for each client. """
        while self.is_running:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection from {client_address}")
            client_handler = threading.Thread(
                target=self._handle_client,
                args=(client_socket,)
            )
            client_handler.start()

    def _handle_client(self, client_socket: socket.socket):
        """ Handles communication with a connected client. 
        
        Args:
        - client_socket (str): The server socket connection
        
        """
        try:
            request_data = client_socket.recv(1024).decode('utf-8')
            print(f"Received: {request_data}")
            if self.configs.reread_on_query:
                global file_contents
                file_contents = read_file(self.configs.linuxpath)
            response = self.search(request_data)
            client_socket.sendall(response.encode('utf-8'))
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def stop(self):
        """ Stops the server and closes the socket. """
        self.is_running = False
        self.server_socket.close()
        print("Server stopped")

    def search(self, query) -> str:
        """ wraps search algorithms function calls """
        global file_contents
        found = regex_search(file_contents, query)
        if found:
            return "STRING EXISTS"
        else:
            return "STRING NOT FOUND"