"""fsearch entry point script."""
# fsearch/__main__.py

import os
import argparse
from typing import Optional
from fsearch import __app_name__, __version__
from fsearch.server import Server
from fsearch.utils import benchmark_algorithms

class StartArgs(argparse.Namespace):
    subcommand: str
    config: str

class StopArgs(argparse.Namespace):
    subcommand: str

class BenchmarkArgs(argparse.Namespace):
    subcommand: str
    report_path: str
    sample: str
    size: int

class DefaultArgs(argparse.Namespace):
    version: Optional[bool]
    config: Optional[str]
    search: Optional[str]


def main():
    parser = argparse.ArgumentParser(description="A highly performant and secure command-line server to search text files for strings.")
    subparsers = parser.add_subparsers(dest='subcommand', help='Subcommands')

    # Subcommand: start
    parser_start = subparsers.add_parser('start', help='Start the server')
    parser_start.add_argument(
        "-c", "--config",
        type=str,
        required=True,
        help="Path to the configuration file"
    )

    # Subcommand: benchmark
    parser_benchmark = subparsers.add_parser('benchmark', help='Run benchmarks')
    parser_benchmark.add_argument(
        "-r", "--report_path",
        type=str,
        required=True,
        help="Path to save the benchmark report"
    )
    parser_benchmark.add_argument(
        "-s", "--sample",
        type=str,
        required=True,
        help="Sample to benchmark"
    )
    parser_benchmark.add_argument(
        "--size",
        type=int,
        default=10,
        help="Size of the benchmark sample (default: 10)"
    )

    # Subcommand: stop
    subparsers.add_parser('stop', help='Stop the server')

    # Default (no subcommand)
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"{__app_name__} ({__version__})"
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        help="Path to the configuration file"
    )
    parser.add_argument(
        "search",
        type=str,
        nargs='?',
        help="String to search for"
    )

    args: StartArgs = parser.parse_args()

    if args.subcommand == 'start':
        config_path = args.config
        if not os.path.isabs(config_path):
            config_path = os.path.abspath(config_path)
        print(f"Starting server with configuration file: {config_path}")
        server = Server(config_path)
        server.connect()
    elif args.subcommand == 'benchmark':
        benchmark_args: BenchmarkArgs = args
        report_path = benchmark_args.report_path
        sample = benchmark_args.sample
        size = benchmark_args.size
        print(f"Running benchmarks with sample: {sample}, size: {size}, report path: {report_path}")
        benchmark_algorithms(report_path, sample, size)
    elif args.subcommand == 'stop':
        stop_args: StopArgs = args
        print("Stopping the server")
        # todo: logic to stop the server
    else:
        default_args: DefaultArgs = args
        if default_args.config:
            config_path = default_args.config
            if not os.path.isabs(config_path):
                config_path = os.path.abspath(config_path)
            print(f"Using configuration file: {config_path}")
            if default_args.search:
                search_string = default_args.search
                print(f"Searching for: {search_string}")
                # todo: logic to perform search with the provided configuration and search string
            else:
                print("Error: No search string provided.")
                parser.print_help()
                
        else:
            parser.print_help()

if __name__ == "__main__":
    main()
