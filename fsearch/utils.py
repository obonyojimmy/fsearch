"""This module provides the utility functions for fsearch package."""
# fsearch/utils.py

import base64
import configparser
import logging
import os
import random
import subprocess
import string
import timeit
from io import BytesIO
from typing import Tuple, Dict, List
from fsearch.config import Config

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s : [%(levelname)s] - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

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
    for section in config_parser.sections():
        for k, v in config_parser.items(section):
            if k not in defaults:
                defaults[k] = v
    
    config = Config(**defaults)

    # Check if the config option linuxpath, path is relative
    if not os.path.isabs(config.linuxpath):
        config.linuxpath = os.path.abspath(config.linuxpath)

    return config

def read_file(filepath: str, max_lines: int = 250000) -> str:
    """
    Reads the first (max_line) lines from a file and returns them as a single string.

    Args:
      - filepath (str): The path to the file to read.
      - max_lines (int): The max number of lines to read from the file.Default to 250000

    Returns:
      str: A str of the contents from the file, or None.

    Raises:
      FileNotFoundError: If the provided filepath does not exists.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")

    lines = []

    try:
        with open(filepath, 'r') as file:
            for i in range(max_lines):
                line = file.readline()
                if not line:
                    break
                lines.append(line)
    except Exception as e:
        return None
    
    return '\n'.join(lines)

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

def generate_certs(cert_dir: str = './.certs') -> Tuple[str, str]:
    """Generates self-signed certificates if missing using openssl or return existing certs in the certs directory.

    Args:
        cert_dir (str): Directory path to store the generated certs. Defaults to a ./.certs dir releative to cwd.

    Returns:
        tuple[str, str]: Absolute paths to generated certfile and keyfile.
    """
    certfile = os.path.join(cert_dir, "server.crt")
    keyfile = os.path.join(cert_dir, "server.key")

    # Return previous generated certs if exists
    if os.path.exists(certfile) and os.path.exists(keyfile):
        return certfile, keyfile 

    os.makedirs(cert_dir, exist_ok=True)

    # Generate the self-signed certificate using openssl bash cmd
    subprocess.check_call([
        "openssl", "req", "-x509", "-nodes", "-days", "365",
        "-newkey", "rsa:2048", "-keyout", keyfile, "-out", certfile,
        "-subj", "/C=US/ST=California/L=San Francisco/O=My Company/OU=Org/CN=mydomain.com"
    ])

    return certfile, keyfile

def generate_random_string(chars):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=chars))
    
def create_sample(size_mb: int, out_dir: str = 'samples'):
    # Calculate the target size in bytes
    target_size_bytes = size_mb * 1024 * 1024
    line_length = 10
    line_with_newline_length = line_length + 1  # Each line is 10 chars + 1 newline character
    num_lines = target_size_bytes // line_with_newline_length

    # Calculate the number of lines in thousands, rounded down to the nearest thousand
    k_lines =  round(num_lines / 1000)

    file_name = f"{k_lines}k.txt"
    file_path = os.path.join(out_dir, file_name)
    
    with open(file_path, 'w') as new_file:
        bytes_written = 0
        while bytes_written < target_size_bytes:
            random_string = generate_random_string(line_length)
            new_file.write(random_string + '\n')
            bytes_written += line_with_newline_length


def generate_samples(file_path: str, size: int = 10) -> List[str]:
    """
    Sample random lines from a file.

    Args:
        - file_path (str): Path to the file.
        - size (int): Number of lines to sample. Defaults to 10.

    Returns:
    list: A list of sampled lines.
    """
    lines = read_file(file_path).split("\n")
    total = len(lines)

    if size > total:
        size = total
    
    sampled_lines = random.sample(lines, size)
    return sampled_lines

def plot_benchmarks(results: Dict[str, Dict[str, float]]) -> BytesIO:
    """
    Plots a grouped bar chart for the benchmark results and returns the BytesIO object.

    Args:
        results (dict): A dictionary containing the algorithm names as keys and another dictionary as values,
                        where the keys are file line numbers and the values are execution times.

    Returns:
        BytesIO: The BytesIO object containing the plot image.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.error('please install matplotlib. Run `pip install fsearch[benchmark]` or `pip install matplotlib')
        raise ImportError
    
    algorithms = list(results.keys())
    file_sizes = list(results[algorithms[0]].keys())

    fig, ax = plt.subplots(figsize=(7, 6))
    width = 0.15
    x = range(len(file_sizes))

    for i, algorithm in enumerate(algorithms):
        times = [results[algorithm][file_size] for file_size in file_sizes]
        ax.bar([pos + i * width for pos in x], times, width, label=algorithm)

    ax.set_xlabel('File Size')
    ax.set_ylabel('Time (seconds)')
    ax.set_title('Benchmark of Search Algorithms')
    ax.set_xticks([pos + width * (len(algorithms) / 2) for pos in x])
    ax.set_xticklabels(file_sizes)
    ax.legend()

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    return buffer

def print_benchmarks(results: Dict[str, Dict[str, float]]) -> str:
    """
    Pretty prints the benchmark results as a table.

    Args:
        results (dict[str, dict[str, float]]): A dictionary with algorithm names as keys and dictionaries of file sizes and times as values.

    Returns:
    str: The table string representation of the results.
    """
    file_sizes = list(next(iter(results.values())).keys())
    headers = ["Algorithm"] + file_sizes + ["Average"]
    row_format = "{:<20}" + "{:<15}" * (len(headers) - 1)
    
    table_str = row_format.format(*headers) + "\n"
    table_str += "-" * 20 + "-" * 15 * (len(headers) - 1) + "\n"

    for algorithm, times in results.items():
        avg_time = sum(times.values()) / len(times)
        row = [algorithm] + [f"{times[file_size]:.6f}" for file_size in file_sizes] + [f"{avg_time:.6f}"]
        table_str += row_format.format(*row) + "\n"

    table_str += "-" * 20 + "-" * 15 * (len(headers) - 1) + "\n"
    print(table_str)
    return table_str

def benchmark_algorithms(file_paths: List[str], report_path: str, sample_size: int = 1):
    """
    Benchmarks the different search algorithms using the content of the specified files and patterns
    sampled from the files, then creates a PDF report with the plotted benchmark results using WeasyPrint.

    Args:
        file_paths (list): A list of paths to the search files.
        report_path (str): The path the benchmark PDF report will be saved to.
        sample_size (int): Number of lines to sample for generating patterns.

    Returns:
        None
    """
    try:
        # ensure the required extra dependencies are installed
        import matplotlib, weasyprint  # type: ignore
    except ImportError:
        logger.debug('Please install matplotlib and weasyprint dependencies. Run `pip install fsearch[benchmark]` or `pip install matplotlib weasyprint` to install them')
        return
    
    # internal package imports
    from fsearch.algorithms import native_search, regex_search, rabin_karp_search, kmp_search, aho_corasick_search
    from fsearch.templates import benchmark_template

    algorithms = {
        'Native Search': native_search,
        'Rabin-Karp Search': rabin_karp_search,
        'KMP Search': kmp_search,
        'Aho-Corasick Search': aho_corasick_search,
        'Regex Search': regex_search
    }
    
    results = {algorithm: {} for algorithm in algorithms.keys()}

    for file_path in file_paths:
        try:
            text = read_file(file_path)
            file_size_label = sum(1 for i in open(file_path, 'rb'))
            patterns = generate_samples(file_path, sample_size)
            for pattern in patterns:
                for name, algorithm in algorithms.items():
                    timer = timeit.Timer(lambda: algorithm(text, pattern))
                    time_taken = timer.timeit(number=1)  # Run the algorithm 1 time and get the time
                    if file_size_label not in results[name]:
                        results[name][file_size_label] = []
                    results[name][file_size_label].append(time_taken)
        
        except FileNotFoundError:
            logger.error(f"File at path {file_path} not found.")
        except Exception as e:
            logger.error(f"An error occurred with file {file_path}: {e}")

    avg_results = {algorithm: {file_size: (sum(times) / len(times)) if len(times) > 0 else 0 for file_size, times in result.items()} for algorithm, result in results.items()}
    sorted_results = dict(sorted(avg_results.items(), key=lambda item: (sum(item[1].values()) / len(item[1].values())) if len(item[1].values()) > 0 else float('inf')))

    # Pretty print the results
    table_str = print_benchmarks(sorted_results)

    # Plot the results
    plot_img = plot_benchmarks(sorted_results)
    img_str = base64.b64encode(plot_img.read()).decode('utf-8')
    
    report_template = benchmark_template.format(table_str=table_str, plot_img=img_str)
    weasyprint.HTML(string=report_template).write_pdf(report_path)
    logger.debug(f"Benchmark report saved to {report_path}")