@echo off

title AI LLM Bot
echo Starting AI Docker install, please wait

mkdir data

docker compose build --no-cache 
docker compose up -d