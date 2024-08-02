"""This file provides the report html template used for search algorithms benchmarks in fsearch package."""
# fsearch/report.py

benchmark_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Benchmark Results</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 10px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 50px;
        }}
        .plot {{
            text-align: center;
            margin: 50px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Benchmarking Search Algorithms</h1>
        <p></p>
    </div>
    <div class="plot">
        <img src="data:image/png;base64,{plot_img}" alt="Benchmark Plot">
    </div>
</body>
</html>
"""

service_template ="""[Unit]
Description=Fsearch Command-Line Search Service
After=network.target

[Service]
Type=simple
ExecStart={exec_path} start --config {config_file} --port {port}
WorkingDirectory={working_dir}
Restart=on-failure

[Install]
WantedBy=default.target
"""