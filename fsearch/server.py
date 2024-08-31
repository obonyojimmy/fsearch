"""This module provides the server class implementation for fsearch package."""

# fsearch/server.py
import os
import socket
import ssl
import sys
import threading
import time
from dataclasses import asdict
from typing import Optional

from fsearch.algorithms import regex_search
from fsearch.config import Config
from fsearch.utils import generate_certs, logger, read_config, read_file


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
    """  # noqa: E501

    config_path: str
    configs: Config
    server_socket: socket.socket
    is_running: bool = False
    max_payload: int = 1024  # the max request payload size. Defaults to 1024
    max_conn: int = 5  # the maximum number of concurrent connections.
    max_rows: int = (
        250000  # the maximum number of lines to be read from linux-path file
    )
    database: str = (
        ""  # the contents of linux-path used as the server database
    )

    def __init__(
        self, config_path: str, port: Optional[int] = None, max_conn: int = 5
    ):
        """Initializes the server with configs and creates a socket"""
        self.config_path = config_path
        self.configs = read_config(config_path)

        if port:
            ## overide port in config file
            self.configs.port = port

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
        """Secures server socket with TLS.
        Will generate self-signed SSL certs if configs certfile or keyfile do not exist."""  # noqa: E501
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
        """Loads the linux-path file as the server database"""
        self.database = read_file(self.configs.linuxpath)

    def connect(self):
        """Starts the server, binds the socket, and begins listening for connections."""  # noqa: E501
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
        """Handles incoming connections and starts a new thread for each client.
        Should be called after socket is bound and listening"""  # noqa: E501
        ## notes:  https://docs.python.org/3/howto/sockets.html
        # print(self.is_running)
        # return None
        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                # print('receive loop')

                ## read the configs again to check if reread_on_query has changed  # noqa: E501
                self.configs = read_config(self.config_path)
                logger.debug(
                    f"DEBUG: [REREAD_ON_QUERY] = {self.configs.reread_on_query}"  # noqa: E501
                )

                start_time: float = time.perf_counter()

                ## if reread_on_query if true , re-load the database
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
        """Handles communication with a connected client.

        Args:
            - client_socket (socket.socket): The server socket connection
        """
        try:
            ## receive connection payload, strip null characters ie '\x00' and decode to utf-8  # noqa: E501
            request_data = (
                client_socket.recv(self.max_payload)
                .rstrip(b"\x00")
                .decode("utf-8")
            )
            response = self.search(request_data)
            duration: float = time.perf_counter() - start_time
            client_socket.sendall(response.encode("utf-8"))

            logger.debug(
                f"DEBUG: Query: {request_data}, IP: {client_address}, + Execution Time: {duration * 1000}"  # noqa: E501
            )
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            pass
            # client_socket.close()

    def stop(self):
        """Stops the server and closes the socket."""
        self.is_running = False
        try:
            # self.server_socket.close()
            self.server_socket.shutdown(socket.SHUT_RDWR)
            logger.debug("---Server stopped---")
        except OSError:
            pass
        except Exception as e:
            logger.debug(f"Error stopping server: {e}")
        self.server_socket.close()

    def search(self, query: str) -> str:
        """searches for query in the server database with selected search algorithm

        Args:
            - query (str): The search query.

        Returns:
            (str): The response, either; "STRING EXISTS" or "STRING NOT FOUND"
        """  # noqa: E501
        found = regex_search(self.database, query)
        if found:
            return "STRING EXISTS"
        else:
            return "STRING NOT FOUND"
