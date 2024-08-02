"""This module provides the server class implementation for fsearch package."""
# fsearch/server.py
import os
import socket
import ssl
import time
import threading
from fsearch.config import Config
from fsearch.utils import read_config, read_file, generate_certs
from fsearch.algorithms import regex_search

class Server:
    """
    The Server class. Starts a server from config , reads linux-path config as its database
    and handles query search connections.

    Example
    ----------
    ```
    server = Server(config_path)
    server.connect()
    ```

    Methods
    -------
    __init__(config_path: str)
        Initializes the server with configs and creates a socket.

    load_ssl()
        Secures server socket with TLS.Will generate self-signed SSL certs if configs certfile or keyfile do not exist.

    load_database()
        Loads the linux-path file as the server database 
    
    connect()
        Starts the server, binds the socket, and begins listening for connections.

    receive()
        Handles incoming connections and starts a new thread for each client.

    _handle_client(client_socket: socket.socket)
        Handles communication with a connected client.

    stop()
        Stops the server and closes the socket.
    
    search(query: str)
        searches for query in the server database with selected search algorithm.
    """

    config_path: str
    configs: Config
    server_socket: socket.socket
    is_running: bool = False
    max_payload: int = 1024 # the max request payload size. Defaults to 1024
    max_conn: int = 5 # the maximum number of concurrent connections.
    max_rows: int = 250000 #the maximum number of lines to be read from linux-path file
    database: str = ''  # the contents of linux-path used as the server database

    def __init__(self, config_path: str):
        """ Initializes the server with configs and creates a socket  """
        self.config_path = config_path
        self.configs = read_config(config_path)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.configs.ssl:
            self.load_ssl()
        self.load_database()
        self.is_running = False

    def load_ssl(self):
        """Secures server socket with TLS.Will generate self-signed SSL certs if configs certfile or keyfile do not exist."""
        if not os.path.exists(self.configs.certfile) and not os.path.exists(self.configs.keyfile):
            self.configs.certfile, self.configs.keyfile = generate_certs()

        self.server_socket = ssl.wrap_socket(
            self.server_socket,
            server_side=True,
            certfile=self.configs.certfile,
            keyfile=self.configs.keyfile,
            ssl_version=ssl.PROTOCOL_TLS
        )
    
    def load_database(self):
        """Loads the linux-path file as the server database """
        self.database = read_file(self.configs.linuxpath)

    def connect(self):
        """ Starts the server, binds the socket, and begins listening for connections. """
        host, port = self.configs.host, self.configs.port
        self.server_socket.bind((host, port))
        self.server_socket.listen(self.max_conn)
        self.is_running = True
        print(f"Server started on {host}:{port}")
        self.receive()

    def receive(self):
        """ Handles incoming connections and starts a new thread for each client. """
        while self.is_running:
            client_socket, client_address = self.server_socket.accept()
            start_time: float = time.time()
            print(f"Connection from {client_address}")

            ## read the configs again to check if reread_on_query has changed
            configs = read_config(self.config_path)

            ## if reread_on_query if true , update the self.config.linux-path and re-load the database
            if configs.reread_on_query:
                self.configs.linuxpath = configs.linuxpath
                self.load_database()   

            client_handler = threading.Thread(
                target=self._handle_client,
                args=(client_socket, start_time, client_address)
            )
            client_handler.start()

    def _handle_client(self, client_socket: socket.socket, start_time: float, client_address: str):
        """ Handles communication with a connected client. 
        
        Args:
            - client_socket (socket.socket): The server socket connection
        """
        try:
            
            ## receive connection payload and strip null characters ie '\x00' and decode to utf-8
            request_data = client_socket.recv(self.max_payload).rstrip(b'\x00').decode('utf-8')
            print(f"Received: {request_data}")
            response = self.search(request_data)
            client_socket.sendall(response.encode('utf-8'))
            duration: float = time.time() - start_time
            print(f"DEBUG: Query: {request_data}, IP: {client_address}, + Execution Time: {duration}")
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def stop(self):
        """ Stops the server and closes the socket. """
        self.is_running = False
        self.server_socket.close()
        print("Server stopped")

    def search(self, query: str) -> str:
        """ searches for query in the server database with selected search algorithm

        Args:
            - query (str): The search query.

        Returns:
            (str): The response, either; "STRING EXISTS" or "STRING NOT FOUND"
        """
        found = regex_search(self.database, query)
        if found:
            return "STRING EXISTS"
        else:
            return "STRING NOT FOUND"