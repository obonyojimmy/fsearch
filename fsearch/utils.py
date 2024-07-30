"""This module provides the utility functions for fsearch package."""
# fsearch/utils.py

import configparser
import os
from fsearch.config import Config

def read_config(config_path: str) -> Config:
    """ Reads server configurations from file to a `Config` object

    Args:
    - filepath (str): The path to the file to read.

    Returns:
    - Config: The server configuration object.

    Raises:
    - FileNotFoundError: If the provided filepath does not exists.
    """
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"The file '{config_path}' does not exist.")

    config = configparser.ConfigParser()

    try:
        config.read(config_path)
    except configparser.Error as e:
        raise Exception(f"Error reading the config file: {e}")

    defaults = dict(config.defaults())
    sections = {section: dict(config.items(section)) for section in config.sections()}

    return Config(**defaults, **sections)

def read_file(filepath: str) -> str:
    """
    Reads the contents of a file and returns a list of lines.

    Args:
    - filepath (str): The path to the file to read.

    Returns:
    - str: A str of the contents from the file, or None.

    Raises:
    - FileNotFoundError: If the provided filepath does not exists.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")

    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        return None
