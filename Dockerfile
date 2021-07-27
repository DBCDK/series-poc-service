FROM docker.dbc.dk/dbc-python3
MAINTAINER Søren Mollerup <shm@dbc.dk>


ENV PORT=5000

RUN apt-get update && \
	apt-get install -y --no-install-recommends wget gcc g++ unzip && \
	pip install -U pip && \
	pip install json5 && \
	pip install series-poc && \
	apt-get remove -y wget gcc g++ unzip && \
	apt-get autoremove -y

RUN mkdir data-files
ADD ./data-files data-files/

CMD ["series-service", "--verbose", "--port", "5000"]

LABEL "PORT"="Port to expose service on"
