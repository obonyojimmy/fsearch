"""
fsearch/__main__.py

The fsearch package main script.

This script serves as the main entry point for the fsearch command-line tool.
It provides various subcommands to start the server, run benchmarks,
generate samples, create SSL certificates, and stop the server.

For usage and options:
```bash
$ python fsearch/__main__.py -h
"""

import argparse
import logging
import os
from typing import Optional, Type

from fsearch import __app_name__, __version__
from fsearch.server import Server
from fsearch.utils import benchmark_algorithms, create_sample, generate_certs

logger = logging.getLogger(__name__)


class DefaultArgs(argparse.Namespace, Type):
    """Attributes
    ----------
    subcommand : str
        The subcommand to execute.
    version : Optional[bool]
        The version flag.
    config : Optional[str]
        The path to the configuration file.
    """

    subcommand: str
    version: Optional[bool]
    config: Optional[str]


class StartArgs(argparse.Namespace):
    """Namespace class to hold the arguments for the 'start' subcommand.

    Attributes
    ----------
    config : str
        The path to the configuration file.
    """

    config: str


class StopArgs(argparse.Namespace):
    """Namespace class to hold the arguments for the 'stop' subcommand.

    Attributes
    ----------
    subcommand : str
        The subcommand to execute.
    """

    subcommand: str


class BenchmarkArgs(argparse.Namespace):
    """Namespace class to hold the arguments for the 'benchmark' subcommand.

    Attributes
    ----------
    report_path : str
        The path to save the benchmark report.
    sample : Optional[str]
        The sample to benchmark.
    sample_dir : Optional[str]
        The directory that contains the sample files to benchmark.
    size : int
        The size of the number of patterns to sample with (default: 1).
    """

    report_path: str
    sample: Optional[str]
    sample_dir: Optional[str]
    size: int


class SamplesArgs(argparse.Namespace):
    """Namespace class to hold the arguments for the 'samples' subcommand.

    Attributes
    ----------
    size : int
        The size of the sample file output in MB.
    """

    size: int


class CertArgs(argparse.Namespace):
    """Namespace class to hold the arguments for the 'certs' subcommand.

    Attributes
    ----------
    dir : str
        The output directory for the created certificates, defaults to the current directory.
    """  # noqa: E501

    dir: str


def main():
    """Main function to parse arguments and execute the appropriate subcommand."""  # noqa: E501
    parser = argparse.ArgumentParser(
        description="A highly performant and secure command-line server to search text files for strings."  # noqa: E501
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommands")

    # Subcommand: start
    parser_start = subparsers.add_parser("start", help="Start the server")
    parser_start.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to the configuration file",
    )

    # Subcommand: benchmark
    parser_benchmark = subparsers.add_parser(
        "benchmark", help="Run benchmarks"
    )
    parser_benchmark.add_argument(
        "-r",
        "--report_path",
        type=str,
        required=True,
        help="Path to save the benchmark report",
    )
    parser_benchmark.add_argument(
        "-s", "--sample", type=str, help="Sample to benchmark"
    )
    parser_benchmark.add_argument(
        "-d",
        "--sample_dir",
        type=str,
        help="A directory that contains the sample files to benchmark",
    )
    parser_benchmark.add_argument(
        "-n",
        "--size",
        type=int,
        default=1,
        help="Size of the number of patterns to sample with (default: 1)",
    )

    # Subcommand: stop
    subparsers.add_parser("stop", help="Stop the server")

    # Subcommand: samples
    parser_samples = subparsers.add_parser(
        "samples", help="Samples data generator"
    )
    parser_samples.add_argument(
        "-s",
        "--size",
        type=int,
        default=1,
        help="Size of the sample file output in MB",
    )

    # Subcommand: certs
    parser_certs = subparsers.add_parser(
        "certs", help="Utility to create SSL certificates"
    )
    parser_certs.add_argument(
        "-d",
        "--dir",
        type=str,
        default=".",
        help="Output directory for the created certificates, defaults to the current directory",  # noqa: E501
    )

    # Default (no subcommand)
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{__app_name__} ({__version__})",
    )
    parser.add_argument(
        "-c", "--config", type=str, help="Path to the configuration file"
    )

    args: DefaultArgs = parser.parse_args()  # type: ignore

    if args.subcommand == "start":
        start_args: StartArgs = args  # type: ignore
        config_path = start_args.config
        if not os.path.isabs(config_path):
            config_path = os.path.abspath(config_path)
        logger.debug(f"Starting server with configuration file: {config_path}")
        server = Server(config_path)
        server.connect()
    elif args.subcommand == "benchmark":
        benchmark_args: BenchmarkArgs = args  # type: ignore
        report_path = benchmark_args.report_path
        if not benchmark_args.sample and not benchmark_args.sample_dir:
            logger.debug(
                "Provide a sample path or directory with -s or -d args"
            )
        samples = []
        if benchmark_args.sample:
            samples = [benchmark_args.sample]
        if benchmark_args.sample_dir:
            samples = [
                os.path.join(benchmark_args.sample_dir, f)
                for f in os.listdir(benchmark_args.sample_dir)
                if os.path.isfile(os.path.join(benchmark_args.sample_dir, f))
            ]

        size = benchmark_args.size
        logger.debug(
            f"Running benchmarks with samples: {samples}, report path: {report_path}"  # noqa: E501
        )
        benchmark_algorithms(samples, report_path, size)
    elif args.subcommand == "stop":
        stop_args: StopArgs = args  # type: ignore
        logger.debug("Stopping the server")
        # TODO: Add logic to stop the server
    elif args.subcommand == "samples":
        samples_args: SamplesArgs = args  # type: ignore
        logger.debug("Generating test sample file")
        create_sample(samples_args.size)
    elif args.subcommand == "certs":
        cert_args: CertArgs = args  # type: ignore
        logger.debug("Generating SSL certificates")
        generate_certs(cert_args.dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
