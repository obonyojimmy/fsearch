# fsearch

A highly performant and secure command-line server to search text files for strings.

## Features

- **Concurrent Connections**: Handles multiple connections simultaneously using multithreading.
- **Configurable**: Reads configuration settings from [INI](https://en.wikipedia.org/wiki/INI_file) files.
- **String Search**: Searches for full-line strings in the configured server file database.
- **Secure Communication**: SSL support for secure client-server communication.
- **Benchmarks and Reports**: Provides performance benchmarks for different file search algorithms.

## Installation

```bash
unzip fsearch.zip
pip install .
```

## Usage

### Starting the Server

1. **Start as a service:**

```bash
usage: fsearch.service [-h] -c CONFIG [-p PORT]

required arguments:
  -c CONFIG, --config CONFIG  Path to the server configuration file

optional arguments:
  -h, --help                  Show this help message and exit
  -p PORT, --port PORT        The server port
```

Example: `fsearch.service -c config.ini`

Notes:

- This will run the fsearch server as a linux server in current user space.
- To check the service status , run `systemctl --user status fsearch.service`
- To stop the service , run `systemctl --user stop fsearch.service`
- To view the service logs , run `systemctl --user stop fsearch.service`

2. **Manually start the server:**

```bash
usage: fsearch start [-h] -c CONFIG

Run fsearch server.

required arguments:
  -c CONFIG, --config CONFIG  Path to the server configuration file

optional arguments:
  -h, --help                  Show this help message and exit
  -p PORT, --port PORT        The server port
```

Example: `fsearch start -c config.ini`

Notes:

- This will run the server in the current terminal , to stop it press `[CTRL] + [C]` buttons.

### Configuration File Specification

Use an `.ini` configuration file formatted as follows:

```ini
[DEFAULT]
linuxpath=samples/200k.txt
reread_on_query=False
ssl=False
certfile=.certs/server.crt
keyfile=.certs/server.key
```

**Required Configurations:**

- `linuxpath`: Path to the server database to be searched.

**Optional Configurations:**

- `reread_on_query`: Determine if the database should be re-read on every request. (`True` or `False`)
- `ssl`: Enable SSL for the server. If set to `True` and no certificates are provided, the server will autogenerate self-signed certificates.
- `certfile`: Path to the SSL certificate. If missing, the server will autogenerate a certificate at `.certs/server.crt`.
- `keyfile`: Path to the SSL key. If missing, the server will autogenerate a key at `.certs/server.key`.

### Running Client Requests

You can query the server from any location using `client.py`. Please feel free to copy it to a convenient location.

```bash
usage: client.py [-h] [--host HOST] -p PORT [-c CERT] [-k KEY] [query]

fsearch client

positional arguments:
  query                 String to search for

required arguments:
  -p PORT, --port PORT  The server port

optional arguments:
  -h, --help            Show this help message and exit
  --host HOST           The server host IP (defaults to 0.0.0.0)
  -c CERT, --cert CERT  Optional SSL server certificate file path
  -k KEY, --key KEY     Optional certificate key file path
```

**Note:**
1. If you start the server with SSL, you must provide both the certificate and key to authenticate with the server.

Example: `python client.py -p 8080 -c .certs/server.crt -k .certs/server.key '11;0;23;11;0;19;5;0;'`

2. We have included a utility command to generate certs, run `fsearch certs -d <dir>` , this will generate **server.crt** and **server.key** files in the `<dir>` folder , which can be passed to respective SSL args when running server or client.

## Testing

1. Ensure you have installed the required test dependencies. Run `pip install fsearch[test]` or `pip install pytest pytest-cov` to install them.
2. Run `pytest --fsearch-config [CONFIG_FILE] --cov=fsearch -v`, where `[CONFIG_FILE]` is the server configuration file described earlier. 

Example: `pytest --fsearch-config config.ini --cov=fsearch -v`

## Benchmarks and Reports

`fsearch` has five implemented search algorithms that have been extensively benchmarked. The best-performing algorithm, **regex**, is used in the server search. Please see the [benchmark report](reports/benchmark.pdf).

Algorithms Benchmarks:

```plaintext
Algorithm           95326          190651         Average        
-----------------------------------------------------------------
Regex Search        1.148966       0.988754       1.068860 (ms)  
Native Search       1.267466       1.029631       1.148548 (ms)  
Rabin-Karp Search   20.985291      17.455178      19.220235 (ms) 
Aho-Corasick Search 33.802388      31.473223      32.637805 (ms) 
KMP Search          48.840177      46.024340      47.432259 (ms) 
-----------------------------------------------------------------
```

Performance Benchmarks:

```plaintext
Requests | 1000-kb    | 2000-kb   
-------- | ---------- | ----------
10       | 6.7 | 12.2 | 6.1 | 15.6
20       | 6.3 | 14.4 | 6.5 | 13.4
30       | 6.9 | 14.4 | 6.1 | 12.9
40       | 2.1 | 11.1 | 6.9 | 12.5
50       | 5.5 | 11.3 | 7.5 | 12.6
60       | 8.9 | 14.9 | 6.0 | 6.8 
70       | 6.9 | 12.0 | 5.1 | 13.8
80       | 7.5 | 13.4 | 7.8 | 9.5 
90       | 6.9 | 8.8  | 6.5 | 13.0
```

*Legend*

- The first collumn of each file is measure of time of when RE_READ_ON_QUERY == False, the second collumn is time measure when RE_READ_ON_QUERY == True
To run the search algorithms benchmarks:

1. Please ensure that required benchmark utility libraries  **_(matplotlib weasyprint)_** are installed , if not please install them by running:
`pip install matplotlib weasyprint`

2. Run benchmark.py  to run both performance and algorithms comparisons benchmarks:

```bash
usage: benchmark.py [-h] -r REPORT_PATH [-s MIN_SIZE] [-i ITERATIONS]

Measures server performance and algorithm comparison benchmarks

optional arguments:
  -h, --help            show this help message and exit
  -r REPORT_PATH, --report_path REPORT_PATH
                        Path to save the benchmark report
  -s MIN_SIZE, --min_size MIN_SIZE
                        The minimum sample size in kb. Defaults to 10000 ie 10mb (default: 1).
  -i ITERATIONS, --iterations ITERATIONS
                        The number of iterations to run the performance benchmark loop. Defaults to 2 loops.
```

Example: `fsearch benchmark -r reports/benchmark.pdf -d samples/ -n 1` will run benchmarks using files in the `samples/` directory as the sampling samples, and create a pdf report at path `reports/benchmark.pdf`

## Limitations

- The 1st client request will take ~0.40ms longer , proceeding request will be much faster ~0.5ms if REREAD_ON_QUERY false and ~10ms if REREAD_ON_QUERY is True.
- It reads a maximum of 250,000 lines of the database file (`linuxpath`).
- Client connections are handled in multithreaded mode but in the same process as the server, which might overload a single processor. Optimization can be achieved by handling client connections in multiple processes.
- The maximum number of concurrent connections is set to 5. It is suggested to make this configurable.

## Code Quality

```plaintext
---------- coverage: platform linux, python 3.9.19-final-0 -----------
Name                    Stmts   Miss  Cover
-------------------------------------------
fsearch/__init__.py         2      0   100%
fsearch/__main__.py        76      6    92%
fsearch/algorithms.py     115      3    97%
fsearch/config.py          25      2    92%
fsearch/server.py          98     20    80%
fsearch/service.py         31      2    94%
fsearch/templates.py        2      0   100%
fsearch/utils.py          168     21    88%
-------------------------------------------
TOTAL                     517     54    90%


============================ 59 passed in 10.44s ========================
```

## License

`fsearch` is licensed under the terms of the MIT license.

## Contact

For any questions or suggestions, please contact Jimmycliff at [cliffjimmy27@gmail.com](mailto:cliffjimmy27@gmail.com).