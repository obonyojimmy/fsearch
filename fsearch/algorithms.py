"""This module provides the search algorithms functions for fsearch package."""
# fsearch/algorithms.py

import re

def regex_search(content, search_query):
    """
    Perform a regex search on the provided content.
    
    Args:
    - content (str): The content to search within.
    - search_query (str): The regex pattern to search for.
    
    Returns:
    - bool: True if the pattern is found, False otherwise.
    """
    pattern = re.compile(search_query)
    return bool(pattern.search(content))