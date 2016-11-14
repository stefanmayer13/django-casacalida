FROM python:3.6-alpine

RUN useradd --system app && \
    mkdir /app && \
    chown app:app /app

ADD requirements.txt manage.py /app/
ADD casacalida /app/casacalida
ADD core /app/core

RUN pip install -r /app/requirements.txt

VOLUME ["/app"]
USER app
WORKDIR /app
ENV PYTHONUNBUFFERED 1
