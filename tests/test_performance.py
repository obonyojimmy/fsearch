import os
import time
import socket
import threading
import pytest
import multiprocessing
from fsearch.server import Server
from fsearch.utils import read_config

from subprocess import call

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_query(self, query):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(query.encode())
            response = s.recv(1024)
        return response.decode()

def execution_timer(client, query, file_size):
    start_time = time.time()
    response = client.send_query(query)
    end_time = time.time()
    execution_time = end_time - start_time
    #print(f"File Size: {file_size} lines, Query: {query}, Response: {response}, Execution Time: {execution_time:.6f} seconds")
    return execution_time

def send_queries(client, query, num_queries):
    execution_times = []
    for _ in range(num_queries):
        execution_times.append(execution_timer(client, query, 'N/A'))
    avg_time = sum(execution_times) / len(execution_times)
    avg_time = avg_time * 1000
    print(f"Average Execution Time for {num_queries} queries: {avg_time:.6f} milli-seconds")
    return avg_time

def write_config(config_path, config):
    with open(config_path, 'w') as config_file:
        for key, value in config.items():
            config_file.write(f'{key} = {value}\n')

def update_config(file_path):
    config = read_config('config.ini')
    #config['linuxpath'] = file_path
    #write_config('config.ini', config)



#@pytest.fixture(scope="module")
def start_server(server:Server, stop_event: threading.Event):
    while not stop_event.isSet():
        server.connect()
    return

#@pytest.mark.performance
def performance():
    host, port = '0.0.0.0', 8080
    query = '11;0;23;11;0;19;5;0;'
    file_sizes = [
        ('file_10000.txt', 10000),
        ('file_100000.txt', 100000),
        #('file_500000.txt', 500000),
        #('file_1000000.txt', 1000000)
    ]

    
    # Test execution times for different file sizes
    for file_path, file_size in file_sizes:
        # Update server config and restart server
        #update_config(file_path)
        #start_server.stop()
        stop_event = threading.Event()
        config_path = 'config.ini'  # path to your config file
        server = Server(config_path=config_path, port=port)
        server_thread = threading.Thread(target=start_server, args=(server, stop_event))
        server_thread.start()
        time.sleep(5)  # Wait for the server to restart
        
        client = Client(host, port)
        num_queries_list = [10, 50] #[10, 50, 100, 200]
        for num_queries in num_queries_list:
            thread = threading.Thread(target=send_queries, args=(client, query, num_queries))
            thread.start()
            thread.join()
        
        # Stop the server
        server.stop()
        stop_event.set()
        time.sleep(5)
        print('Server stoped: ', file_path)

if __name__ == "__main__":
    #queries = ["example1", "example2", "example3"]
    performance()