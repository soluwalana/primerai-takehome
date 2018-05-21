FROM ubuntu:16.04

WORKDIR /code

RUN apt-get update && apt-get install python3 netcat libpq-dev postgresql-client python3-setuptools python3-pip libffi-dev netcat apt-utils ca-certificates -y

ADD requirements.txt /code/
RUN pip3 install -r requirements.txt
RUN update-ca-certificates
CMD ["python3", "-m", "processor.service"]
