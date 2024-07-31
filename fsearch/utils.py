"""This module provides the utility functions for fsearch package."""
# fsearch/utils.py

import configparser
import os
import subprocess
import tempfile
from dataclasses import asdict
from typing import Tuple
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

    config_parser = configparser.ConfigParser()

    try:
        config_parser.read(config_path)
    except configparser.Error as e:
        raise Exception(f"Error reading the config file: {e}")

    defaults = dict(config_parser.defaults())
    sections = {section: dict(config_parser.items(section)) for section in config_parser.sections()}

    config = Config(**defaults, **sections)

    # Check if the config option linuxpath, path is relative
    if not os.path.isabs(config.linuxpath):
        config.linuxpath = os.path.abspath(config.linuxpath)

    print(f"Using configurations:", asdict(config))
    return config

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
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def generate_self_signed_cert() -> Tuple[str, str]:
    """Generates self-signed certificates using openssl and stores them in a temporary directory."""
    module_dir = os.path.dirname(os.path.abspath(__file__))
    cert_dir = os.path.join(module_dir, '.certs')

    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)

    certfile = os.path.join(cert_dir, "server.crt")
    keyfile = os.path.join(cert_dir, "server.key")

    # Return previous generated certs if exists
    if os.path.exists(certfile) and os.path.exists(keyfile):
        return certfile, keyfile 

    # Generate the self-signed certificate using openssl
    subprocess.check_call([
        "openssl", "req", "-x509", "-nodes", "-days", "365",
        "-newkey", "rsa:2048", "-keyout", keyfile, "-out", certfile,
        "-subj", "/C=US/ST=California/L=San Francisco/O=My Company/OU=Org/CN=mydomain.com"
    ])

    return certfile, keyfile