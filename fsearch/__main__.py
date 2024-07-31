"""fsearch entry point script."""
# fsearch/__main__.py

import os
import argparse
from fsearch import __app_name__, __version__
from fsearch.server import Server

def main():
    parser = argparse.ArgumentParser(description="A highly performant and secure command-line server to search text files for strings.")
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"{__app_name__} ({__version__})"
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        required=True,
        help="Path to the configuration file"
    )

    args = parser.parse_args()
    config_path = args.config

    # Check if the config path is relative
    if not os.path.isabs(config_path):
        # Update the config_path to be absolute relative to the current working directory
        config_path = os.path.abspath(config_path)
    
    print(f"Using configuration file: {config_path}")
    server = Server(config_path)
    server.connect()


if __name__ == "__main__":
    main()