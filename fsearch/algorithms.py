"""This module provides the search algorithms functions for fsearch package."""
# fsearch/algorithms.py

import re
from collections import deque, defaultdict
from fsearch.utils import hash_words, compute_lps
from typing import List

def naive_search(text: str, pattern: str) -> bool:
	"""
	Perform a native string search on the provided content.
	
	Args:
	  - text (str): The text in which to search for the pattern.
	  - pattern (str): The substring to search for in the text.
	
	Returns:
	   bool: True if the pattern is found, False otherwise.
	"""
	index = text.find(pattern)
	return index != -1


def regex_search(text: str, pattern: str):
	"""
	Perform substring search using regex.
	
	This function checks whether the pattern exist in the text.
	It compiles a regex pattern from the substring and searches the text.

	Args:
	  - text (str): The text in which to search for the pattern.
	  - pattern (str): The substring to search for in the text.
	
	Returns:
	   bool: True if the pattern is found, False otherwise.
	"""
	# Split text and pattern into words and compile the pattern for whole word match
	words = ' '.join(text.split())
	regex_pattern = re.compile(r'\b' + re.escape(pattern) + r'\b')
	
	# Search for the pattern in the text
	return bool(regex_pattern.search(words))

def rabin_karp(text: str, pattern: str) -> bool:
	"""
	Perform substring search using the Rabin-Karp algorithm.
	
	This function checks whether the pattern appears as a whole word in the text.
	It uses a hashing mechanism to efficiently find the pattern in the text.

	Args:
	  - text (str): The text in which to search for the pattern.
	  - pattern (str): The substring to search for in the text.

	Returns:
	  bool: True if the pattern is found as a whole word in the text, False otherwise.
	"""
	
	text_words = text.split()
	pattern_words = pattern.split()
	
	if len(text_words) < len(pattern_words):
		return False
	
	pattern_hash = hash_words(pattern_words)
	
	for i in range(len(text_words) - len(pattern_words) + 1):
		window_hash = hash_words(text_words[i:i + len(pattern_words)])
		if window_hash == pattern_hash and text_words[i:i + len(pattern_words)] == pattern_words:
			return True
	
	return False

def kmp_search(text: str, pattern:str) -> bool:
	"""
	Perform substring search using the Knuth-Morris-Pratt (KMP) algorithm.
	
	This function checks whether the pattern appears as a whole word in the text.
	It uses the KMP algorithm to efficiently search for the pattern within the text.

	Parameters:
	text (str): The text in which to search for the pattern.
	pattern (str): The pattern to search for in the text.

	Returns:
	bool: True if the pattern is found as a whole word in the text, False otherwise.
	"""
	text_words = text.split()
	pattern_words = pattern.split()
	
	if len(text_words) < len(pattern_words):
		return False

	lps = compute_lps(pattern_words)
	i = j = 0
	while i < len(text_words):
		if pattern_words[j] == text_words[i]:
			i += 1
			j += 1
		if j == len(pattern_words):
			return True
		elif i < len(text_words) and pattern_words[j] != text_words[i]:
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
		__init__(patterns): 
			Initializes the trie and constructs the failure function.
	
		build_trie(patterns): 
			Builds the trie for the given patterns.
	
		build_failure(): 
			Constructs the failure function for the trie.
	
		search(text): 
			Searches for patterns in the given text and returns True if any pattern matches a whole word.
	"""
	def __init__(self, patterns: List[str]):
		"""
		Initializes the Aho-Corasick trie and constructs the failure function.

		Args:
			patterns (list of str): List of patterns to search for in the text.
		"""
		self.trie = defaultdict(dict)
		self.fail = defaultdict(int)
		self.output = defaultdict(list)
		self.build_trie(patterns)
		self.build_failure()

	def build_trie(self, patterns: List[str]):
		"""
		Builds the trie for the given patterns.

		Parameters:
			patterns (list of str): List of patterns to insert into the trie.
		"""
		for pattern in patterns:
			node = 0
			for symbol in pattern:
				node = self.trie[node].setdefault(symbol, len(self.trie))
			self.output[node].append(pattern)

	def build_failure(self):
		"""
		Constructs the failure function for the trie.
		
		The failure function is used to determine the next state when a mismatch occurs.
		"""
		queue = deque()
		for node in self.trie[0]:
			queue.append(self.trie[0][node])
			self.fail[self.trie[0][node]] = 0
		while queue:
			r = queue.popleft()
			for a in self.trie[r]:
				s = self.trie[r][a]
				queue.append(s)
				state = self.fail[r]
				while state and a not in self.trie[state]:
					state = self.fail[state]
				self.fail[s] = self.trie[state].get(a, 0)
				self.output[s].extend(self.output[self.fail[s]])

	def search(self, text: str):
		"""
		Searches for patterns in the given text.

		Parameters:
			text (str): The text in which to search for the patterns.

		Returns:
			bool: True if any pattern matches a whole word in the text, False otherwise.
		"""
		words = text.split()
		for word in words:
			node = 0
			for symbol in word:
				while node and symbol not in self.trie[node]:
					node = self.fail[node]
				node = self.trie[node].get(symbol, 0)
				if node in self.output:
					if word in self.output[node]:
						return True
		return False