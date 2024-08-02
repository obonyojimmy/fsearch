.PHONY:  dev install help start test benchmark search

dev:
	pip install -e .

install:
	pip install .

help:
	fsearch --help

start:
	fsearch start -c config.ini

test:
	pytest --fsearch-config /home/jimmy/Projects/Personal/fsearch/config.ini --cov=fsearch -v

benchmark:
	fsearch benchmark -r reports/benchmark.pdf -s samples/200k.txt -n 10

search:
	fsearch client -c config.ini '11;0;23;11;0;19;5;0;'
	fsearch client -c config.ini '11;0;23;11;0;19;5'
