FROM ubuntu:22.04

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . /app
WORKDIR /app

RUN rm -f config.json

RUN ./setup.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]