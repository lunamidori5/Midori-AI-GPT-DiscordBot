#!/bin/bash

yay -Syu --noconfirm python-pyfiglet python-virtualenv wget git zip tar curl tree python310

yay -Ycc --noconfirm

python3 -m venv ai

ai/bin/pip install -U chromadb
ai/bin/pip install -U discord-py-interactions
ai/bin/pip install -U langchain
ai/bin/pip install -U pyautogen
ai/bin/pip install -U openai
ai/bin/pip install -U tika