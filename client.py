"""
client.py

This module provides the client for the fsearch package.

Classes:
    - ClientArgs: Represents command-line arguments for the client.
    - Client: Handles client operations including connecting to the server,
      sending messages, and managing SSL connections.

Functions:
    - main: Entry point for the client, handling argument parsing and client execution.
"""  # noqa: E501

import argparse
import os
import socket
import ssl
import sys
from typing import Optional


class ClientArgs(argparse.Namespace):
    """Represents command-line arguments for the client.

    Attributes
    ----------
    host : str
        The server's hostname or IP address.
    port : int
        The port on which the server is listening.
    cert : Optional[str]
        Path to the SSL certificate file.
    key : Optional[str]
        Path to the SSL key file.
    query : str
        The string to search for on the server.
    """

    host: str
    port: int
    cert: Optional[str]
    key: Optional[str]
    query: str


class Client:
    """
    A class to represent the client for the fsearch package.

    Attributes
    ----------
    host : str
        The server's hostname or IP address.
    port : int
        The port on which the server is listening.
    certfile : Optional[str]
        Path to the SSL certificate file.
    keyfile : Optional[str]
        Path to the SSL key file.
    client_socket : socket.socket
        The client socket for communication with the server.

    Methods
    -------
    __init__(host: str, port: int, certfile: Optional[str] = None, keyfile: Optional[str] = None):
        Initializes the client with configurations and creates a socket.
    load_ssl():
        Secures the client socket with SSL using the provided certificate and key files.
    connect():
        Connects the client to the server.
    send_message(message: str) -> str:
        Sends a message to the server and returns the response.
    """  # noqa: E501

    host: str
    port: int
    certfile: Optional[str]
    keyfile: Optional[str]
    client_socket: socket.socket

    def __init__(
        self,
        host: str,
        port: int,
        certfile: Optional[str] = None,
        keyfile: Optional[str] = None,
    ):
        """
        Initializes the client with configurations and creates a socket.

        Parameters
        ----------
        host : str
            The server's hostname or IP address.
        port : int
            The port on which the server is listening.
        certfile : Optional[str], optional
            Path to the SSL certificate file, by default None.
        keyfile : Optional[str], optional
            Path to the SSL key file, by default None.

        Raises
        ------
        Exception
            If the SSL certificate or key file paths do not exist.
        """

        self.host = host
        self.port = port
        if certfile and not os.path.exists(certfile):
            raise Exception("ssl cert path does not exist")
        if keyfile and not os.path.exists(keyfile):
            raise Exception("key path does not exist")
        self.certfile = certfile
        self.keyfile = keyfile

    def load_ssl(self):
        """
        Secures the client socket with SSL using the provided certificate and key files.

        This method wraps the client socket with SSL to enable secure communication
        with the server. If the SSL handshake fails, the process exits with an error.
        """  # noqa: E501
        certfile, keyfile = self.certfile, self.keyfile

        try:
            self.client_socket = ssl.wrap_socket(
                self.client_socket,
                certfile=certfile,
                keyfile=keyfile,
                ssl_version=ssl.PROTOCOL_TLS,
            )
        except ssl.SSLError as e:
            print(f"SSL handshake Error: {e}")
            sys.exit()

    def connect(self):
        """
        Connects the client to the server.

        This method attempts to establish a connection to the server using the
        specified host and port. If the connection fails, the process exits with an error.
        """  # noqa: E501
        try:
            host, port = self.host, self.port
            self.client_socket.connect((host, port))
            print(f"Connected to server at {host}:{port}")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            sys.exit()

    def send_message(self, message: str) -> str:
        """
        Sends a message to the server and returns the response.

        Parameters:
            message : str
                The message to send to the server.

        Returns:
            str
                The response from the server.
        """

        with socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        ) as client_socket:
            self.client_socket = client_socket
            if self.certfile:
                self.load_ssl()
            self.connect()
            try:
                self.client_socket.sendall(message.encode("utf-8"))
                response = self.client_socket.recv(1024).decode("utf-8")
                return response
            except Exception as e:
                print(f"Error sending message: {e}")
                return ""
            # finally:
            #    self.client_socket.close()


def main():
    """
    Entry point for the fsearch client.

    This function parses command-line arguments and creates a Client instance
    to send a search query to the server. The server's response is then printed
    to the console.
    """
    parser = argparse.ArgumentParser(description="fsearch client")

    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="The server port"
    )
    parser.add_argument(
        "-p", "--port", type=int, required=True, help="The server port"
    )
    parser.add_argument(
        "-c", "--cert", type=str, help="Optional SSL server cert file path"
    )
    parser.add_argument(
        "-k", "--key", type=str, help="Optional cert key file path"
    )
    parser.add_argument(
        "query", type=str, nargs="?", help="String to search for"
    )

    args: ClientArgs = parser.parse_args()  # type: ignore

    client = Client(args.host, args.port, certfile=args.cert, keyfile=args.key)
    response = client.send_message(args.query)
    print(f"Response from server: {response}")


if __name__ == "__main__":
    main()
