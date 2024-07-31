"""This module provides the utility functions for fsearch package."""
# fsearch/utils.py

import base64
import configparser
import os
import random
import subprocess
import timeit
from dataclasses import asdict
from io import BytesIO
from typing import Tuple, Dict, List
from fsearch.config import Config

def read_config(config_path: str) -> Config:
    """ Reads server configurations from file to a `Config` object

    Args:
      - filepath (str): The path to the file to read.

    Returns:
      Config: The server configuration object.

    Raises:
      FileNotFoundError: If the provided filepath does not exists.
    """
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"The file '{config_path}' does not exist.")

    config_parser = configparser.ConfigParser()

    try:
        config_parser.read(config_path)
    except configparser.Error as e:
        raise Exception(f"Error reading the config file: {e}")

    defaults = dict(config_parser.defaults())
    sections = {section: dict(config_parser.items(section)) for section in config_parser.sections()}

    config = Config(**defaults, **sections)

    # Check if the config option linuxpath, path is relative
    if not os.path.isabs(config.linuxpath):
        config.linuxpath = os.path.abspath(config.linuxpath)

    print(f"Using configurations:", asdict(config))
    return config

def read_file(filepath: str) -> str:
    """
    Reads the contents of a file and returns a list of lines.

    Args:
      - filepath (str): The path to the file to read.

    Returns:
      str: A str of the contents from the file, or None.

    Raises:
      FileNotFoundError: If the provided filepath does not exists.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")

    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        return None

def compute_lps(pattern: str) -> List[int]:
    """
    Compute the longest prefix suffix (LPS) array for the pattern.
    
    The LPS array is used to skip characters while matching.

    Parameters:
      pattern (list): List of words representing the pattern.

    Returns:
      list: LPS array for the pattern.
    """
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

    return lps

def generate_self_signed_cert() -> Tuple[str, str]:
    """Generates self-signed certificates using openssl and stores them in a temporary directory."""
    module_dir = os.path.dirname(os.path.abspath(__file__))
    cert_dir = os.path.join(module_dir, '.certs')

    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)

    certfile = os.path.join(cert_dir, "server.crt")
    keyfile = os.path.join(cert_dir, "server.key")

    # Return previous generated certs if exists
    if os.path.exists(certfile) and os.path.exists(keyfile):
        return certfile, keyfile 

    # Generate the self-signed certificate using openssl
    subprocess.check_call([
        "openssl", "req", "-x509", "-nodes", "-days", "365",
        "-newkey", "rsa:2048", "-keyout", keyfile, "-out", certfile,
        "-subj", "/C=US/ST=California/L=San Francisco/O=My Company/OU=Org/CN=mydomain.com"
    ])

    return certfile, keyfile

def generate_samples(file_path: str, size: int) -> List[str]:
    """
    Sample random lines from a file.

    Args:
        - file_path (str): Path to the file.
        - size (int): Number of lines to sample.

    Returns:
    list: A list of sampled lines.
    """
    lines = read_file(file_path).split("\n")
    total = len(lines)

    if size > total:
        size = total
    
    sampled_lines = random.sample(lines, size)
    return sampled_lines

def plot_benchmarks(results: Dict[str, float]) -> BytesIO:
    """
    Plots a bar chart for the benchmark results and returns the BytesIO object.

    Args:
        results (dict): A dictionary containing the algorithm names as keys and the average execution time as values.

    Returns:
        BytesIO: The BytesIO object containing the plot image.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print('please install matplotlib. Run `pip install fsearch[benchmark]` or `pip install matplotlib')
        raise ImportError
    
    names = list(results.keys())
    times = list(results.values())
    
    plt.figure(figsize=(6, 6))
    plt.bar(names, times, color='skyblue')
    plt.xlabel('Search Algorithms')
    plt.ylabel('Time (seconds)')
    plt.title('Benchmark of Search Algorithms')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    return buffer

def print_benchmarks(results: Dict[str, float]):
    """
    Pretty prints the benchmark results as a table.

    Arags:
        results (dict[str, float]): A dictionary with algorithm names as keys and their respective times as values.
    """
    headers = ["Algorithm", "Time (seconds)"]
    row_format = "{:<20} {:<15}"
    print(row_format.format(*headers))
    print("-" * 35)
    for algorithm, time_taken in results.items():
        print(row_format.format(algorithm, f"{time_taken:.6f}"))
    print("-" * 35, "\n\n")

def benchmark_algorithms(file_path: str, report_path: str, sample_size: int = 10):
    """
    Benchmarks the different search algorithms using the content of the specified file and patterns
    sampled from the file, then creates a PDF report with the plotted benchmark results using WeasyPrint.

    Args:
        file_path (str): The path to the search file.
        report_path (str): The path the benchmark PDF report will be saved to.
        sample_size (int): Number of lines to sample for generating patterns.

    Returns:
        None
    """
    try:
        # ensure the required extra dependencies are installed
        import matplotlib, weasyprint  # type: ignore
    except ImportError:
        print('Please install matplotlib and weasyprint dependencies. Run `pip install fsearch[benchmark]` or `pip install matplotlib weasyprint` to install them')
        return
    
    # internal package imports
    from fsearch.algorithms import native_search, regex_search, rabin_karp_search, kmp_search, aho_corasick_search
    from fsearch.reports import benchmark_template


    try:
        patterns = generate_samples(file_path, sample_size)
        text = read_file(file_path)
        
        algorithms = {
            'Native Search': native_search,
            'Rabin-Karp Search': rabin_karp_search,
            'KMP Search': kmp_search,
            'Aho-Corasick Search': aho_corasick_search,
            'Regex Search': regex_search
        }
        
        results = {}
        for pattern in patterns:
            for name, algorithm in algorithms.items():
                timer = timeit.Timer(lambda: algorithm(text, pattern.strip()))
                time_taken = timer.timeit(number=10)  # Run the algorithm 10 times and get the average time
                if name not in results:
                    results[name] = []
                results[name].append(time_taken)
        
        # Average the results for each algorithm
        avg_results = {name: sum(times) / len(times) for name, times in results.items()}
        sorted_results = dict(sorted(avg_results.items(), key=lambda item: item[1]))
        
        # Pretty print the results
        print_benchmarks(sorted_results)

        # Plot the results
        plot_img = plot_benchmarks(sorted_results)
        img_str = base64.b64encode(plot_img.read()).decode('utf-8')
        
        # Create a pdf report of the results
        report_template = benchmark_template.format(plot_img=img_str)
        weasyprint.HTML(string=report_template).write_pdf(report_path)
        print(f"Benchmark report saved to {report_path}")
    
    except FileNotFoundError:
        print(f"File at path {file_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")