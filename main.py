
import os
import sys
import time
import json
import random
import asyncio
import chromadb
import datetime
import interactions

from tika import parser
from openai import AsyncOpenAI
from chromadb.utils import embedding_functions
from interactions import Client, Intents, listen
from langchain.text_splitter import RecursiveCharacterTextSplitter

bot = Client(intents=Intents.DEFAULT) ##Discord Bot
## This sets up the discord bot using default intents

sentence_transformer_ef = embedding_functions.DefaultEmbeddingFunction()
## Enbedding model running inside of the bot...

chroma_client = chromadb.Client()
chroma_collection_name = "maindb"
collection = chroma_client.get_or_create_collection(name=chroma_collection_name, embedding_function=sentence_transformer_ef)
## This makes a folder that will save the vector to disk after being upsreted on boot, 
## the vectors are DESTORED on shutdown, but the embeds are saved

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1096,
    chunk_overlap=0,
    length_function=len,
)
## Token slpiter makes the vector store work

print(f"Imports done")

if os.path.exists("config.json"):
    with open("config.json") as jsonfile:
        config = json.load(jsonfile)
else:
    sys.exit("'config.json' not found! Please add it and try again.")

system_prompt = config["systemprompt"]

hotword = str(config["hotword"])

discord_token = config["discordtoken"]

openai_base_url = config["openaiurl"]
openai_token = config["openaitoken"]

client_openai = AsyncOpenAI(base_url=openai_base_url, api_key=openai_token, timeout=6000)

def upsert_docs():
    folder_path = 'data'
    files = os.listdir(folder_path)

    for file in files:
        file_path = os.path.join(folder_path, file)

        if ".pdf" in file_path:
            raw = parser.from_file(file_path)
            text = str(raw['content'])

        with open(file_path, 'r', encoding='utf8', errors='ignore') as f:
            text = f.read()

        items_to_add = text_splitter.split_text(str(text))
        current_id = time.time()

        documents = []
        ids = []

        for content_str in items_to_add:
            documents.append(content_str)
            ids.append(str(current_id))
            current_id = current_id + 1
            print(f"Upserting {content_str} id of {current_id}")
            collection.upsert(documents=documents, ids=ids)

@listen()
async def on_ready():
    print("Ready")
    print(f"This bot is owned by {bot.owner}")


@listen()
async def on_message_create(event):

    temp_message = str(event.message.content)
    
    if "!exit" in temp_message:
        await event.message.channel.send("Rebooting, Please wait!")
        sys.exit("Rebooting")

    if event.message.author == bot.user or event.message.author.bot:
        return
    
    chit_chat = random.randint(8, 400)

    if chit_chat > 350:
        can_reply = True
    else:
        can_reply = True
    
    if hotword.lower() in temp_message.lower():
        can_reply = True

    if "<@1233587882317320252>" in temp_message:
        can_reply = True
    
    if can_reply != True:
        return None
    
    session_inside = []
    
    if os.path.exists("memory.json"):
        with open('memory.json', 'r') as jsonfile:
            session_inside = json.load(jsonfile)
    
    results = collection.query(query_texts=[str(temp_message)], n_results=4)
    cleaned_similarity_results4 = results['documents']
    
    print(f"Message received: {temp_message} vector store returned {cleaned_similarity_results4}")

    current_datetime = datetime.datetime.now()
    current_date_str = current_datetime.strftime('%Y-%m-%d')
    current_time_str = current_datetime.strftime('%I:%M:%S %p')

    message_gpt = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'system', 'content': f'The date is {current_date_str} / The time is `{current_time_str}`'},
                {'role': 'system', 'content': f'The file that we are reviewing returned `{cleaned_similarity_results4}`'},
                *session_inside,
                {'role': 'user', 'content': str(temp_message)}
            ]

    messages = [{"role": msg["role"], "content": msg["content"]} for msg in message_gpt]
    
    message_to_user = await event.message.channel.send("Starting Message one moment...")
    
    while True:
        try:

            response = await client_openai.chat.completions.create(model='gpt-14b-carly', temperature=1.8, stream=True, messages=messages)

            #reply_content = response.choices[0].message.content
            new_item = []
            reply_content = ""

            async for chunk in response:
                if str(chunk).strip() == "":
                    print("Blank Message Sent - Chunk")
                else:
                    reply_content = reply_content + chunk.choices[0].delta.content
                    new_item.append(chunk.choices[0].delta.content)

                    if len(new_item) > 55:
                        await message_to_user.edit(content=str(reply_content))
                        print(reply_content)
                        new_item = []
            break
        except Exception as e:
            print("retrying")

    await message_to_user.edit(content=str(reply_content))

    print(reply_content)

    session_inside.append({"role": "unknown", "content": f"The user says {str(temp_message)}"})
    session_inside.append({"role": "unknown", "content": f"The AI replyed {reply_content}"})

    with open('memory.json', 'w') as jsonfile:
        json.dump(session_inside, jsonfile)

upsert_docs()

if os.path.exists("memory.json"):
    os.remove('memory.json')

bot.start(discord_token)