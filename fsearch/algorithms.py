"""This module provides the search algorithms functions for fsearch package."""
# fsearch/algorithms.py
from __future__ import annotations

import re
from collections import deque, defaultdict
from fsearch.utils import hash_words, compute_lps
from typing import List

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

def rabin_karp(text: str, pattern: str) -> bool:
    """
    Searches for an exact match of the pattern in the text using Rabin-Karp algorithm.

    Parameters:
        - text (str): The content of the file.
        - pattern (str): The search string.

    Returns:
        bool: True if the pattern is found as a full match in the text, otherwise False.
    """
    d = 256  # number of characters in the input alphabet
    q = 101  # a prime number
    n = len(text)
    m = len(pattern)
    p = 0    # hash value for pattern
    t = 0    # hash value for text
    h = 1

    for i in range(m-1):
        h = (h * d) % q

    for i in range(m):
        p = (d * p + ord(pattern[i])) % q
        t = (d * t + ord(text[i])) % q

    for i in range(n - m + 1):
        if p == t:
            match = True
            for j in range(m):
                if text[i + j] != pattern[j]:
                    match = False
                    break
            if match:
                return True

        if i < n - m:
            t = (d * (t - ord(text[i]) * h) + ord(text[i + m])) % q
            if t < 0:
                t = t + q

    return False

def kmp_search(text, pattern) -> bool:
    """
    Searches for an exact match of the pattern in the text using KMP (Knuth-Morris-Pratt) algorithm.

    Parameters:
    text (str): The content of the file.
    pattern (str): The search string.

    Returns:
    bool: True if the pattern is found as a full match in the text, otherwise False.
    """
    n = len(text)
    m = len(pattern)
    lps = compute_lps(pattern)
    i = 0  # index for text
    j = 0  # index for pattern

    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == m:
            return True
            j = lps[j - 1]

        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    return False
class AhoCorasick:
    """
    Aho-Corasick algorithm for multiple pattern matching.
    
    This class constructs a trie for the given patterns and uses it to search
    for occurrences of these patterns in a given text, ensuring whole word matching.

    Methods:
    -------
        __init__(): 
            Initializes Aho-Corasick algorithm class.
    
        __call__(text, pattern): 
            Initializes Aho-Corasick class and calls search.
    
        build_trie(patterns): 
            Builds the trie for the given patterns.
    
        build_failure(): 
            Constructs the failure function for the trie.
    
        search(text): 
            Searches for patterns in the given text and returns True if any pattern matches a whole word.
    """
    def __init__(self):
        """
        Initializes the Aho-Corasick algorithm.

        Args:
            patterns (list of str): List of patterns to search for in the text.
        """
        self.root = {}
        self.end_of_pattern = {}  # To mark end of patterns
        self.fail_link = {}       # Failure links for nodes
        self.output_link = {}     # Output links for nodes

    def __call__(cls: AhoCorasick, text: str, pattern: str) -> bool:
        """
        Initializes and searches for an exact match of the pattern in the text using Aho-Corasick algorithm.

        Args:
            - text (str): The content of the file.
            - pattern (str): The search string.

        Returns:
            - bool: True if the pattern is found as a full match on a stand-alone line, otherwise False.
        """
        self: AhoCorasick = cls()
        self.add_pattern(pattern)
        self.build_failure()
        return self.search(text)
        
    def add_pattern(self, pattern: List[str]):
        """
        Add a pattern to the Aho-Corasick automaton.

        Args:
            - pattern (str): The pattern to add.
        """
        node = self.root
        for char in pattern:
            if char not in node:
                node[char] = {}
            node = node[char]
        # Use id() to uniquely identify the node where the pattern ends
        self.end_of_pattern[id(node)] = pattern

    def build_failure(self):
        """
        Build failure links for the Aho-Corasick automaton.
        """
        queue = deque()
        # Initialize the queue with the root's children
        for char, child in self.root.items():
            self.fail_link[id(child)] = self.root
            queue.append(child)

        while queue:
            current_node = queue.popleft()
            current_node_id = id(current_node)

            for char, child in current_node.items():
                if char == 'fail':
                    continue  # Skip the 'fail' key added for queue initialization

                queue.append(child)
                fail_node = self.fail_link[current_node_id]

                while fail_node is not None and char not in fail_node:
                    fail_node = self.fail_link.get(id(fail_node))
                self.fail_link[id(child)] = fail_node[char] if fail_node else self.root
                
                if id(self.fail_link[id(child)]) in self.end_of_pattern:
                    self.output_link[id(child)] = self.fail_link[id(child)]
                else:
                    self.output_link[id(child)] = self.output_link.get(id(self.fail_link[id(child)]), None)

    def search(self, text: str) -> bool:
        """
        Search for patterns in the text, ensuring the pattern matches an entire line.

        Parameters:
            - text (str): The text to search through.

        Returns:
            bool: True if the pattern is found as a full match on a stand-alone line, otherwise False.
        """
        lines = text.splitlines()
        for line in lines:
            node = self.root
            i = 0
            while i < len(line):
                char = line[i]
                while node is not None and char not in node:
                    node = self.fail_link.get(id(node))
                if node is None:
                    node = self.root
                    i += 1
                    continue

                node = node[char]
                temp_node = node
                while temp_node is not None:
                    if id(temp_node) in self.end_of_pattern:
                        pattern_length = len(self.end_of_pattern[id(temp_node)])
                        if i - pattern_length + 1 == 0 and len(line) == pattern_length:
                            return True
                    temp_node = self.output_link.get(id(temp_node), None)
                i += 1

        return False


