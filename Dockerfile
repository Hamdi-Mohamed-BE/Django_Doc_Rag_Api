FROM python:3.11
LABEL MAINTAINER="Hamdi Mohamed BE <3"

# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# This keeps Python from buffering stdin/stdout
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

CMD ["sh","/scripts/server_run.sh"]