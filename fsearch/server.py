"""
fsearch/server.py

This module provides the `Server` class implementation for the `fsearch` package. The `Server` class
is responsible for initializing, securing, and managing the server, as well as handling client
connections and processing search queries using a multithreaded approach.

Classes:
    - Server: A class that encapsulates the server's configuration, database loading, connection handling,
      and search functionalities.

Example usage:
    >>> from fsearch.server import Server
    >>> server = Server(config_path="config.ini")
    >>> server.connect()
"""  # noqa: E501

import logging
import os
import socket
import ssl
import sys
import threading
import time
from dataclasses import asdict
from pickle import NONE
from typing import Optional

from fsearch.algorithms import regex_search
from fsearch.config import Config
from fsearch.utils import generate_certs, read_config, read_file

logger = logging.getLogger(__name__)


class Server:
    """
    The Server class encapsulates the server's configuration, database, and socket handling.
    It provides methods to start, secure, and manage client connections. The server handles
    multiple clients concurrently and processes search queries on the loaded database.

    Attributes
    ----------
    config_path : str
        The file path to the server configuration file.
    configs : Config
        The server configuration object.
    server_socket : socket.socket
        The server's main socket for handling connections.
    is_running : bool
        A flag indicating whether the server is currently running.
    max_payload : int
        The maximum size of the request payload. Defaults to 1024.
    max_conn : int
        The maximum number of concurrent connections. Defaults to 5.
    max_rows : int
        The maximum number of lines to read from the linux-path file. Defaults to 250,000.
    database : str
        The content of the linux-path file used as the server's database.

    Methods
    -------
    __init__(config_path: str, port: Optional[int] = None, max_conn: int = 5)
        Initializes the server with configuration settings and creates a socket.

    load_ssl()
        Secures the server socket with TLS. Generates self-signed SSL certificates if the
        certfile or keyfile specified in the configuration does not exist.

    load_database()
        Loads the linux-path file content as the server's database.

    connect()
        Starts the server, binds the socket, and begins listening for incoming connections.

    receive()
        Handles incoming client connections and spawns a new thread for each client.

    _handle_client(client_socket: socket.socket, start_time: float, client_address: str)
        Handles communication with a connected client.

    stop()
        Stops the server and closes the socket.

    search(query: str) -> str
        Searches for a query in the server's database using the configured search algorithm.
    """  # noqa: E501

    config_path: str
    configs: Config
    server_socket: socket.socket
    is_running: bool = False
    # the max request payload size. Defaults to 1024
    max_payload: int = 1024
    # the maximum number of concurrent connections.
    max_conn: int = 5
    # the maximum number of lines to be read from linux-path file
    max_rows: int = 250000
    # the contents of linux-path used as the server database
    database: str = ""

    def __init__(
        self,
        config_path: str,
        port: Optional[int] = None,
        max_conn: int = 5,
        log_level: Optional[str] = None,
    ):
        """
        Initializes the Server with configuration settings and creates a socket.

        Parameters
        ----------
        config_path : str
            The file path to the configuration file.
        port : Optional[int], optional
            The port number to override the one in the configuration file, by default None.
        max_conn : int, optional
            The maximum number of concurrent connections, by default 5.
        log_level : str, optional
            Overide log level in config file, by default None.
        """  # noqa: E501

        self.config_path = config_path
        self.configs = read_config(config_path)

        # Override port in config file if provided
        if port:
            self.configs.port = port

        # Override log_level in config file if provided
        if log_level:
            self.configs.log_level = log_level

        # Configure the log level
        level = logging.getLevelName(self.configs.log_level)
        logger.setLevel(level)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ## Reconnect socket to an exisitng address
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEPORT, 1
        )

        if self.configs.ssl:  ## load ssl if only ssl is set to true
            self.load_ssl()

        logger.debug(f"Using configurations {asdict(self.configs)}")

        self.load_database()
        self.is_running = False
        self.max_conn = max_conn

    def load_ssl(self):
        """
        Secures the server socket with TLS.

        If the configuration's certfile or keyfile does not exist, this method will generate
        self-signed SSL certificates.
        """  # noqa: E501
        # if not self.configs.certfile and not self.configs.keyfile:
        #    raise ValueError("certfile not provided in configs")
        if not os.path.exists(self.configs.certfile) and not os.path.exists(  # type: ignore
            self.configs.keyfile  # type: ignore
        ):
            self.configs.certfile, self.configs.keyfile = generate_certs()

        try:
            self.server_socket = ssl.wrap_socket(
                self.server_socket,
                server_side=True,
                certfile=self.configs.certfile,
                keyfile=self.configs.keyfile,
                ssl_version=ssl.PROTOCOL_TLS,
            )
        except Exception as e:
            print("load_ssl.error", e)

    def load_database(self):
        """
        Loads the content of the linux-path file specified in the configuration as the server's database.
        """  # noqa: E501
        self.database = read_file(self.configs.linuxpath)

    def connect(self):
        """
        Starts the server, binds the socket to the host and port, and begins listening for connections.
        """  # noqa: E501
        host, port = self.configs.host, self.configs.port
        try:
            self.server_socket.bind((host, port))
            # self.server_socket.setblocking(False)
            self.server_socket.listen(self.max_conn)
            self.is_running = True
            logger.debug(f"Server started on {host}:{port}")
            self.receive()
        except KeyboardInterrupt:
            logger.debug("Exiting the server...")
            self.stop()
            sys.exit(0)
        except OSError as e:
            logger.debug(f"Exiting the server...")
            sys.exit(0)

    def receive(self):
        """
        Handles incoming connections and starts a new thread for each client.

        This method should be called after the socket is bound and listening for connections.
        """  # noqa: E501
        ## notes:  https://docs.python.org/3/howto/sockets.html

        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()

                # Re-read configs to check if reread_on_query has changed
                self.configs = read_config(self.config_path)
                logger.debug(
                    f"[REREAD_ON_QUERY] = {self.configs.reread_on_query}"
                )

                start_time: float = time.perf_counter()

                # Re-load the database if reread_on_query is enabled
                if self.configs.reread_on_query:
                    self.load_database()

                client_handler = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, start_time, client_address),
                )
                client_handler.start()
            except ssl.SSLError as e:
                logger.error(f"Client SSL ERROR: {e}")
            except Exception as e:
                logger.debug(f"SERVER CONNECTIONS CLOSED")

    def _handle_client(
        self,
        client_socket: socket.socket,
        start_time: float,
        client_address: str,
    ):
        """
        Handles communication with a connected client.

        Parameters
        ----------
        client_socket : socket.socket
            The socket object representing the client connection.
        start_time : float
            The time when the connection was established.
        client_address : str
            The address of the connected client.
        """

        try:
            # Receive request payload, strip null characters, and decode to UTF-8  # noqa: E501
            request_data = (
                client_socket.recv(self.max_payload)
                .rstrip(b"\x00")
                .decode("utf-8")
            )
            response = self.search(request_data)
            duration: float = time.perf_counter() - start_time
            client_socket.sendall(response.encode("utf-8"))
            duration_ms = round(duration * 1000, 2)
            logger.debug(
                f"Query: {request_data}, IP: {client_address}, Execution Time: {duration_ms} ms"  # noqa: E501
            )
        except Exception as e:
            logger.error(f"Error handling client: {e}")

    def stop(self):
        """
        Stops the server and closes the socket.
        """
        self.is_running = False
        try:
            # self.server_socket.close()
            self.server_socket.shutdown(socket.SHUT_RDWR)
            logger.debug("---Server stopped---")
        except OSError:
            pass
        except Exception as e:
            logger.error(f"Error stopping server: {e}")
        self.server_socket.close()

    def search(self, query: str) -> str:
        """
        Searches for the specified query in the server's database using the configured search algorithm.

        Parameters
        ----------
        query : str
            The search query.

        Returns
        -------
        str
            The search result, either "STRING EXISTS" or "STRING NOT FOUND".
        """  # noqa: E501

        found = regex_search(self.database, query)
        if found:
            return "STRING EXISTS"
        else:
            return "STRING NOT FOUND"
