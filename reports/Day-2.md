**Daily Progress Report**: (Day 2)

**Date**: July 31, 2024

**Reporter**: Jimmycliff Obonyo

**Assignee**: Queen (Algorithmic Sciences)

**Hours Tracked**: 8.10 hours


### 1. **Summary of Activities**
   
   - **Research String Search Implementations**:
     - Investigated various string search algorithms to determine the most efficient methods for the project's requirements.

   - **Unit Tests Implementation**:
     - Developed unit tests for the package modules to ensure robustness and reliability.

   - **Additional String Search Algorithms**:
     - Implemented the following string search algorithms:
       - Rabin-Karp
       - Knuth-Morris-Pratt (KMP)
       - Naive Search
       - Aho-Corasick

   - **`reread_on_query` Server Option**:
     - Implemented the `reread_on_query` option in the server to dynamically reread files upon each query.

   - **Debug and Fix Search Algorithms**:
     - Debugged and fixed the search algorithms to ensure they match the full string in a line.

   - **Configurable SSL Implementation**:
     - Enhanced SSL configuration by creating self-signed SSL certificates if missing or not found when the SSL config option is set to true.

   - **Support for Relative Paths**:
     - Added support for relative paths in the config file and `linuxpath` config option to improve flexibility.

   - **Dynamic Config Path Resolution**:
     - Fixed dynamic config path resolution for `pytest_addoption` in `conftest.py` using the `--fsearch-config` argument.

### 2. **Challenges**
   - The main challenge was debugging the string search algorithms to ensure they correctly match full strings within lines.
   - Passing dynamic config file when running the tests. 

### 3. **Proud Work Showcase**
   - **Additional String Search Algorithms Code**:
     - **Screenshot**: Attached in email.
     - **Difficulty**: Ensuring each algorithm performs optimally and handles various edge cases such as full match in a line.
     - **Thought Process**: Focused on implementing robust algorithms that can handle different types of string searches efficiently.

### 4. **AI Assistance**
   - **Issue**: Research string search algorithms
     **AI Log**: [ChatGPT Log](https://chatgpt.com/share/d1451439-7034-4d2c-bae1-11b824d2a4d0)
     **Solution**: Conducted thorough research on various string search algorithms and selected the most suitable ones for implementation.

   - **Issue**: Autogenerate unit test cases for current codebase module files
     **AI Log**: [ChatGPT Log](https://chatgpt.com/share/97dd36d9-f71e-49f4-bfc8-dedcd416dc28)
     **Solution**: Efficiently scaffolded unit test cases for the package modules.


### 5. **Plan for Tomorrow**
   - Implement benchmarks for different string search algorithms.
   - Create coverage reports.
   - Implement the client.
   - Package the project, including installation to support running the server as a daemon.
   - Implement `mmap` for efficient large file searching.

### 6. **Pending Issues**
   - N/A

### 7. **Attachments**
   - Toggl time tracking report for Day 2.
   - String search algorithms code screenshot.
   - AI assistance documentation.
