import unittest

from fsearch.algorithms import (
    AhoCorasick,
    aho_corasick_search,
    kmp_search,
    native_search,
    rabin_karp_search,
    regex_search,
)

text = "Hello World\nThis is a test\nGoodbye World"

full_match = "This is a test"
false_match = "Not in text"
partial_match = "Not in text"


class TestNativeSearch(unittest.TestCase):
    def test_search_match(self):
        self.assertTrue(native_search(text, full_match))

    def test_no_match(self):
        self.assertFalse(native_search(text, false_match))

    def test_partial_match(self):
        self.assertFalse(native_search(text, partial_match))


class TestRegExSearch(unittest.TestCase):
    def test_search_match(self):
        self.assertTrue(regex_search(text, full_match))

    def test_no_match(self):
        self.assertFalse(regex_search(text, false_match))

    def test_partial_match(self):
        self.assertFalse(regex_search(text, partial_match))


class TestRabinKarpSearch(unittest.TestCase):
    def test_search_match(self):
        self.assertTrue(rabin_karp_search(text, full_match))

    def test_no_match(self):
        self.assertFalse(rabin_karp_search(text, false_match))

    def test_partial_match(self):
        self.assertFalse(rabin_karp_search(text, partial_match))


class TestKpmSearch(unittest.TestCase):
    def test_search_match(self):
        self.assertTrue(kmp_search(text, full_match))

    def test_no_match(self):
        self.assertFalse(kmp_search(text, false_match))

    def test_partial_match(self):
        self.assertFalse(kmp_search(text, partial_match))


class TestAhoCorasickSearch(unittest.TestCase):
    def test_search_match(self):
        self.assertTrue(aho_corasick_search(text, full_match))

    def test_no_match(self):
        self.assertFalse(aho_corasick_search(text, false_match))

    def test_partial_match(self):
        self.assertFalse(aho_corasick_search(text, partial_match))


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

        assert ac.output[7] == "his"

    def test_search(self):
        ac = AhoCorasick()
        ac.add_pattern("he")
        ac.add_pattern("she")
        ac.add_pattern("his")
        ac.add_pattern("hers")
        ac.build_automaton()

        results = ac.search("ushers")
        assert results == [(2, "he"), (2, "hers")]
