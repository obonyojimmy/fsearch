import pytest
import unittest
from fsearch.algorithms import (
    native_search, regex_search, rabin_karp_search, kmp_search, aho_corasick_search, AhoCorasick
)

text = "Hello World\nThis is a test\nGoodbye World"

full_match = "This is a test"
false_match = "Not in text"
partial_match = "Not in text"

class TestNativeSearch(unittest.TestCase):
    def test_search_match(self):
        assert native_search(text, full_match) == True

    def test_no_match(self):
        assert native_search(text, false_match) == False

    def test_partial_match(self):
        assert native_search(text, partial_match) == False

class TestRegExSearch(unittest.TestCase):
    def test_search_match(self):
        assert regex_search(text, full_match) == True

    def test_no_match(self):
        assert regex_search(text, false_match) == False

    def test_partial_match(self):
        assert regex_search(text, partial_match) == False

class TestRabinKarpSearch(unittest.TestCase):
    def test_search_match(self):
        assert rabin_karp_search(text, full_match) == True

    def test_no_match(self):
        assert rabin_karp_search(text, false_match) == False

    def test_partial_match(self):
        assert rabin_karp_search(text, partial_match) == False

class TestKpmSearch(unittest.TestCase):
    def test_search_match(self):
        assert kmp_search(text, full_match) == True

    def test_no_match(self):
        assert kmp_search(text, false_match) == False

    def test_partial_match(self):
        assert kmp_search(text, partial_match) == False

class TestAhoCorasickSearch(unittest.TestCase):
    def test_search_match(self):
        assert aho_corasick_search(text, full_match) == True

    def test_no_match(self):
        assert aho_corasick_search(text, false_match) == False

    def test_partial_match(self):
        assert aho_corasick_search(text, partial_match) == False

class TestAhoCorasick(unittest.TestCase):
    def test_init(self):
        ac = AhoCorasick()
        assert ac.goto == {}
        assert ac.output == {}
        assert ac.fail == {}
        assert ac.new_state == 0

    def test_add_pattern(self):
        ac = AhoCorasick()
        ac.add_pattern("he")
        ac.add_pattern("she")
        ac.add_pattern("his")
        ac.add_pattern("hers")
        
        assert ac.new_state == 9

    def test_build_automaton(self):
        ac = AhoCorasick()
        ac.add_pattern("he")
        ac.add_pattern("she")
        ac.add_pattern("his")
        ac.add_pattern("hers")
        ac.build_automaton()
        
        assert ac.output[7] == 'his'

    def test_search(self):
        ac = AhoCorasick()
        ac.add_pattern("he")
        ac.add_pattern("she")
        ac.add_pattern("his")
        ac.add_pattern("hers")
        ac.build_automaton()

        results = ac.search("ushers")
        assert results == [(2, 'he'), (2, 'hers')]

        