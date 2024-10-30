FROM lunamidori5/pixelarch:latest

COPY . /app
WORKDIR /app

RUN sudo rm -f config.json

RUN sudo chmod +x setup.sh && sudo chmod +x entrypoint.sh && ./setup.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]