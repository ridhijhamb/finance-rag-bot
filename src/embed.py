import os
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def get_embeddings():
    return OpenAIEmbeddings()
