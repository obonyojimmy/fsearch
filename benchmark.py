import argparse
import configparser
import itertools
import os
import queue
import tempfile
import threading
import time
from typing import Dict

from client import Client
from fsearch.server import Server
from fsearch.utils import benchmark_algorithms, create_sample, generate_samples


def send_query(client: Client, query):
    """
    Sends a query to the server using the provided client and measures the request time.

    Args:
        client : Client
            An instance of the Client class used to send the query.
        query : str
            The query string to send to the server.

    Returns:
        float: The time taken to receive the response, in seconds.
    """  # noqa: E501

    start_time = time.perf_counter()
    client.send_message(query)
    # print("Response:", response)
    req_time = time.perf_counter() - start_time
    return req_time


def batch_queries(host, port, linuxpath, no_requests, msg_queue: queue.Queue):
    """
    Sends a batch of queries to the server and calculates the average execution time.

    Args:
        host : str
            The server host address.
        port : int
            The server port number.
        linuxpath : str
            The path to the sample file used to generate queries.
        no_requests : int
            The number of queries to send.
        msg_queue : queue.Queue
            A queue to store the average execution time of the requests.

    Returns:
        float: The average execution time of the batch, in milliseconds.
    """  # noqa: E501
    log_level = "DEBUG"
    client = Client(host, port, log_level=log_level)
    sample_queries = generate_samples(linuxpath, no_requests)
    sample_queries = [n for n in sample_queries if n]
    queries = itertools.cycle(sample_queries)
    execution_times = []
    ## ensure that it run the loop within 1 second
    # start_time = (
    #    time.perf_counter()
    # )
    for _ in range(no_requests):
        # if time.perf_counter() - start_time > 1:
        #    break
        query = next(queries)
        req_time = send_query(client, query)
        execution_times.append(req_time)
    request_count = len(execution_times)
    avg_time = sum(execution_times) / request_count
    avg_ms = round(avg_time * 1000, 2)
    msg_queue.put(avg_ms)
    print(
        f"Average Execution Time for {request_count} requests : {avg_ms} milli-seconds"  # noqa: E501
    )
    return avg_ms


def start_server(server: Server, stop_event: threading.Event):
    """
    Starts the server and keeps it running until the stop event is set.

    Args:
        server : Server
            An instance of the Server class.
        stop_event : threading.Event
            An event used to signal when to stop the server.

    Returns:
        None
    """
    while not stop_event.isSet():
        server.connect()
    return


def write_config(config_path: str, configs: Dict[str, str]):
    """
    Writes the provided configuration dictionary to a file.

    Args:
        config_path : str
            The file path where the configuration should be written.
        configs : Dict[str, str]
            A dictionary containing configuration key-value pairs to be written
            under the 'DEFAULT' section of the configuration file.

    Returns:
        None
    """
    config = configparser.ConfigParser()
    config["DEFAULT"] = configs
    with open(config_path, "w") as configfile:
        config.write(configfile)


def format_dict_to_table(data: dict) -> str:
    """
    Formats the nested dictionary into a table string with underscores under headers.

    Args:
        data (dict): The dictionary to format.

    Returns:
        str: The formatted table string.
    """  # noqa: E501
    # Extract headers from the dictionary keys
    headers = ["Requests"] + list(data.keys())

    # Initialize the rows list with the header
    rows = [headers]

    # Get the unique query numbers (like 10) from the nested dictionaries
    queries = sorted(
        {query for subdict in data.values() for query in subdict.keys()}
    )

    for query in queries:
        # Initialize a row with the current query number
        row = [str(query)]
        for key in data.keys():
            # Get the set of values for the current query number
            values_set = data[key].get(query)
            if values_set:
                # Format the values as comma-separated strings
                formatted_values = " | ".join(
                    f"{value:.1f}" for value in sorted(values_set)
                )
            else:
                formatted_values = ""
            row.append(formatted_values)
        # Add the formatted row to the rows list
        rows.append(row)

    # Calculate the maximum width of each column
    col_widths = [max(len(str(item)) for item in col) for col in zip(*rows)]

    # Build the formatted table string
    table = ""

    # Format the header row
    header_row = " | ".join(
        str(item).ljust(width) for item, width in zip(rows[0], col_widths)
    )
    table += f"{header_row}\n"

    # Add the underline row
    underline_row = " | ".join("-" * width for width in col_widths)
    table += f"{underline_row}\n"

    # Add the data rows
    for row in rows[1:]:
        formatted_row = " | ".join(
            str(item).ljust(width) for item, width in zip(row, col_widths)
        )
        table += f"{formatted_row}\n"

    return table


def performance(min_size: int, no_iterations: int) -> str:
    """
    Runs a performance benchmark by testing the server's response time with different file sizes
    and numbers of requests. The results are returned in a formatted table string.

    Args:
        min_size (int): The minimum sample size in kb. Defaults to 10000 ie 10mb
        no_iterations (int): The number of iterations to run the performance benchmark loop. Defaults to 2 loops.

    Returns:
        str: The performance benchmark report as a formatted table string.
    """  # noqa: E501
    host, port = "0.0.0.0", 8080
    benchmarks = {}
    # log_level = "DEBUG"
    log_level = "INFO"
    # for file_size in range(10000, 1000000 + 100000, 100000):
    for file_size in range(
        min_size, (min_size * no_iterations) + min_size, min_size
    ):
        label = f"{file_size}-kb"
        ## records collector
        benchmarks[label] = {}
        # create a sample database file
        mb_size = file_size / 1000
        linuxpath = create_sample(mb_size)

        # Create a temporary config file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            config_path = temp_file.name

        for no_requests in range(10, 100, 10):
            # select a random query pattern from the sample
            records = set()
            for reread_on_query in [False, True]:
                configs = {
                    "host": host,
                    "port": port,
                    "linuxpath": linuxpath,
                    "REREAD_ON_QUERY": reread_on_query,
                }

                write_config(config_path, configs=configs)
                # run server in a separate thread

                stop_event = threading.Event()
                server = Server(
                    config_path=config_path,
                    port=port,
                    max_conn=10,
                    log_level=log_level,
                )
                server_thread = threading.Thread(
                    target=start_server, args=(server, stop_event)
                )
                server_thread.start()
                ## give timeout for server to start
                time.sleep(5)

                ## run client batched requests in a separate thread
                msg_queue = queue.Queue()
                client_thread = threading.Thread(
                    target=batch_queries,
                    args=(host, port, linuxpath, no_requests, msg_queue),
                )
                client_thread.start()
                client_thread.join()
                avg_time = msg_queue.get()
                records.add(avg_time)

                # Stop the server
                server.stop()
                stop_event.set()
                print("Server stoped: ", linuxpath)
            benchmarks[label][no_requests] = records

        ## cleanup the sample and tempconfig

        os.remove(linuxpath)
        os.remove(config_path)
        # break
    print(benchmarks)
    report_table = format_dict_to_table(benchmarks)
    report_table = f"\n{report_table}"
    print(report_table)
    return report_table


class BenchmarkArgs(argparse.Namespace):
    """Namespace class to hold the arguments for the 'benchmark' subcommand.

    Attributes
    ----------
    report_path : str
        The path to save the benchmark report.
    min_size : Optional[int]
        The minimum sample size in kb. Defaults to 10000 ie 10mb (default: 1).
    iterations : Optional[int]
        The number of iterations to run the performance benchmark loop. Defaults to 2 loops.

    """  # noqa: E501

    report_path: str
    min_size: int = 10000
    iterations: int = 2


def main():
    """
    Main function that runs the performance benchmark and algorithm benchmarks.

    The performance benchmark measures the server's response time under different conditions,
    and the algorithm benchmarks compare the performance of different search algorithms.
    """  # noqa: E501
    parser = argparse.ArgumentParser(
        description="Measures server performance and algorithm comparison benchmarks"  # noqa: E501
    )

    parser.add_argument(
        "-r",
        "--report_path",
        type=str,
        required=True,
        help="Path to save the benchmark report",
    )
    parser.add_argument(
        "-s",
        "--min_size",
        type=int,
        default=10000,
        help="The minimum sample size in kb. Defaults to 10000 ie 10mb (default: 1).",  # noqa: E501
    )
    parser.add_argument(
        "-i",
        "--iterations",
        type=int,
        default=2,
        help="The number of iterations to run the performance benchmark loop. Defaults to 2 loops.",  # noqa: E501
    )

    args: BenchmarkArgs = parser.parse_args()  # type: ignore

    # run the speed test benchmark
    min_size, iterations = args.min_size, args.iterations
    speed_report = performance(min_size, iterations)

    ## run algorithms benchmarks
    samples = []
    report_path = args.report_path
    for file_size in range(1, 3, 1):
        sample_path = create_sample(file_size)
        samples.append(sample_path)
    benchmark_algorithms(samples, report_path, 1, speed_report)

    ## cleanup samples
    for filepath in samples:
        os.remove(filepath)


if __name__ == "__main__":
    main()
