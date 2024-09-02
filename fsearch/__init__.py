"""
fsearch/__init__.py

The fsearch package init script.
"""

import logging

__app_name__ = "fsearch"
__version__ = "0.1.0"

logging.basicConfig(
    format="%(asctime)s : [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler()],
)
