.PHONY:  dev install test 

dev:
	pip install -e .

install:
	pip install .

test:
	pytest
