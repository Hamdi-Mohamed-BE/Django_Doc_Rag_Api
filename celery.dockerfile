FROM python:3.11
LABEL MAINTAINER="Hamdi Mohamed BE <3"

ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get -y dist-upgrade
RUN apt install -y netcat-traditional
RUN apt install -y libgdal-dev


COPY ./requirements.txt /requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt
RUN pip3 install chromadb

RUN mkdir /app
WORKDIR /app
COPY ./app /app
COPY ./scripts /scripts
RUN mkdir /tmp/runtime-user
RUN chmod +x /scripts/celery_run.sh

CMD ["sh", "/scripts/celery_run.sh"]