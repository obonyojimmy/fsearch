import configparser
import os
import queue
import tempfile
import threading
import time
from dataclasses import asdict
from subprocess import call
from tracemalloc import start
from typing import Dict, Optional

from client import Client
from fsearch.config import Config
from fsearch.server import Server
from fsearch.utils import create_sample, generate_samples, logger


def send_query(client: Client, query, msg_queue: Optional[queue.Queue]):
    start_time = time.perf_counter()
    response = client.send_message(query)
    print("Response:", response)
    execution_time = time.perf_counter() - start_time
    if msg_queue:
        msg_queue.put(execution_time)
    return execution_time


def batch_queries(client, query, num_queries, q: queue.Queue):
    execution_times = []
    for _ in range(num_queries):
        send_query(client, query, q)
        tm = q.get()
        execution_times.append(tm)
    avg_time = sum(execution_times) / len(execution_times)
    millseconds = avg_time * 1000
    print(
        f"Average Execution Time for {num_queries} queries: {millseconds:.6f} milli-seconds"  # noqa: E501
    )
    return avg_time


def start_server(server: Server, stop_event: threading.Event):
    while not stop_event.isSet():
        server.connect()
    return


def write_config(config_path: str, configs: Dict[str, str]):
    """
    Writes the provided configuration dictionary to a file.

    Parameters:
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
    """
    # Extract headers from the dictionary keys
    headers = ["Queries"] + list(data.keys())

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


def performance(read_on_query: bool = False):
    host, port = "0.0.0.0", 8080
    benchmarks = {}
    for file_size in range(10000, 1000000 + 100000, 100000):
        label = f"{file_size}-kb"
        ## records collector
        benchmarks[label] = {}
        # create a sample database file
        mb_size = file_size / 1000
        linuxpath = create_sample(mb_size)

        # Create a temporary config file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            config_path = temp_file.name
        configs = {
            "host": host,
            "port": port,
            "linuxpath": linuxpath,
            "REREAD_ON_QUERY": read_on_query,
        }

        write_config(config_path, configs=configs)

        # run server in a separate thread
        stop_event = threading.Event()
        server = Server(config_path=config_path, port=port, max_conn=5)
        # server.configs.linuxpath = os.path.abspath(linuxpath)
        server_thread = threading.Thread(
            target=start_server, args=(server, stop_event)
        )
        server_thread.start()

        # run a timed client query in a separate thread
        # client = Client(host, port)

        # for reread_on_query in [False, True]:
        for no_requests in range(1, 10, 2):
            # server.configs.reread_on_query = reread_on_query

            # select a random query pattern from the sample
            queries = generate_samples(linuxpath, no_requests)
            queries = [n for n in queries if n]
            print(queries)
            records = set()
            execution_times = []
            msg_queue = queue.Queue()
            client = Client(host, port)
            for query in queries:
                client_thread = threading.Thread(
                    target=send_query, args=(client, query, msg_queue)
                )
                client_thread.start()
                client_thread.join()
                time_taken = msg_queue.get()
                time_ms = round(time_taken * 1000, 1)
                execution_times.append(time_ms)
                print("execution_time:", time_ms)

            print("client stoped: ")
            avg_time = sum(execution_times) / no_requests
            records.add(round(avg_time, 1))

            benchmarks[label][no_requests] = records

        # Stop the server
        server.stop()
        stop_event.set()
        print("Server stoped: ", linuxpath)

        ## cleanup the sample and tempconfig

        os.remove(linuxpath)
        os.remove(config_path)
        # break
    print(benchmarks)
    report_table = format_dict_to_table(benchmarks)
    # print(f"\n\nREREAD_ON_QUERY: ({read_on_query})\n", report_table)
    return report_table


def main():
    report_1 = performance(False)
    report_2 = performance(True)
    print(f"\n\nREREAD_ON_QUERY: ({False})\n", report_2)
    print(f"\n\nREREAD_ON_QUERY: ({True})\n", report_2)


if __name__ == "__main__":
    main()
