"""This file provides the report html template used for search algorithms benchmarks in fsearch package."""  # noqa: E501
# fsearch/report.py

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
        <pre>{table_str}</pre>
    </div>
    <div class="plot">
        <img src="data:image/png;base64,{plot_img}" alt="Benchmark Plot">
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
"""

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
