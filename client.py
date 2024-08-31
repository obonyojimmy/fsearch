"""This module provides the client to fsearch."""
# client.py

import argparse
import os
import socket
import ssl
import sys
from typing import Optional


class ClientArgs(argparse.Namespace):
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
    """

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

        Args
        ----------
        port (int): The server port
        certfile (str): The server ssl cert path
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
        """Secures server socket with self-signed SSL certs if certfile or keyfile do not exist."""  # noqa: E501
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
        """
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

        Args
        ----------
        message : str
            The message to send to the server.

        Returns
        -------
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
    """client entypoint"""
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
