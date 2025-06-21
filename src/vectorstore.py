import os
import json
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from pathlib import Path

SAVE_DIR = Path("data/edgar_sec_filings")
INDEX_DIR = "faiss_index_all"

def load_docs_from_txt():
    docs = []
    for filepath in SAVE_DIR.glob("*.txt"):
        with open(filepath, "r") as f:
            content = f.read()
        # Infer company name from filename (e.g., apple_chunk_0.txt)
        company_name = filepath.stem.split("_chunk_")[0].capitalize()
        docs.append(Document(page_content=content, metadata={"company": company_name}))
    return docs

def build_and_save_faiss_index():
    docs = load_docs_from_txt()
    print(f"Loaded {len(docs)} document chunks.")
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(INDEX_DIR)
    print(f"FAISS index saved to '{INDEX_DIR}'")

if __name__ == "__main__":
    build_and_save_faiss_index()
