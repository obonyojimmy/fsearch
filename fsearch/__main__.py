"""fsearch entry point script."""
# fsearch/__main__.py

import argparse
import os
import sys
from typing import Optional
from fsearch import __app_name__, __version__
from fsearch.server import Server
from fsearch.utils import benchmark_algorithms, logger, create_sample

class DefaultArgs(argparse.Namespace):
    subcommand: str
    version: Optional[bool]
    config: Optional[str]
    search: Optional[str]

class StartArgs(argparse.Namespace):
    config: str

class StopArgs(argparse.Namespace):
    subcommand: str

class BenchmarkArgs(argparse.Namespace):
    report_path: str
    sample: Optional[str]
    sample_dir: Optional[str]
    size: int

class SamplesArgs(argparse.Namespace):
    #file: str
    size: int

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
        #required=True,
        help="Sample to benchmark"
    )
    parser_benchmark.add_argument(
        "-d", "--sample_dir",
        type=str,
        #required=True,
        help="A directory that contains the Sample files to benchmark"
    )
    parser_benchmark.add_argument(
        "-n", "--size",
        type=int,
        default=1,
        help="Size of the number of patterns to sample with (default: 1)"
    )

    # Subcommand: stop
    subparsers.add_parser('stop', help='Stop the server')

    # Subcommand: test
    parser_samples = subparsers.add_parser('samples', help='Test data generator')

    #parser_samples.add_argument(
    #    "-f", "--file",
    #    type=str,
    #    required=True,
    #    help="The input file that will be used to generate sample out file"
    #)
    parser_samples.add_argument(
        "-s", "--size",
        type=int,
        default=1,
        help="Size of sample file out in mb"
    )


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
    

    args: DefaultArgs = parser.parse_args()

    if args.subcommand == 'start':
        start_args: StartArgs = args
        config_path = start_args.config
        if not os.path.isabs(config_path):
            config_path = os.path.abspath(config_path)
        logger.debug(f"Starting server with configuration file: {config_path}")
        server = Server(config_path)
        server.connect()
    elif args.subcommand == 'benchmark':
        benchmark_args: BenchmarkArgs = args
        report_path = benchmark_args.report_path
        if not benchmark_args.sample and not benchmark_args.sample_dir:
            logger.debug("Must provide a sample path or directory with -s or -d args")
        samples = []
        if benchmark_args.sample:
            samples = [benchmark_args.sample]
        if benchmark_args.sample_dir:
            samples = [os.path.join(benchmark_args.sample_dir, f) for f in os.listdir(benchmark_args.sample_dir) if os.path.isfile(os.path.join(benchmark_args.sample_dir, f))]
            
        size = benchmark_args.size
        logger.debug(f"Running benchmarks with samples: {samples}, report path: {report_path}")
        benchmark_algorithms(samples, report_path, size)
    elif args.subcommand == 'stop':
        stop_args: StopArgs = args
        logger.debug("Stopping the server")
        # todo: logic to stop the server
    elif args.subcommand == 'samples':
        samples_args: SamplesArgs = args
        logger.debug("Geneerating test sample file")
        create_sample(samples_args.size)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
