"""This module provides the utility functions for fsearch package."""
# fsearch/utils.py

import configparser
from collections import namedtuple
import os

Config = namedtuple('Config', 'linuxpath reread_on_query ssl')

def read_config(config_path) -> Config:
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