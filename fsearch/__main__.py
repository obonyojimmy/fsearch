"""fsearch entry point script."""
# fsearch/__main__.py

import argparse
from fsearch import __app_name__, __version__

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
    print(config_path)

if __name__ == "__main__":
    main()