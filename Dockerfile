FROM lunamidori5/pixelarch:latest

COPY . /app
WORKDIR /app

RUN rm -f config.json

RUN ./setup.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]