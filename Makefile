.PHONY:  dev install help start service stop test benchmark client logs samples perf

dev:
	pip install -e .

install:
	pip install .

help:
	fsearch --help

start:
	fsearch start -c config.ini

service:
	fsearch.service -c config.ini

stop:
	systemctl --user stop fsearch.service

status:
	systemctl --user status fsearch.service

logs:
	journalctl --user -u fsearch.service -f

samples:
	fsearch samples -s 10

test:
	pytest --fsearch-config config.ini --cov=fsearch -v
	#pytest tests/test_server.py --fsearch-config config.ini --cov=fsearch.server -s

perf:
	#pytest --fsearch-config config.ini --cov=fsearch -v
	python tests/test_performance.py

benchmark:
	#fsearch benchmark -r reports/benchmark.pdf -s samples/200k.txt -n 1
	fsearch benchmark -r reports/benchmark.pdf -d samples/ -n 1

client:
	python client.py -p 8080 -c .certs/server.crt -k .certs/server.key '11;0;23;11;0;19;5;0;'
	python client.py --host 0.0.0.0 -c .certs/server.crt -k .certs/server.key -p 8080 '11;0;23;11;0;19;5;0;'
	#client.py -h 0.0.0.0 -p 8080 '11;0;23;11;0;19;5'
