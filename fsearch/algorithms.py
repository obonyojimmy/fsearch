"""This module provides the search algorithms functions for fsearch package."""
# fsearch/algorithms.py

from __future__ import annotations

import re
from collections import deque, defaultdict
from fsearch.utils import compute_lps

def native_search(text: str, pattern: str):
    """
    Searches for an exact match of the pattern in the text using naive search algorithm.

    Args:
        - text (str): The content of the file.
        - pattern (str): The search string.

    Returns:
        bool: True if the pattern is found as a full match in the text, otherwise False.
    """
    for line in text.split('\n'):
        if line == pattern:
            return True
    return False

def regex_search(text: str, pattern: str) -> bool:
    """
    Searches for an exact match of the pattern in the text using regular expressions,
    ensuring that the pattern matches an entire line.

    Parameters:
    text (str): The content of the file.
    pattern (str): The search string.

    Returns:
    bool: True if the pattern is found as a full match on a stand-alone line, otherwise False.
    """
    # Compile the regex pattern to match the whole line
    regex = re.compile(f"^{re.escape(pattern)}$", re.MULTILINE)
    
    # Search through the text
    matches = regex.search(text)
    
    return matches is not None

def rabin_karp_search(text: str, pattern: str):
    """
    Rabin-Karp algorithm to find a full line match of a pattern in the text.
    
    Args:
        - text (str): The content of the file.
        - pattern (str): The search string.

    Returns:
        bool: True if the pattern is found as a full match on a stand-alone line, otherwise False.
    """
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
        pattern_hash = (prime * pattern_hash + ord(pattern[i]))

    lines = text.split('\n')
    for line in lines:
        n = len(line)
        if n != m:
            continue
        
        # Initialize hash value for current line
        current_hash = 0
        for i in range(m):
            current_hash = (prime * current_hash + ord(line[i]))

        # Compare the hash values
        if pattern_hash == current_hash:
            # Check for exact match to avoid hash collision
            if line == pattern:
                return True

    return False

def kmp_search(text: str, pattern: str) -> bool:
    """
    KMP algorithm to find a full line match of a pattern in the text.

    Args:
        - text (str): The content of the file.
        - pattern (str): The search string.

    Returns:
        bool: True if the pattern is found as a full match on a stand-alone line, otherwise False.
    """
    def kmp_search_line(pattern, line):
        """
        KMP search for a pattern in a single line.

        :param pattern: The pattern string.
        :param line: The line of text.
        :return: True if the pattern matches the full line, otherwise False.
        """
        m = len(pattern)
        n = len(line)
        
        if m != n:
            return False
        
        lps = compute_lps(pattern)
        i = 0  # index for line
        j = 0  # index for pattern

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

    lines = text.split('\n')
    for line in lines:
        if kmp_search_line(pattern, line):
            return True

    return False

def aho_corasick_search(text: str, pattern: str) -> bool:
    """
    Aho-Corasick algorithm to find a full line match of a pattern in the text.

    Args:
        - text (str): The content of the file.
        - pattern (str): The search string.

    Returns:
        bool: True if the pattern is found as a full match on a stand-alone line, otherwise False.
    """
    aho = AhoCorasick()
    aho.add_pattern(pattern)
    aho.build_automaton()

    lines = text.split('\n')
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
            - pattern (str): The pattern to add.
        """
        state = 0
        for char in pattern:
            if (state, char) not in self.goto:
                self.new_state += 1
                self.goto[(state, char)] = self.new_state
            state = self.goto[(state, char)]
        self.output[state] = pattern

    def build_automaton(self):
        """ Builds the failure function and finalizes the automaton. """
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

        Parameters:
            - text (str): The text to search through.

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
                    results.append((index - len(self.output[state]) + 1, self.output[state]))
            else:
                state = 0
        return results
