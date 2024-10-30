FROM lunamidori5/pixelarch:latest

COPY . /app
WORKDIR /app

RUN sudo rm -f config.json

RUN chmod +x setup.sh && chmod +x entrypoint.sh && ./setup.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]