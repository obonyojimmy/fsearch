.PHONY:  dev install help start service stop test benchmark client

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

test:
	pytest --fsearch-config /home/jimmy/Projects/Personal/fsearch/config.ini --cov=fsearch -v

benchmark:
	fsearch benchmark -r reports/benchmark.pdf -s samples/200k.txt -n 10

client:
	python client.py -p 8080 -c .certs/server.crt -k .certs/server.key '11;0;23;11;0;19;5;0;'
	python client.py --host 0.0.0.0 -c .certs/server.crt -k .certs/server.key -p 8080 '11;0;23;11;0;19;5;0;'
	#client.py -h 0.0.0.0 -p 8080 '11;0;23;11;0;19;5'
