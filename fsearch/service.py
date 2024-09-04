"""
fsearch/service.py

This module provides the functionality to create and manage a systemd service for the fsearch server.

It includes the ability to generate a systemd service file, place it in the appropriate directory, and start the service.
The module also defines a command-line interface (CLI) for running the fsearch server as a service.

Functions:
----------
- create_service(config_file: str, port: int = 8080):
    Creates and starts a systemd service for the fsearch server.

Classes:
--------
- ParserArgs(argparse.Namespace):
    Custom argument parser namespace to hold the command-line arguments.

Entry Point:
------------
- main():
    Parses command-line arguments and creates the fsearch systemd service.
"""  # noqa: E501

import argparse
import os
import shutil
from subprocess import call

from fsearch.templates import service_template


def create_service(config_file: str, port: int = 8080):
    """
    Creates and starts a systemd service for the fsearch server.

    This function generates a systemd service file based on a template, places it in the user's systemd directory,
    reloads the systemd daemon, and starts the service.

    Args:
        config_file (str): The path to the server configuration file.
        port (int, optional): The port on which the fsearch server should run. Defaults to 8080.
    """  # noqa: E501

    # Path to the target systemd user directory
    target_service_dir = os.path.expanduser("~/.config/systemd/user")
    target_service_file = os.path.join(target_service_dir, "fsearch.service")

    # Ensure the target directory exists
    os.makedirs(target_service_dir, exist_ok=True)

    # the current working directory
    working_dir = os.getcwd()

    ## get the install path of fsearch
    exec_path = shutil.which("fsearch")

    ## define the service template
    service_defination = service_template.format(
        exec_path=exec_path,
        config_file=config_file,
        working_dir=working_dir,
        port=port,
    )

    # Create the service file to the systemd user directory
    with open(target_service_file, "w") as file:
        file.write(service_defination)

    # Reload systemd user daemon to recognize the new service
    call(["systemctl", "--user", "daemon-reload"])

    # Enable the service to start on user login
    # call(['systemctl', '--user', 'enable', 'fsearch.service'])

    # Start the service immediately
    call(["systemctl", "--user", "start", "fsearch.service"])


class ParserArgs(argparse.Namespace):
    """
    Custom argument parser namespace to hold the command-line arguments.

    Attributes:
        config (str): The path to the server configuration file.
        port (int): The port on which the fsearch server should run. Defaults to 8080.
    """  # noqa: E501

    config: str
    port: int = 8080


def main():
    """
    Parses command-line arguments and creates the fsearch systemd service.

    This function sets up the argument parser, reads the config file and port from the command-line arguments,
    and then calls create_service() to create and start the fsearch server as a systemd service.
    """  # noqa: E501

    parser = argparse.ArgumentParser(
        description="Run fsearch server as a service."
    )

    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to the server configuration file",
    )

    parser.add_argument(
        "-p", "--port", type=int, default=8080, help="The server port"
    )

    args: ParserArgs = parser.parse_args()  # type: ignore
    config_file = args.config
    port = args.port

    if not args.config:
        parser.print_help()

    ## create and run the service
    create_service(config_file, port)


if __name__ == "__main__":
    main()
