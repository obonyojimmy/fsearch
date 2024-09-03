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

certs:
	fsearch certs -d ./.certs_2

test:
	pytest --fsearch-config config.ini --cov=fsearch -v
	#pytest tests/test_service.py --fsearch-config config.ini --cov=fsearch.server -s

benchmark:
	python benchmark.py -r reports/benchmark.pdf -s 1000 -i 2

client:
	python client.py -p 8080 '11;0;23;11;0;19;5;0;'
	#python client.py -p 8080 -c .certs/server.crt -k .certs/server.key '11;0;23;11;0;19;5;0;'
	#python client.py --host 0.0.0.0 -c .certs/server.crt -k .certs/server.key -p 8080 '11;0;23;11;0;19;5;0;'
