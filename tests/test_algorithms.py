import pytest
import re
from fsearch.algorithms import regex_search

def test_regex_search_match():
    content = "This is a sample text for testing."
    search_query = r"sample"
    assert regex_search(content, search_query) is True

def test_regex_search_no_match():
    content = "This is a sample text for testing."
    search_query = r"notfound"
    assert regex_search(content, search_query) is False

def test_regex_search_empty_content():
    content = ""
    search_query = r"sample"
    assert regex_search(content, search_query) is False

def test_regex_search_empty_query():
    content = "This is a sample text for testing."
    search_query = r""
    assert regex_search(content, search_query) is True  # Empty pattern matches everything

def test_regex_search_special_characters():
    content = "This is a sample text for testing."
    search_query = r"\bsample\b"
    assert regex_search(content, search_query) is True

def test_regex_search_invalid_regex():
    content = "This is a sample text for testing."
    search_query = r"(["
    with pytest.raises(re.error):
        regex_search(content, search_query)
