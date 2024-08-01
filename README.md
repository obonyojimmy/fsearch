# fsearch

A highly performant and secure command-line server to search text files for strings.

## Features

- **Concurrent Connections**: Handles multiple connections simultaneously using multithreading.
- **Configurable**: Reads configuration settings from a text file with `key=value` structure similar to [INI](https://en.wikipedia.org/wiki/INI_file) file.
- **String Search**: Searches for a specific string in the configured server file.
- **Secure Communication**: SSL support for secure client-server communication.
- **Detailed Logging**: Logs search queries, execution times, and other relevant information.
- **Benchmarks and Reports**: Provides performance benchmarks for different file search algorithms.

## Installation

1. **Extract the Repository**:

```bash
cd fsearch
```
 
2. **Install the Package**:


## Limitations

- It only reads max of 250,000 lines of the data-file (linux path)
- The client connections are handled in multithreaded but in same process as the server process , this might overload a single processor , optimization is to handle client connection in multiprocess.
- max number of concurrent connections is set to 5, suggest improvement to make it be configurable.

## Usage

TBD

## Project Structure

TBD

## Benchmarks and Reporting

TBD

## Testing

TBD

## Code Quality

TBD

## Security

TBD

## Contributions

TBD

## License

TBD

## Contact

For any questions or suggestions, please contact Jimmycliff at cliffjimmy27@gmail.com
