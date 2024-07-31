.PHONY:  dev install help start test 

dev:
	pip install -e .

install:
	pip install .

help:
	fsearch --help

start:
	fsearch -c config.ini

test:
	pytest --fsearch-config /home/jimmy/Projects/Personal/fsearch/config.ini
