"""
fsearch/utils.py

This module provides utility functions for the fsearch package, such as configuration handling, file operations,
random data generation, benchmarking, and certificate generation.

Functions:
    - read_config: Reads server configurations from a file into a `Config` object.
    - read_file: Reads a specified number of lines from a file.
    - compute_lps: Computes the Longest Prefix Suffix (LPS) array for the KMP search algorithm.
    - generate_certs: Generates or retrieves self-signed SSL certificates.
    - generate_random_string: Generates a random string of specified length.
    - create_sample: Creates a sample text file of a specified size in megabytes.
    - generate_samples: Samples random lines from a file.
    - plot_benchmarks: Plots benchmark results for different search algorithms.
    - print_benchmarks: Pretty prints benchmark results as a formatted table.
    - benchmark_algorithms: Benchmarks various search algorithms and generates a report.
"""  # noqa: E501

import base64
import configparser
import logging
import os
import random
import string
import subprocess
import timeit
from io import BytesIO
from typing import Dict, List, Optional, Tuple

from fsearch.config import Config

logger = logging.getLogger(__name__)


def read_config(config_path: str) -> Config:
    """Reads server configurations from a file into a `Config` object.

    Args:
        config_path (str): The path to the configuration file.

    Returns:
        Config: The server configuration object.

    Raises:
        FileNotFoundError: If the provided filepath does not exist.
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
    Reads the first `max_lines` lines from a file and returns them as a single string.

    Args:
        filepath (str): The path to the file to read.
        max_lines (int): The maximum number of lines to read from the file. Defaults to 250,000.

    Returns:
        str: A string of the file contents.

    Raises:
        FileNotFoundError: If the provided filepath does not exist.
    """  # noqa: E501
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")

    lines = []
    try:
        with open(filepath, "r") as file:
            lines = file.readlines(max_lines)
    except Exception:
        return ""

    return "".join(lines)


def compute_lps(pattern: str) -> List[int]:
    """
    Compute the longest prefix suffix (LPS) array for the KMP algorithm.

    Args:
        pattern (str): The pattern string for which to compute the LPS array.

    Returns:
        list[int]: The LPS array where each index `i` contains the length of the longest
        prefix which is also a suffix for the substring pattern[0:i+1].
    """  # noqa: E501
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


def generate_certs(cert_dir: str = "./.certs") -> Tuple[str, str]:
    """Generates self-signed certificates if missing or returns existing certificates in the certs directory.

    Args:
        cert_dir (str): Directory path to store the generated certificates. Defaults to `./.certs`.

    Returns:
        Tuple[str, str]: Absolute paths to the generated certificate file and key file.
    """  # noqa: E501
    certfile = os.path.join(cert_dir, "server.crt")
    keyfile = os.path.join(cert_dir, "server.key")

    # Return previous generated certs if exists
    if os.path.exists(certfile) and os.path.exists(keyfile):
        return certfile, keyfile

    os.makedirs(cert_dir, exist_ok=True)

    # Generate the self-signed certificate using openssl bash cmd
    subprocess.check_call(
        [
            "openssl",
            "req",
            "-x509",
            "-nodes",
            "-days",
            "365",
            "-newkey",
            "rsa:2048",
            "-keyout",
            keyfile,
            "-out",
            certfile,
            "-subj",
            "/C=US/ST=California/L=San Francisco/O=My Company/OU=Org/CN=mydomain.com",  # noqa: E501
        ]
    )

    return certfile, keyfile


def generate_random_string(chars: int) -> str:
    """Generates a random string of the specified length.

    Args:
        chars (int): The length of the string to generate.

    Returns:
        str: The generated random string.
    """
    return "".join(
        random.choices(string.ascii_letters + string.digits, k=chars)
    )


def create_sample(size_mb: float, out_dir: str = "samples") -> str:
    """
    Create a sample text file of a specified size in megabytes.

    Args:
        size_mb (int): The size of the file to create in megabytes.
        out_dir (str, optional): The directory to save the file in. Defaults to "samples".

    Returns:
        str: The path to the created file.
    """  # noqa: E501
    # Calculate the target size in bytes
    target_size_bytes = size_mb * 1024 * 1024
    line_length = 10

    # Each line is 10 characters + 1 newline character
    line_with_newline_length = line_length + 1
    num_lines = target_size_bytes // line_with_newline_length

    # Calculate the number of lines in thousands, rounded down to the nearest thousand  # noqa: E501
    k_lines = round(num_lines / 1000)

    file_name = f"{k_lines}k.txt"
    file_path = os.path.join(out_dir, file_name)

    os.makedirs(out_dir, exist_ok=True)

    with open(file_path, "w") as new_file:
        bytes_written = 0
        while bytes_written < target_size_bytes:
            random_string = generate_random_string(line_length)
            new_file.write(random_string + "\n")
            bytes_written += line_with_newline_length

    return file_path


def generate_samples(file_path: str, size: int = 10) -> List[str]:
    """
    Samples random lines from a file.

    Args:
        file_path (str): Path to the file.
        size (int): Number of lines to sample. Defaults to 10.

    Returns:
        List[str]: A list of sampled lines.
    """
    lines = read_file(file_path).splitlines()
    total = len(lines)

    if size > total:
        size = total

    return random.sample(lines, k=size)
    # sampled_lines = [n for n in random.sample(lines, k=size) if n]


def plot_benchmarks(results: Dict[str, Dict[str, float]]) -> BytesIO:
    """
    Plots a grouped bar chart for the benchmark results and returns a BytesIO object containing the plot image.

    Args:
        results (Dict[str, Dict[str, float]]): A dictionary containing the algorithm names as keys and another dictionary as values,
                                               where the keys are file line numbers and the values are execution times.

    Returns:
        BytesIO: The BytesIO object containing the plot image.
    """  # noqa: E501
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.error(
            "please install matplotlib. Run `pip install fsearch[benchmark]` or `pip install matplotlib"  # noqa: E501
        )
        raise ImportError

    algorithms = list(results.keys())
    file_sizes = list(results[algorithms[0]].keys())

    fig, ax = plt.subplots(figsize=(7, 6))
    width = 0.15
    x = range(len(file_sizes))

    for i, algorithm in enumerate(algorithms):
        times = [results[algorithm][file_size] for file_size in file_sizes]
        ax.bar([pos + i * width for pos in x], times, width, label=algorithm)

    ax.set_xlabel("File Size")
    ax.set_ylabel("Time (seconds)")
    ax.set_title("Benchmark of Search Algorithms")
    ax.set_xticks([pos + width * (len(algorithms) / 2) for pos in x])
    ax.set_xticklabels(file_sizes)
    ax.legend()

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    return buffer


def print_benchmarks(results: Dict[str, Dict[str, float]]) -> str:
    """
    Pretty prints the benchmark results as a table.

    Args:
        results (Dict[str, Dict[str, float]]): A dictionary containing algorithm names as
            keys and dictionaries of file sizes and times as values.

    Returns:
        str: The string representation of the table of results.
    """  # noqa: E501
    file_sizes = list(next(iter(results.values())).keys())
    headers = ["Algorithm"] + file_sizes + ["Average"]
    row_format = "{:<20}" + "{:<15}" * (len(headers) - 1)

    table_str = row_format.format(*headers) + "\n"
    table_str += "-" * 20 + "-" * 15 * (len(headers) - 1) + "\n"

    for algorithm, times in results.items():
        avg_time = sum(times.values()) / len(times)
        row = (
            [algorithm]
            + [f"{times[file_size]:.6f}" for file_size in file_sizes]
            + [f"{avg_time:.6f} (ms)"]
        )
        table_str += row_format.format(*row) + "\n"

    table_str += "-" * 20 + "-" * 15 * (len(headers) - 1) + "\n"
    print(table_str)
    return table_str


def benchmark_algorithms(
    file_paths: List[str],
    report_path: str,
    sample_size: int = 1,
    speed_report: Optional[str] = None,
):
    """
    Benchmarks the different search algorithms using the content of the specified files and patterns
    sampled from the files, then creates a PDF report with the plotted benchmark results using WeasyPrint.

    Args:
        file_paths (list): A list of paths to the search files.
        report_path (str): The path the benchmark PDF report will be saved to.
        sample_size (int, optional): Number of lines to sample for generating patterns.
        speed_report (str, optional): Optional speed-test report generated from `perf.py` to add to the benchmark pdf report

    Returns:
        None
    """  # noqa: E501
    try:
        # ensure the required extra dependencies are installed
        import weasyprint
    except ImportError:
        logger.debug(
            "Please install matplotlib and weasyprint dependencies. \
            Run `pip install fsearch[benchmark]` \
            or `pip install matplotlib weasyprint` to install them"
        )
        return

    # internal package imports
    from fsearch.algorithms import (
        aho_corasick_search,
        binary_search,
        kmp_search,
        native_search,
        rabin_karp_search,
        regex_search,
    )
    from fsearch.templates import benchmark_template

    algorithms = {
        "Native Search": native_search,
        "Rabin-Karp Search": rabin_karp_search,
        "KMP Search": kmp_search,
        "Aho-Corasick Search": aho_corasick_search,
        "Regex Search": regex_search,
        "Binary Search": binary_search,
    }

    results = {algorithm: {} for algorithm in algorithms.keys()}

    for file_path in file_paths:
        try:
            text = read_file(file_path)
            file_size_label = sum(1 for i in open(file_path, "rb"))
            patterns = generate_samples(file_path, sample_size)
            for pattern in patterns:
                for name, algorithm in algorithms.items():
                    timer = timeit.Timer(lambda: algorithm(text, pattern))
                    time_taken = timer.timeit(
                        number=1
                    )  # Run the algorithm 1 time and get the time
                    time_taken = time_taken * 1000
                    if file_size_label not in results[name]:
                        results[name][file_size_label] = []
                    results[name][file_size_label].append(time_taken)

        except FileNotFoundError:
            logger.error(f"File at path {file_path} not found.")
        except Exception as e:
            logger.error(f"An error occurred with file {file_path}: {e}")

    avg_results = {
        algorithm: {
            file_size: (sum(times) / len(times)) if len(times) > 0 else 0
            for file_size, times in result.items()
        }
        for algorithm, result in results.items()
    }
    sorted_results = dict(
        sorted(
            avg_results.items(),
            key=lambda item: (sum(item[1].values()) / len(item[1].values()))
            if len(item[1].values()) > 0
            else float("inf"),
        )
    )

    # Pretty print the results
    table_str = print_benchmarks(sorted_results)

    # Plot the results
    plot_img = plot_benchmarks(sorted_results)
    img_str = base64.b64encode(plot_img.read()).decode("utf-8")

    report_template = benchmark_template.format(
        table_str=table_str, plot_img=img_str, speed_report=speed_report
    )

    logger.setLevel(logging.ERROR)

    ## reset fonttools and weasyprint verbose logs
    logging.getLogger("fontTools").setLevel(logging.ERROR)
    logging.getLogger("weasyprint").setLevel(logging.ERROR)
    weasyprint.HTML(string=report_template).write_pdf(report_path)
    logger.setLevel(logging.DEBUG)
    logger.debug(f"Benchmark report saved to {report_path}")
