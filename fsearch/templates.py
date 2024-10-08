"""
fsearch/templates.py

This module provides template literals for:

- bechmark reports
- linux service defination
"""

# benchmark a pdf template
benchmark_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Benchmark Results</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 5px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 50px;
        }}
        .plot {{
            text-align: center;
            margin: 20px 5px;
        }}
        .table {{
            margin: 10px;
        }}
        .speed_table {{
            margin-top: 20px;
            margin-bottom: 20px;
            margin-left: 5px;
            margin-right: 5px;
        }}
        .summary {{
            margin-bottom: 50px;
            margin-top: 10px;
        }}
        
    </style>
</head>
<body>
    <div class="header">
        <h1>Benchmarking Search Algorithms</h1>
    </div>
    <div class="summary">
        <h3>Summary</h3>
        <p> 
            In the world of text processing, efficient search algorithms are essential for applications ranging from simple file searches to complex data mining tasks. This article presents a benchmark report comparing the performance of five popular search algorithms: Regex Search, Native Search, Rabin-Karp Search, KMP Search, and Aho-Corasick Search. The performance of each algorithm was evaluated on files of different different sizes.
        </p>
    </div>
    <div class="table">
        <h4>Algorithms benchmark</h4>
        <pre>{table_str}</pre>
    </div>
    <div class="plot">
        <img src="data:image/png;base64,{plot_img}" alt="Benchmark Plot">
    </div>
    <div class="speed_table">
        <h4>Speed Test Benchmark</h4>
        <pre>{speed_report}</pre>
        <h5>Legend</h5>
        <p>The first collumn of each file is measure of time of when RE_READ_ON_QUERY == False, the second collumn is time measure when RE_READ_ON_QUERY == True</p>
    </div>
    <div>
        <h3>Conclusion:</h3>
        <p>
        The benchmark results highlight the importance of choosing the right algorithm based on the specific requirements and constraints of the application. For single pattern searches in text files, Regex Search is the clear winner due to its superior performance and efficiency. Native Search, while easy to implement, may not be suitable for larger datasets. Algorithms like Rabin-Karp, KMP, and Aho-Corasick, which are theoretically efficient, may not always offer practical performance benefits due to various overheads.
        </p>
        <p>
        When designing a search functionality, it is crucial to consider the nature of the search tasks, the size of the data, and the specific performance characteristics of each algorithm. This benchmark provides a foundational understanding to guide such decisions, ensuring optimal performance and efficiency in text search operations.
        </p>
    </div>
</body>
</html>
"""  # noqa: E501

## Linux service defination template
service_template = """[Unit]
Description=Fsearch Command-Line Search Service
After=network.target

[Service]
Type=simple
ExecStart={exec_path} start --config {config_file}
WorkingDirectory={working_dir}
Restart=on-failure

[Install]
WantedBy=default.target
"""
