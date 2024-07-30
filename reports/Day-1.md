
**Daily Progress Report**: (Day 1)

**Date**: July 30, 2024

**Reporter**: Jimmycliff Obonyo

**Assignee**: Queen (Algorithmic Sciences)

**Hours Tracked**: 8.35 hours



### 1. **Summary of Activities**
   
   - **Project Planning**:
     - Read and understood the problem statement, key requirements, and constraints.
     - Created a project issue tracking board in a private Asana workspace.
     - Set up a private Toggl project for time tracking.

   - **Project Structure Setup**:
     - Initiated a command-line Python package project called `fsearch`.
     - Designed the package to expose a command-line entry point for launching the server with subcommands and options/arguments.
     - The only required command-line argument is `--config`, which specifies the path to the server configuration file.
     - Here is a tree diagram of the project:
      .
      ├── config.ini
      ├── fsearch
      │   ├── algorithms.py
      │   ├── config.py
      │   ├── __init__.py
      │   ├── __main__.py
      │   ├── server.py
      │   └── utils.py
      ├── LICENSE
      ├── README.md
      ├── requirements.txt
      ├── samples
      │   └── 200k.txt
      ├── server.crt
      ├── server.key
      ├── setup.py
      └── tests
          └── __init__.py

   - **Server Module Implementation**:
     - Implemented a `Server` class that reads configuration from a file to gather server settings.
     - The server opens a TCP socket with host and port options provided from the configuration object (default values are used if options are missing).
     - The server listens for connections, accepts connections in a loop, and starts a new thread to handle each client connection.
     - Each client connection is processed, a response is sent, and the connection is closed.

   - **Configuration Options Handling**:
     - Implemented a `config` module that reads the configuration file and transforms it into a `Config` dataclass object, providing default values for missing configuration options.

   - **SSL Security Implementation**:
     - Implemented configurable SSL termination in the server module.

   - **Regex File Search Algorithm Implementation**:
     - Implemented a simple regex pattern matching search algorithm.
     - Integrated the search functionality in the server's client request handling process.

### 2. **Understanding and Interpretation of New Tasks**

   - **Task**: Implement regex file search algorithm
     - **Understanding**: This task involves creating a function to perform regex pattern matching on the file contents read by the server. The function will take a search query as an argument and return `True` if the pattern is found, otherwise `False`.
     - **Plan**: 
       - Create a new module `algorithms.py` with a `regex_search` function.
       - Integrate this function into the server's client request handling.
     - **Estimated Duration**: 3 hours
     - **Expected Completion**: By the end of tomorrow

### 3. **Challenges**
   - The main challenge was determining the best template for the daily reporting email.

### 4. **Obstacles and Questions**
   - No current obstacles. All tasks are proceeding as planned.

### 5. **Proud Work Showcase**
   - **Server Module Code**:
     - **Screenshot**: ![Server Module Code](path/to/screenshot.png)
     - **Difficulty**: The main difficulty was ensuring the server correctly handles multiple client connections and integrates SSL.
     - **Thought Process**: Focused on creating a robust multi-threaded server that securely handles connections using SSL.

### 6. **AI Assistance**
   - **Issues and Solutions**:
     - **Issue**: Implementing a simple command-line Python package
       - **Solution**: [ChatGPT Link](https://chatgpt.com/share/f3e71ca6-7298-4cd1-8cad-3c1b9dcd337e)
       - **Implemented**: Followed the solution to set up the package structure.
     - **Issue**: Creating a config parser module
       - **Solution**: [ChatGPT Link](https://chatgpt.com/share/1f6daff3-6562-44bf-b4a6-8086cff99dc9)
       - **Implemented**: Used the provided code to handle configuration files.

   - **AI Assistance Documentation**:
     - **Document**:
       - **Section 1**: Brief description of the issue.
       - **Section 2**: Solution provided by AI.
       - **Section 3**: Implementation after consulting AI.
     - **Full Log**: Attached as a separate document.

### 7. **Plan for Tomorrow**
   - Implement tests for all modules.
   - Research and implement other search algorithms, such as binary search.
   - Implement the `reread_on_query` option.
   - Implement logging functionality.

### 8. **Pending Issues**
   - Need to test the initial implementation.

### 9. **Additional Notes**
   - Suggest improving communication with the backend team to avoid delays.

### 10. **Attachments**
   - Toggl time tracking report for Day 1.
   - Asana project plan tasks.
   - AI assistance documentation (TBD).

---

This version of the report includes the total hours tracked in the header and omits the detailed task tracking section.