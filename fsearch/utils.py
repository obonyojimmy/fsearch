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
      Config: The server configuration object.

    Raises:
      FileNotFoundError: If the provided filepath does not exists.
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
      str: A str of the contents from the file, or None.

    Raises:
      FileNotFoundError: If the provided filepath does not exists.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")

    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        return None

def hash_words(words) -> int:
    """
    Generate a hash for a list of words.

    Args:
      words (list): List of words to hash.

    Returns:
      int: Hash value of the words.
    """
    return hash(' '.join(words))

def compute_lps(pattern: str) -> list:
    """
    Compute the longest prefix suffix (LPS) array for the pattern.
    
    The LPS array is used to skip characters while matching.

    Parameters:
      pattern (list): List of words representing the pattern.

    Returns:
      list: LPS array for the pattern.
    """
    lps = [0] * len(pattern)
    j = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[j]:
            j += 1
            lps[i] = j
            i += 1
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                lps[i] = 0
                i += 1
    return lps