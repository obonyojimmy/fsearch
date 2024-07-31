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
            margin: 40px;
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