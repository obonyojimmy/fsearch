"""This module provides the utility functions for fsearch package."""
# fsearch/utils.py

import configparser
import os
from fsearch.config import Config

def read_config(config_path: str) -> Config:
    """ Reads server configurations from file to a `Config` object
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