#!/bin/bash

apt-get update 

apt-get install -y wget git zip tar curl tree 
apt-get install -y python3.10 python3-pip

apt-get clean
apt-get autoclean

pip install -U chromadb
pip install -U discord-py-interactions
pip install -U langchain
pip install -U pyautogen
pip install -U openai
pip install -U tika