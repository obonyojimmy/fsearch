"""
fsearch/algorithms.py

This module contains various string search algorithms implemented in Python. Each algorithm searches for
an exact match of a given pattern within a provided text. The module includes the following search functions:

- `native_search`: Performs a naive search for a pattern in the text.
- `regex_search`: Uses regular expressions to find a full line match of the pattern.
- `rabin_karp_search`: Implements the Rabin-Karp algorithm for searching a full line match.
- `kmp_search`: Applies the Knuth-Morris-Pratt (KMP) algorithm to find a full line match.
- `aho_corasick_search`: Applies the Aho-Corasick algorithm algorithm to find a full line match.

The functions provided are designed to work with multi-line text and search for patterns that match entire lines.

Functions:
- native_search(text: str, pattern: str) -> bool
- regex_search(text: str, pattern: str) -> bool
- rabin_karp_search(text: str, pattern: str) -> bool
- kmp_search(text: str, pattern: str) -> bool
- aho_corasick_search(text: str, pattern: str) -> bool

Example usage:

    >>> text = "Hello world\\nThis is a test\\nAnother line"
    >>> pattern = "This is a test"
    >>> native_search(text, pattern)
    True

    >>> regex_search(text, pattern)
    True

    >>> rabin_karp_search(text, pattern)
    True

    >>> kmp_search(text, pattern)
    True

    >>> aho_corasick_search(text, pattern)
    True
"""  # noqa: E501

from __future__ import annotations

import re
from collections import deque

from fsearch.utils import compute_lps


def native_search(text: str, pattern: str):
    """
    Search for an exact match of the pattern in the provided text using a naive search algorithm.

    This function splits the input `text` into individual lines and checks each line for an exact match
    with the `pattern`. If an exact match is found, the function returns `True`; otherwise, it returns `False`.

    Args:
        text (str): The text in which to search for the pattern. This text may contain multiple lines.
        pattern (str): The exact pattern to search for within the text.

    Returns:
        bool: `True` if the pattern is found as an exact match in any line of the text; `False` otherwise.

    Example:
        >>> text = "Hello world\\nThis is a test\\nAnother line"
        >>> pattern = "This is a test"
        >>> native_search(text, pattern)
        True

        >>> pattern = "Not in text"
        >>> native_search(text, pattern)
        False
    """  # noqa: E501
    for line in text.split("\n"):
        if line == pattern:
            return True
    return False


def regex_search(text: str, pattern: str) -> bool:
    """
    Search for an exact match of the pattern in the provided text using regular expressions.

    This function uses regular expressions to find an exact match of the `pattern` in the `text`.
    It ensures that the pattern matches an entire line within the text.

    Args:
        text (str): The text in which to search for the pattern. This text may contain multiple lines.
        pattern (str): The exact pattern string to search for within the text.

    Returns:
        bool: `True` if the pattern is found as an exact match on any line in the text; `False` otherwise.

    Example:
        >>> text = "Hello world\\nThis is a test\\nAnother line"
        >>> pattern = "This is a test"
        >>> regex_search(text, pattern)
        True

        >>> pattern = "Not in text"
        >>> regex_search(text, pattern)
        False
    """  # noqa: E501
    # Compile the regex pattern to match the whole line
    regex = re.compile(f"^{re.escape(pattern)}$", re.MULTILINE)

    # Search through the text
    matches = regex.search(text)

    return matches is not None


def rabin_karp_search(text: str, pattern: str):
    """
    Search for a full line match of a pattern in the provided text using the Rabin-Karp algorithm.

    This function implements the Rabin-Karp algorithm to find an exact line-by-line match of the
    `pattern` in the `text`. It calculates hash values for the `pattern` and compares them with
    the hash values of each line in the text to detect potential matches. If the hash values match,
    the function performs a direct comparison to ensure there are no hash collisions.

    Args:
        text (str): The text in which to search for the pattern. This text may contain multiple lines.
        pattern (str): The exact pattern to search for within the text.

    Returns:
        bool: `True` if the pattern is found as an exact match on any line in the text; `False` otherwise.

    Example:
        >>> text = "Hello world\\nThis is a test\\nAnother line"
        >>> pattern = "This is a test"
        >>> rabin_karp_search(text, pattern)
        True

        >>> pattern = "Not in text"
        >>> rabin_karp_search(text, pattern)
        False
    """  # noqa: E501
    if not pattern or not text:
        return False

    # Define a prime number for the hash function
    prime = 101

    # Calculate the length of the pattern
    m = len(pattern)

    # Initialize hash values for pattern
    pattern_hash = 0

    # Calculate the hash value of the pattern
    for i in range(m):
        pattern_hash = prime * pattern_hash + ord(pattern[i])

    lines = text.split("\n")
    for line in lines:
        n = len(line)
        if n != m:
            continue

        # Initialize hash value for current line
        current_hash = 0
        for i in range(m):
            current_hash = prime * current_hash + ord(line[i])

        # Compare the hash values
        if pattern_hash == current_hash:
            # Check for exact match to avoid hash collision
            if line == pattern:
                return True

    return False


def kmp_search(text: str, pattern: str) -> bool:
    """
    Search for a full line match of a pattern in the provided text using the Knuth-Morris-Pratt (KMP) algorithm.

    This function implements the KMP algorithm to efficiently find an exact line-by-line match of the
    `pattern` in the `text`. The KMP algorithm preprocesses the pattern to create a longest prefix suffix (LPS)
    array that is used to skip unnecessary comparisons during the search process.

    Args:
        text (str): The content of the text to search. This may contain multiple lines.
        pattern (str): The search string to find within the text.

    Returns:
        bool: `True` if the pattern is found as a full match on a stand-alone line, otherwise `False`.

    Example:
        >>> text = "Hello world\\nThis is a test\\nAnother line"
        >>> pattern = "This is a test"
        >>> kmp_search(text, pattern)
        True

        >>> pattern = "Not in text"
        >>> kmp_search(text, pattern)
        False
    """  # noqa: E501

    def kmp_search_line(pattern: str, line: str) -> bool:
        """
        Perform KMP search for a pattern in a single line.

        Args:
            pattern (str): The pattern string to search for.
            line (str): The line of text in which to search.

        Returns:
            bool: `True` if the pattern matches the full line, otherwise `False`.
        """  # noqa: E501
        m = len(pattern)
        n = len(line)

        if m != n:
            return False

        lps = compute_lps(pattern)
        i = 0  # Index for line
        j = 0  # Index for pattern

        while i < n:
            if pattern[j] == line[i]:
                i += 1
                j += 1

            if j == m:
                return True
            elif i < n and pattern[j] != line[i]:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1

        return False

    lines = text.split("\n")
    for line in lines:
        if kmp_search_line(pattern, line):
            return True

    return False


def aho_corasick_search(text: str, pattern: str) -> bool:
    """
    Aho-Corasick algorithm to find a full line match of a pattern in the text.

    Args:
        text (str): The content of the file.
        pattern (str): The search string.

    Returns:
        bool: True if the pattern is found as a full match on a stand-alone line, otherwise False.
    """  # noqa: E501
    aho = AhoCorasick()
    aho.add_pattern(pattern)
    aho.build_automaton()

    lines = text.split("\n")
    for line in lines:
        if len(line) == len(pattern):
            matches = aho.search(line)
            for _, match in matches:
                if match == pattern:
                    return True

    return False


class AhoCorasick:
    """
    Aho-Corasick algorithm for multiple pattern matching.

    Methods:
    -------
        __init__():
            Initializes Aho-Corasick automaton.

        add_pattern(pattern):
            Add a pattern to the  automaton.

        build_automaton():
            Builds the failure function and finalizes the automaton.

        search(text):
            Searches the text using the automaton.
    """

    def __init__(self):
        """
        Initializes the Aho-Corasick algorithm.
        """
        self.goto = {}
        self.output = {}
        self.fail = {}
        self.new_state = 0

    def add_pattern(self, pattern: str):
        """
        Add a pattern to the  automaton.

        Args:
            pattern (str): The pattern to add.
        """
        state = 0
        for char in pattern:
            if (state, char) not in self.goto:
                self.new_state += 1
                self.goto[(state, char)] = self.new_state
            state = self.goto[(state, char)]
        self.output[state] = pattern

    def build_automaton(self):
        """Builds the failure function and finalizes the automaton."""
        queue = deque()

        for char in {key[1] for key in self.goto if key[0] == 0}:
            state = self.goto[(0, char)]
            self.fail[state] = 0
            queue.append(state)

        while queue:
            r = queue.popleft()
            for key in {key[1] for key in self.goto if key[0] == r}:
                s = self.goto[(r, key)]
                queue.append(s)
                state = self.fail[r]
                while (state, key) not in self.goto and state != 0:
                    state = self.fail[state]
                if (state, key) in self.goto:
                    self.fail[s] = self.goto[(state, key)]
                else:
                    self.fail[s] = 0
                if self.fail[s] in self.output:
                    self.output[s] = self.output[self.fail[s]]

    def search(self, text: str):
        """
        Searches the text using the automaton.

        Args:
            text (str): The text to search through.

        Returns:
            list: returns a list of matched results.
        """
        state = 0
        results = []
        for index, char in enumerate(text):
            while (state, char) not in self.goto and state != 0:
                state = self.fail[state]
            if (state, char) in self.goto:
                state = self.goto[(state, char)]
                if state in self.output:
                    results.append(
                        (
                            index - len(self.output[state]) + 1,
                            self.output[state],
                        )
                    )
            else:
                state = 0
        return results
